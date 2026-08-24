#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Site_Kiselevy_Creo_bot — приём проектов для сайта Kiselevy_creo.
Логика:
  Пользователь присылает фото + описание. Бот:
   1) определяет категорию по ключевым словам в описании
   2) скачивает фото в assets/projects/
   3) добавляет запись в projects.json
   4) подтверждает в Telegram
Токен читается из окружения SITE_PROJECTS_BOT_TOKEN.
"""
import os, json, io, time, re, hashlib
import urllib.request
from pathlib import Path

BASE = Path(__file__).resolve().parent

# Безопасная загрузка токена: сначала env, затем зашифрованный vault
TOKEN = os.environ.get("SITE_PROJECTS_BOT_TOKEN")
if not TOKEN:
    try:
        import sys
        sys.path.insert(0, "/root/workspace/fobs_projects/security")
        from vault import get_secret
        TOKEN = get_secret("SITE_PROJECTS_BOT_TOKEN") or ""
    except Exception as e:
        print("Vault недоступен:", e)
        TOKEN = ""
API = f"https://api.telegram.org/bot{TOKEN}"
PROJECTS_JSON = BASE / "projects.json"
ASSETS_DIR = BASE / "site_deploy" / "assets" / "projects"
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

AUTHORIZED = {199790247}  # только владелец может добавлять проекты

# Категории сайта и ключевые слова (порядок важен: более конкретные категории первыми,
# чтобы «обработку заявок» не цеплялось как чат-бот по подстроке «бот»)
CATEGORY_KEYWORDS = [
    ("automation",["автоматиз", "crm", "интеграц", "воронк", "n8n", "zapier", "make", "рутин", "email", "рассылк", "цепочк", "обработк", "заявк"]),
    ("chatbot",   ["чат-бот", "чатбот", "чат-бот", "telegram-бот", "whatsapp", "телеграм", "поддержк", "менеджер", "клиент", "бот", "бот"]),
    ("ai",        ["ai", "ии", "gpt", "нейросет", "ассистент", "интеллект", "llm", "подбор", "генерац"]),
    ("production",["продюсир", "съём", "съем", "монтаж", "ролик", "видео", "кейс", "рекламн", "клип", "саундтрек", "музык", "трек", "эмбиент"]),
    ("marketing", ["маркетинг", "продвиж", "воронки продаж", "реклам", "performance", "таргет", "конверси", "заявок", "продаж", "запуск продукта"]),
]
DEFAULT_CATEGORY = "other"
CATEGORY_LABEL = {
    "chatbot": "Чат-бот", "automation": "Автоматизация", "ai": "AI-система",
    "production": "Продюсирование", "marketing": "Маркетинг", "other": "Другое"
}

def api(method, params=None, files=None, timeout=30):
    if files:
        # multipart
        boundary = "----bot" + hashlib.md5(str(time.time()).encode()).hexdigest()
        parts = []
        for k, v in (params or {}).items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"\r\n\r\n{v}\r\n".encode())
        for k, (fn, data, ctype) in files.items():
            parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"{k}\"; filename=\"{fn}\"\r\nContent-Type: {ctype}\r\n\r\n".encode() + data + b"\r\n")
        parts.append(f"--{boundary}--\r\n".encode())
        body = b"".join(parts)
        req = urllib.request.Request(f"{API}/{method}", data=body, method="POST")
        req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    else:
        url = f"{API}/{method}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def get_updates(offset):
    try:
        return api("getUpdates", {"offset": offset, "timeout": 25})
    except Exception as e:
        print("poll error:", e, flush=True)
        return {"ok": False, "result": []}

def send_msg(chat_id, text, reply_markup=None):
    try:
        p = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        if reply_markup:
            p["reply_markup"] = json.dumps(reply_markup)
        return api("sendMessage", p)
    except Exception as e:
        print("send error:", e)

def load_projects():
    try:
        return json.loads(PROJECTS_JSON.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_projects(projects):
    data = json.dumps(projects, ensure_ascii=False, indent=2)
    PROJECTS_JSON.write_text(data, encoding="utf-8")
    # дублируем в site_deploy/ где развёрнут боевой сайт (HTML читает projects.json рядом с index.html)
    try:
        (BASE / "site_deploy" / "projects.json").write_text(data, encoding="utf-8")
    except Exception as e:
        print("warn: не смог обновить site_deploy/projects.json:", e)

def detect_category(text):
    t = text.lower()
    for cat, kws in CATEGORY_KEYWORDS:
        for kw in kws:
            if kw in t:
                return cat
    return DEFAULT_CATEGORY

def slugify(name):
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return (s or "project")[:40]

def main():
    print(f"Бот проектов запущен. @Site_Kiselevy_Creo_bot")
    offset = 0
    pending = {}  # chat_id -> {photo_path, file_ext}
    while True:
        up = get_updates(offset)
        for u in up.get("result", []):
            offset = u["update_id"] + 1
            msg = u.get("message") or u.get("callback_query", {}).get("message") or {}
            chat = msg.get("chat", {})
            chat_id = chat.get("id")
            if chat_id not in AUTHORIZED:
                if msg.get("text") or msg.get("photo"):
                    send_msg(chat_id, "Извините, этот бот предназначен для владельца.")
                continue
            # ---- фОТО ----
            if msg.get("photo"):
                largest = msg["photo"][-1]
                file_id = largest["file_id"]
                try:
                    f = api("getFile", {"file_id": file_id})
                    file_path = f["result"]["file_path"]
                    ext = os.path.splitext(file_path)[1] or ".jpg"
                    data = urllib.request.urlopen(f"https://api.telegram.org/file/bot{TOKEN}/{file_path}", timeout=30).read()
                    temp = ASSETS_DIR / ("_pending" + ext)
                    temp.write_bytes(data)
                    pending[chat_id] = {"path": temp, "ext": ext}
                    send_msg(chat_id, "📸 Фото получил! Теперь отправь <b>описание проекта</b> (можно одной строкой или абзацем). Отдельно укажи тему — я сам определю категорию.")
                except Exception as e:
                    send_msg(chat_id, "Не смог скачать фото. Попробуй ещё раз.")
                    print("photo err:", e)
                continue
            # ---- ТЕКСТ ----
            text = msg.get("text")
            if not text:
                continue
            if text == "/start":
                send_msg(chat_id, "Привет! Я бот проектов Kiselevy_creo 🌟\n\nПришли мне <b>фото проекта</b>, а затем <b>описание</b> — я определю категорию и добавлю проект на сайт.")
                continue
            if text == "/help":
                send_msg(chat_id, "Как добавить проект:\n1) Пришли фото\n2) Пришли описание (бо́т сам определит категорию)\n3) Готово!\n\nКоманда /status — сколько проектов сейчас.")
                continue
            if text == "/status":
                send_msg(chat_id, f"Сейчас на сайте {len(load_projects())} проектов.")
                continue
            # Если есть фото в ожидании — добавляем проект
            if chat_id in pending:
                pp = pending.pop(chat_id)
                cat = detect_category(text)
                # сохраняем фото с осмысленным именем
                name = text.split("\n")[0].strip()[:50] or "Проект"
                fname = f"{slugify(name)}_{int(time.time())}{pp['ext']}"
                final = ASSETS_DIR / fname
                (pp["path"]).rename(final)
                projects = load_projects()
                projects.append({
                    "title": name,
                    "category": cat,
                    "description": text.strip(),
                    "image": f"assets/projects/{fname}",
                    "result": "",
                    "audio": []
                })
                save_projects(projects)
                send_msg(chat_id,
                    f"✅ Проект добавлен!\n\n<b>{name}</b>\nКатегория: {CATEGORY_LABEL.get(cat, cat)}\n\nФото сохранено в assets/projects/{fname}.\nКогда зальёшь projects.json и фото на сайт — проект появится в портфолио.",
                    reply_markup={"inline_keyboard": [[{"text": "📄 Скачать projects.json", "callback_data": "get_json"}]]})
            else:
                send_msg(chat_id, "Сначала пришли <b>фото</b>, потом описание (или просто фото без текста — добавлю как «Проект»).")
            # callback — выдать JSON
            if u.get("callback_query"):
                cb = u["callback_query"]
                cid = cb.get("message", {}).get("chat", {}).get("id")
                if cid in AUTHORIZED and cb.get("data") == "get_json":
                    send_msg(cid, "Файл projects.json лежит на сервере в projects/kiselevy_creo_site/site_deploy/projects.json — загрузи его на сайт вместе с папкой assets/projects/.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nОстановлен.")
