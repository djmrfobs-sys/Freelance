// =====================================================================
// KISELEVY_CREO — serverless-функция отправки заявок в Telegram (Vercel)
// ---------------------------------------------------------------
// ТЗ #18: Telegram-токен НЕ хранится в клиентском HTML.
// Здесь токен и chat_id берутся из переменных окружения:
//   TELEGRAM_BOT_TOKEN
//   TELEGRAM_CHAT_ID
// Переменные задаются в Vercel (Settings -> Environment Variables)
// или в локальном файле .env (см. .env.example).
//
// Клиент отправляет сюда POST /api/send-lead с JSON-данными заявки.
// Функция валидирует данные, экранирует текст и отправляет в Telegram.
// Токен и служебные данные наружу НЕ возвращаются.
// =====================================================================

// Максимальная длина каждого поля заявки (защита от флуда/мусора)
const MAX_FIELD_LEN = 160;
// Максимум полей в одной заявке
const MAX_FIELDS = 20;
// Кол-во секунд блокировки одного IP (очень простая защита от спама:
// на бесплатной Vercel без БД храним в памяти процесса — достаточно для базы)
const RATE_SECONDS = 10;

// Простой in-memory rate limiter (не для прод-масштаба, но лучше, чем ничего).
// ОСТОРОЖНО: Vercel serverless может иметь несколько инстансов — это защита
// на уровне инстанса. Для серьёзного анти-спама используйте KV/BLOB хранилище.
const hits = new Map();

function sanitize(value) {
  if (value == null) return '';
  const s = String(value).trim().slice(0, MAX_FIELD_LEN);
  // Защита от Telegram-инъекций и лишних переносов в подписи
  return s
    .replace(/\r?\n/g, ' ')
    .replace(/<\/?[a-z][^>]*>/gi, ''); // убираем сырые HTML-теги
}

function buildMessage(payload) {
  const lines = ['🧾 *Новая заявка с сайта KISELEVY_CREO*'];
  let n = 0;
  for (const [k, v] of Object.entries(payload)) {
    if (n++ >= MAX_FIELDS) break;
    const key = sanitize(k) || 'поле';
    const value = sanitize(v);
    if (!value) continue;
    lines.push(`• *${key}*: ${value}`);
  }
  return lines.join('\n');
}

export default async function handler(req, res) {
  // Только POST
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'method not allowed' });
  }

  // Грубая защита от спама по IP
  const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim() || 'unknown';
  const now = Date.now();
  const last = hits.get(ip) || 0;
  if (now - last < RATE_SECONDS * 1000) {
    return res.status(429).json({ ok: false, error: 'too many requests' });
  }
  hits.set(ip, now);

  // Проверка структуры тела
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chatId) {
    console.error('[send-lead] env TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID не заданы');
    return res.status(500).json({ ok: false, error: 'server not configured' });
  }

  let payload;
  try {
    payload = typeof req.body === 'string' ? JSON.parse(req.body) : req.body;
  } catch (e) {
    return res.status(400).json({ ok: false, error: 'invalid json' });
  }
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) {
    return res.status(400).json({ ok: false, error: 'invalid payload' });
  }

  const text = buildMessage(payload);
  if (!text.trim() || text.split('\n').every((l) => !l.includes(':'))) {
    return res.status(400).json({ ok: false, error: 'empty lead' });
  }

  try {
    // Disable web page preview; parse_mode=Markdown, но нас безопаснее оставить HTML-теги вырезанными
    const tgRes = await fetch(
      `https://api.telegram.org/bot${token}/sendMessage`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          chat_id: chatId,
          text,
          disable_web_page_preview: true,
        }),
      }
    );
    const tgJson = await tgRes.json();
    if (!tgRes.ok || !tgJson.ok) {
      console.error('[send-lead] Telegram API error:', tgJson?.description || tgRes.status);
      return res.status(502).json({ ok: false, error: 'telegram send failed' });
    }
    // НЕ логируем персональные данные полностью — только факт успеха
    return res.status(200).json({ ok: true, delivered: 'telegram' });
  } catch (e) {
    console.error('[send-lead] fetch error:', e.message);
    return res.status(502).json({ ok: false, error: 'telegram unavailable' });
  }
}
