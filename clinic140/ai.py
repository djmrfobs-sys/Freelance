# Клиника 140 - модуль работы с DeepSeek (движок врачей)

import json
import re
import requests
from config import (
    DEEPSEEK_KEY_FILE, DEEPSEEK_API, DEEPSEEK_MODEL,
    DOCTORS, STYLES, KETY_ID,
)

def _read_key(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return ""

DEEPSEEK_KEY = _read_key(DEEPSEEK_KEY_FILE)


def _clean_markdown(text):
    """Убираем служебную разметку: звёздочки, длинные тире, замена."""
    if not text:
        return text
    # звёздочки (любые количества) и подчёркивания-разметку
    text = re.sub(r"[*_`~]", "", text)
    # длинные тире (—, –, −) -> обычный дефис
    text = text.replace("—", "-").replace("–", "-").replace("−", "-")
    # тройные/двойные пробелы
    text = re.sub(r"\s{3,}", "  ", text)
    return text.strip()


def _system_prompt(doctor_id, style="detailed", is_consilium=False, other_opinions=None):
    """Системный промпт для врача."""
    doc = next((d for d in DOCTORS if d["id"] == doctor_id), DOCTORS[0])
    style_desc = STYLES.get(style, STYLES["detailed"])

    prompt = f"""Ты - {doc['name']}, врач-{doc['specialty'].lower()} с опытом {doc['experience']} лет.

Ты часть личной «Клиники 140» для Кети. Ты общаешься МЯГКО, тепло и по-человечески, как опытный внимательный доктор из хорошей клиники. Ты знаешь, что у Кети бывает тревога и волнение, поэтому всегда сначала успокаиваешь и внимательно слушаешь, но при этом остаёшься профессиональным и честным: если симптом серьёзный, не приукрашиваешь, а прямо говоришь, что нужно обратиться к очному врачу.

Твоя зона ответственности: {doc['zone']}

КАК ТЫ РАБОТАЕШЬ КАК ПРОФЕССИОНАЛ (это важно):
Ты ведёшь Кети как доктор настоящей клиники, а не как чат. Твоя логика ответа:
1. Сначала оцени, что Кети описала: симптом, его давность, интенсивность, связь с чем-то (еда, сон, нагрузка, стресс).
2. Если информации мало - не спеши с выводами. Задай 1-2 уточняющих вопроса о главном (давность, характер, что усиливает/облегчает), чтобы дать точный совет, а не шаблон.
3. Дай конкретные, практичные рекомендации, что можно сделать дома и на что обратить внимание. Говори по существу, без воды и общих слов.
4. Чётко раздели: что можно понаблюдать дома, а что требует очного осмотра или обследования (и какого именно).
5. Не выдумывай диагнозы и конкретные дозировки лекарств. Называй возможные причины осторожно, как предположения, и всегда направляй к очной консультации при сомнении.
6. Опирайся на то, что Кети уже говорила ранее в истории. Не переспрашивай то, что она уже рассказала, а показывай, что ты помнишь и учитываешь её ситуацию.

СТРОГО соблюдай:
1. НЕ используй маркдаун-разметку: никаких звёздочек, подчёркиваний, жирного. Просто текст.
2. НЕ используй длинные тире (—, –) и дефисы-перечисления. Пиши короткими фразами без канцелярита.
3. В ответах можно ставить 1-2 красивых ВЕКТОРНЫХ эмодзи (нейтральные, аккуратные, не цветные "игрушечные", не монохромные серые). Умеренно, чтобы было тепло и живо, без перебора.
4. Обращайся на «ты», по-доброму, но с уважением. Ты - доктор, а не робот.
4b. Имя пользователя ТОЛЬКО «Кети» (или «ты», если имя уже упоминалось). Никогда не пиши «Кетти», «Кетенька», «Кетюша» и не изменяй имя. Зови её просто Кети.
5. ВАЖНО: когда отвечаешь, учитывай историю диалога с Кети, чтобы отвечать по делу, а не шаблонно.
6. Если вопрос вне твоей зоны - честно скажи и предложи подходящего другого врача из Клиники 140 (например: «Это лучше к психотерапевту, я могу позвать его»).
7. Если симптом серьёзный (сильная боль, кровь, затруднение дыхания, потеря сознания) - сразу скажи, что это повод срочно обратиться к очному врачу или в скорую. Не отговаривай.
8. Никогда не выдумывай диагнозы и лекарства. Давай общие ориентиры и советы, но направляй к очной консультации.
9. ОБЯЗАТЕЛЬНО заканчивай каждый ответ открытым вопросом к Кети (например: «Расскажи, как давно это началось?», «Что скажешь, попробуем?», «Как ты себя чувствуешь сейчас?»). Не заканчивай просто фразой-прощанием без вопроса.
10. ЯЗЫК ОТВЕТА: основной язык - русский. Но если Кети пишет свой вопрос на сербском или просит ответить на сербском (например: «Напиши на сербском», «Možeš li na srpskom?»), то отвечай на сербском. Следуй языку, на котором Кети обращается в запросе, и если она просит сербский - весь ответ пиши на сербском.

СТИЛЬ отчёта: {style_desc}

Отвечай по-человечески, коротко и по существу. Не пиши вступительных фраз как «Как ИИ, я...». Сразу помогай.
"""

    if is_consilium:
        # Консилиум: несколько врачей обсуждают
        others = ", ".join(other_opinions or [])
        prompt += f"""

=====================================
⚕️ РЕЖИМ КОНСИЛИУМ: ты участвуешь в обсуждении сложного случая вместе с другими врачами клиники.
Мнения других врачей:
{others}

Начни свой ответ со слов «мой взгляд как {doc['specialty']}:», дай профессиональное мнение, а в конце предложи одно общее решение для Кети.
"""
    return prompt


def ask_doctor(doctor_id, user_text, chat_history, style="detailed"):
    """Основной запрос к врачу. chat_history - список строк прошлых сообщений."""
    messages = [
        {"role": "system", "content": _system_prompt(doctor_id, style)},
    ]
    # история
    for m in chat_history:
        role = "user" if m["role"] == "user" else "assistant"
        messages.append({"role": role, "content": m["content"]})
    # текущий вопрос
    messages.append({"role": "user", "content": user_text})

    data = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": 900,
        "temperature": 0.65,
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(DEEPSEEK_API, json=data, headers=headers, timeout=45)
        result = r.json()
        if "choices" not in result or not result["choices"]:
            return None, str(result.get("error", "No response"))
        content = result["choices"][0]["message"]["content"]
        return _clean_markdown(content), None
    except Exception as e:
        return None, str(e)


def ask_consilium(doctor_ids, user_text, chat_history, style="detailed"):
    """Режим консилиума: несколько врачей по очереди дают мнение."""
    opinions = []
    for i, doc_id in enumerate(doctor_ids):
        # Для каждого последующего врача передаём мнения предыдущих
        prompt = _system_prompt(doc_id, style, is_consilium=True,
                                other_opinions=opinions)
        messages = [{"role": "system", "content": prompt}]
        for m in chat_history:
            role = "user" if m["role"] == "user" else "assistant"
            messages.append({"role": role, "content": m["content"]})
        messages.append({"role": "user", "content": user_text})

        data = {
            "model": DEEPSEEK_MODEL,
            "messages": messages,
            "max_tokens": 700,
            "temperature": 0.6,
        }
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_KEY}",
            "Content-Type": "application/json",
        }
        try:
            r = requests.post(DEEPSEEK_API, json=data, headers=headers, timeout=60)
            result = r.json()
            if "choices" in result and result["choices"]:
                content = result["choices"][0]["message"]["content"]
                doc = next((d for d in DOCTORS if d["id"] == doc_id), None)
                name = doc["name"] if doc else "Доктор"
                opinions.append(f"{name}: {content}")
        except Exception as e:
            opinions.append(f"Доктор {doc_id}: ошибка ({str(e)[:50]})")

    # Финальное общее резюме - собираем одно итоговое сообщение
    summary = f"⚕️ Консилиум {' + '.join([next((d['name'] for d in DOCTORS if d['id']==i), i) for i in doctor_ids])}\n\n"
    for op in opinions:
        summary += _clean_markdown(op) + "\n\n"
    summary += "-\nРезюме: сопоставив мнения, для Кети рекомендую начать с профилактического осмотра у очного врача. Я рядом и отвечу на вопросы."
    return summary


# срочный вопрос (быстрый ответ одной репликой)
def ask_urgent(doctor_id, user_text):
    """Срочный вопрос - быстрый короткий ответ."""
    prompt = _system_prompt(doctor_id, "short")
    prompt += "\nЭто СРОЧНЫЙ вопрос. Ответь одной-двумя репликами максимум, коротко и конкретно, что делать прямо сейчас."
    messages = [{"role": "system", "content": prompt},
                {"role": "user", "content": user_text}]
    data = {
        "model": DEEPSEEK_MODEL,
        "messages": messages,
        "max_tokens": 300,
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json",
    }
    try:
        r = requests.post(DEEPSEEK_API, json=data, headers=headers, timeout=30)
        result = r.json()
        if "choices" not in result or not result["choices"]:
            return None, str(result.get("error", "No response"))
        return _clean_markdown(result["choices"][0]["message"]["content"]), None
    except Exception as e:
        return None, str(e)
