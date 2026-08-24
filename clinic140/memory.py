# Клиника 140 - модуль памяти кабинетов
# Каждый кабинет (врач) - отдельный файл .json
# Автосохранение после каждого сообщения, восстановление после перезапуска,
# резервная копия раз в сутки.

import os
import json
import shutil
import time
from datetime import datetime, timedelta
from config import CABINETS_DIR, BACKUP_DIR

os.makedirs(CABINETS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)


def _cabinet_path(chat_id, doctor_id):
    """Путь к файлу истории кабинета."""
    return os.path.join(CABINETS_DIR, f"{chat_id}_{doctor_id}.json")


def _safe_read(path):
    """Прочитать JSON безопасно (восстановление после битого файла)."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def init_cabinet(chat_id, doctor_id):
    """Создать/загрузить кабинет врача для пользователя."""
    path = _cabinet_path(chat_id, doctor_id)
    data = _safe_read(path)
    if data is None:
        data = {
            "chat_id": chat_id,
            "doctor_id": doctor_id,
            "created": datetime.now().isoformat(),
            "messages": [],          # [{"role","content","ts"}]
            "context": {},           # доп. состояние кабинета
            "last_question": None,   # последний открытый вопрос Кети
        }
        save_cabinet(chat_id, doctor_id, data)
    return data


def add_message(chat_id, doctor_id, role, content, extra=None):
    """Добавить сообщение в кабинет и сразу сохранить (автосохранение)."""
    data = init_cabinet(chat_id, doctor_id)
    msg = {
        "role": role,
        "content": content,
        "ts": datetime.now().isoformat(),
    }
    if extra:
        msg["extra"] = extra
    data["messages"].append(msg)
    # Ограничим рост: храним последние 500 сообщений кабинета
    if len(data["messages"]) > 500:
        data["messages"] = data["messages"][-500:]
    save_cabinet(chat_id, doctor_id, data)
    return data


def get_last_messages(chat_id, doctor_id, limit=20):
    """Последние N сообщений кабинета для контекста AI."""
    data = init_cabinet(chat_id, doctor_id)
    msgs = data.get("messages", [])
    return msgs[-limit:] if len(msgs) > limit else msgs


def save_cabinet(chat_id, doctor_id, data):
    """Сохранить кабинет в файл."""
    path = _cabinet_path(chat_id, doctor_id)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def reset_cabinet(chat_id, doctor_id):
    """Очистить историю конкретного кабинета."""
    path = _cabinet_path(chat_id, doctor_id)
    new_data = {
        "chat_id": chat_id,
        "doctor_id": doctor_id,
        "created": datetime.now().isoformat(),
        "messages": [],
        "context": {},
        "last_question": None,
    }
    save_cabinet(chat_id, doctor_id, new_data)
    return new_data


def all_cabinets(chat_id):
    """Все кабинеты пользователя (список doctor_id с метаданными)."""
    result = []
    prefix = f"{chat_id}_"
    for fn in os.listdir(CABINETS_DIR):
        if fn.startswith(prefix) and fn.endswith(".json"):
            path = os.path.join(CABINETS_DIR, fn)
            data = _safe_read(path)
            if data:
                result.append({
                    "doctor_id": data.get("doctor_id"),
                    "messages": len(data.get("messages", [])),
                    "last_ts": data["messages"][-1]["ts"] if data.get("messages") else None,
                })
    return result


def daily_backup():
    """Резервная копия всех кабинетов раз в сутки."""
    # Храним последние 30 копий (один месяц)
    backup = os.path.join(BACKUP_DIR, f"backup_{datetime.now().strftime('%Y-%m-%d')}.json")
    all_data = {}
    for fn in os.listdir(CABINETS_DIR):
        if fn.endswith(".json"):
            path = os.path.join(CABINETS_DIR, fn)
            data = _safe_read(path)
            if data is not None:
                all_data[fn] = data
    backup_tmp = backup + ".tmp"
    with open(backup_tmp, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    shutil.move(backup_tmp, backup)
    # Удалить копии старше 30 дней
    cutoff = time.time() - 30 * 86400
    for fn in os.listdir(BACKUP_DIR):
        path = os.path.join(BACKUP_DIR, fn)
        try:
            if os.path.getmtime(path) < cutoff:
                os.remove(path)
        except Exception:
            pass
    return backup
