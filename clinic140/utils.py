# Клиника 140 - вспомогательные функции (PDF, голос, поиск фото из интернета)

import os
import io
import tempfile
import requests
from datetime import datetime
from config import (
    GROQ_KEY_FILE, GROQ_STT_URL, GROQ_STT_MODEL,
    DOCTORS, VOICE_DIR, MEDIA_DIR,
)

os.makedirs(VOICE_DIR, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)

def _read_key(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

GROQ_KEY = _read_key(GROQ_KEY_FILE)


# ============ PDF экспорт ============
def build_pdf(chat_id, cabinets_data, user_name="Кети"):
    """Собрать PDF со всей историей диалогов. Возвращает путь к файлу."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    # Поддержка кириллицы: ищем DejaVu (обычно есть в системе)
    font_path = None
    for cand in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]:
        if os.path.exists(cand):
            font_path = cand
            break
    if font_path:
        pdfmetrics.registerFont(TTFont("DejaVu", font_path))
        font_name = "DejaVu"
    else:
        font_name = "Helvetica"  # кириллица может не отобразиться

    pdf_path = os.path.join(MEDIA_DIR, f"clinic140_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    y = height - 25 * mm
    c.setFont(font_name, 18)
    c.drawString(20 * mm, y, f"Клиника 140 - История консультаций ({user_name})")
    y -= 8 * mm
    c.setFont(font_name, 10)
    c.drawString(20 * mm, y, f"Сформировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    y -= 12 * mm

    for cabinet in cabinets_data:
        doc = next((d for d in DOCTORS if d["id"] == cabinet["doctor_id"]), None)
        if not doc:
            continue
        # заголовок кабинета
        c.setFont(font_name, 14)
        c.setFillColorRGB(0.1, 0.3, 0.6)
        c.drawString(20 * mm, y, f"{doc['emoji']} {doc['name']} - {doc['specialty']}")
        y -= 8 * mm
        c.setFillColorRGB(0, 0, 0)
        c.setFont(font_name, 9)

        for msg in cabinet.get("messages", []):
            if y < 25 * mm:
                c.showPage()
                c.setFont(font_name, 9)
                y = height - 20 * mm
            prefix = "Кети" if msg["role"] == "user" else "Доктор"
            ts = msg.get("ts", "")[:16].replace("T", " ")
            text = f"[{ts}] {prefix}: {msg['content']}"
            # перенос строк
            lines = _wrap_text(text, c, width - 40 * mm)
            for ln in lines:
                c.drawString(20 * mm, y, ln)
                y -= 4.8 * mm
            y -= 2 * mm
        y -= 6 * mm

    c.save()
    return pdf_path


def _wrap_text(text, canvas_obj, max_width):
    """Простой перенос текста по ширине в пикселях (приблизительно)."""
    lines = []
    for para in text.split("\n"):
        if not para:
            lines.append("")
            continue
        cur = ""
        for word in para.split(" "):
            test = (cur + " " + word).strip()
            if canvas_obj.stringWidth(test, canvas_obj._fontname, canvas_obj._fontsize) > max_width:
                if cur:
                    lines.append(cur)
                cur = word
            else:
                cur = test
        lines.append(cur)
    return lines


# ============ Голос -> текст (Groq Whisper) ============
def transcribe_voice(file_bytes, filename):
    """Преобразовать аудио в текст через Groq Whisper."""
    tmp_path = os.path.join(VOICE_DIR, f"voice_{datetime.now().timestamp()}.ogg")
    with open(tmp_path, "wb") as f:
        f.write(file_bytes)
    try:
        headers = {"Authorization": f"Bearer {GROQ_KEY}"}
        with open(tmp_path, "rb") as f:
            files = {"file": (filename or "voice.ogg", f, "audio/ogg")}
            data = {"model": GROQ_STT_MODEL, "language": "ru"}
            r = requests.post(GROQ_STT_URL, headers=headers, files=files, data=data, timeout=60)
        result = r.json()
        if "text" in result:
            return result["text"].strip(), None
        return None, str(result.get("error", "no text"))
    except Exception as e:
        return None, str(e)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def download_file(bot, file_id, suffix=".jpg"):
    """Скачать файл из Telegram (фото/видео/документ). Возвращает путь."""
    fi = bot.get_file(file_id)
    path = os.path.join(MEDIA_DIR, f"media_{datetime.now().timestamp()}{suffix}")
    bot.download_file(fi.file_path, path)
    return path
