# -*- coding: utf-8 -*-
"""
Клиника Рядом - retention-уведомления (push) через отдельный cron-поток.

Запускается в main() главного бота отдельным потоком со СВОИМ event loop
и своим токеном, чтобы не зависеть от polling-цикла бота.

Три типа уведомлений, каждый шлётся ОДИН раз на событие (single-fire) -
для этого таблица notify_log с PRIMARY KEY (user_id, notify_type, day):

1. trial_end        - за TRIAL_WARN_DAYS (1) дня до конца триала
2. subscription_end - за SUBSCRIPTION_WARN_DAYS (2) дня до истечения подписки
3. daily_limit      - шлётся прямо в bot.py при обращении к врачу (не здесь)

Без дублей/спама: каждый шлём только если в notify_log нет записи на сегодня.
"""
import asyncio
import datetime
import logging
import time

import config
import db

log = logging.getLogger("notify")


def _days_left(end_dt):
    """Сколько полных дней осталось до end_dt (>=0), либо None."""
    if not end_dt:
        return None
    left = end_dt - datetime.datetime.now(datetime.timezone.utc)
    days = int(left.total_seconds() // 86400)
    return max(0, days)


async def _send_async(bot, user_id, text, notify_type):
    try:
        await bot.send_message(chat_id=user_id, text=text)
        db.notify_mark(user_id, notify_type)
        log.info("Уведомление %s отправлено user=%s", notify_type, user_id)
    except Exception as e:
        log.warning("Не смог отправить %s user=%s: %s", notify_type, user_id, e)


async def check_trial_end(bot):
    """Шлёт уведомление ровно за TRIAL_WARN_DAYS дня(ей) до конца триала."""
    target = config.TRIAL_WARN_DAYS  # например 1
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT user_id, trial_end_at FROM consent
               WHERE trial_started_at IS NOT NULL
                 AND trial_end_at IS NOT NULL
                 AND trial_end_at > now()"""
        )
        rows = cur.fetchall()
    for r in rows:
        uid = r["user_id"]
        if db.notify_logged(uid, config.NOTIFY_TRIAL):
            continue
        if _days_left(r["trial_end_at"]) == target:
            text = (
                f"⏳ Завтра заканчивается ваш бесплатный период "
                f"({config.TRIAL_LABEL}).\n\n"
                f"Оформите абонемент {config.PRICE_LABEL} "
                f"(или {config.PRICE_YEARLY_LABEL} - выгоднее), чтобы "
                "не потерять доступ ко всем 6 врачам.\n\n"
                "История бесед сохранится."
            )
            await _send_async(bot, uid, text, config.NOTIFY_TRIAL)


async def check_subscription_end(bot):
    """Шлёт уведомление за 1..SUBSCRIPTION_WARN_DAYS дня до истечения подписки."""
    target = config.SUBSCRIPTION_WARN_DAYS  # например 2
    with db.get_conn() as conn, conn.cursor() as cur:
        cur.execute(
            """SELECT user_id, date_end FROM subscriptions
               WHERE status='active' AND date_end IS NOT NULL AND date_end > now()"""
        )
        rows = cur.fetchall()
    for r in rows:
        uid = r["user_id"]
        if db.notify_logged(uid, config.NOTIFY_SUB):
            continue
        days = _days_left(r["date_end"])
        if days is not None and 1 <= days <= target:
            text = (
                f"💳 Ваша подписка заканчивается через {days} дн.\n\n"
                "Продлите заранее, чтобы не потерять доступ ко всем 6 врачам.\n"
                f"• {config.PRICE_LABEL}\n"
                f"• {config.PRICE_YEARLY_LABEL} "
                f"(≈{config.PRICE_YEARLY_MONTH_LABEL}, выгоднее)\n\n"
                "История бесед сохранится."
            )
            await _send_async(bot, uid, text, config.NOTIFY_SUB)


def run_forever(token):
    """Фоновый поток: свой event loop + свой бот, цикл раз в несколько часов."""
    import telegram
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bot = telegram.Bot(token=token)
    log.info("Notify-поток запущен")
    interval = 6 * 3600  # каждые 6 часов
    while True:
        try:
            loop.run_until_complete(check_trial_end(bot))
            loop.run_until_complete(check_subscription_end(bot))
        except Exception as e:
            log.error("Notify-проход упал: %s", e, exc_info=True)
        time.sleep(interval)
