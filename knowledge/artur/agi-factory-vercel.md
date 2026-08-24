# Деплой проектов через Vercel (база знаний Завода Джарвисов)

Источник: статья kb.mcdenil.com, прислана Артуром 24.08.2026.

## Суть
Vercel превращает папку с файлами в живой сайт (HTTPS, CDN, домен) за 30 сек. Одна команда vercel deploy, без nginx/SSL/DNS.

## Подключение
vercel.com → Settings → Tokens → новый токен → /settings → Переменные → VERCEL_TOKEN. Опционально VERCEL_PROJECT_ID (привязка к проекту).

## Деплой
«Задеплой папку ~/projects/my-website на Vercel» → агент покажет план и спросит подтверждение (RED-операция) → vercel --token $VERCEL_TOKEN deploy → ссылка на сайт.

## Что можно деплоить
- Статический HTML (лендинг, визитка) — index.html.
- React / Next.js — package.json с build-скриптом.
- Vanilla JS (калькулятор, квиз).
Агент сам определяет тип и настраивает сборку.

## RED-операции (требуют «да»)
vercel deploy, vercel rm (удалить проект), vercel env rm (удалить переменную).

## Продакшн / домен
vercel --prod → основной домен. «Привяжи домен example.com» → агент даст DNS-записи.

## Применение к нашему заводу
У меня Vercel уже настроен (сегодня): токен ~/.openclaw-neuro/.vercel_token (username djmrfobs-7888), скилл deploy-to-vercel, команда vercel deploy --token. Правило «деплой с подтверждением» = мой P1. Всё покрыто.
