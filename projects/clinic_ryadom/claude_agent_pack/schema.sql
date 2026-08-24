-- ============================================================
-- Клиника Рядом - схема базы данных (PostgreSQL)
-- Требования: история навсегда, абонемент на всех врачей,
-- лимит 35/день/врача, согласие с галочкой, фото в истории.
-- ============================================================

-- Пользователи клиники
CREATE TABLE IF NOT EXISTS users (
    user_id     BIGINT PRIMARY KEY,          -- Telegram user_id
    username    TEXT,
    first_name  TEXT,
    created_at  TIMESTAMPTZ DEFAULT now(),
    lang        TEXT DEFAULT 'ru'
);

-- Согласие (политика конфиденциальности + мед дисклеймер "методист, не врач")
CREATE TABLE IF NOT EXISTS consent (
    user_id     BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    policy_agreed  BOOLEAN DEFAULT FALSE,    -- галочка на политику конфиденциальности
    disclaimer_agreed BOOLEAN DEFAULT FALSE, -- галочка на мед дисклеймер
    agreed_at   TIMESTAMPTZ
);

-- Абонемент пользователя (1 абонемент = доступ ко ВСЕМ врачам)
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id     BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    plan        TEXT DEFAULT 'monthly',      -- monthly (1690 руб/мес)
    date_start  TIMESTAMPTZ DEFAULT now(),
    date_end    TIMESTAMPTZ,                  -- null = активен пока не истечёт
    status      TEXT DEFAULT 'active',        -- active | expired | blocked | pending_payment
    paid        BOOLEAN DEFAULT FALSE,        -- оплачен ли (заглушка: вручную, потом CloudPayments)
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- История диалога пользователя у каждого врача (ОТДЕЛЬНО на каждого врача)
CREATE TABLE IF NOT EXISTS chat_history (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    doctor_key  TEXT NOT NULL,                -- 'terapevt','psiholog','kardiolog','gastro','nevrolog','dermatolog'
    role        TEXT NOT NULL,                -- 'user' | 'assistant'
    content     TEXT NOT NULL,
    photo_file  TEXT,                         -- file_id фото, если прикреплено
    created_at  TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_history_user_doctor ON chat_history(user_id, doctor_key, created_at);

-- Дневной лимит обращений пользователя к каждому врачу
CREATE TABLE IF NOT EXISTS daily_limits (
    user_id     BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    doctor_key  TEXT NOT NULL,
    day         DATE NOT NULL DEFAULT CURRENT_DATE,
    count       INT DEFAULT 0,
    PRIMARY KEY (user_id, doctor_key, day)
);
-- Лимит за день на каждого врача = 35 (задаётся в коде константой, здесь храним счётчик)

-- Платежи (заглушка для CloudPayments, потом заполним)
CREATE TABLE IF NOT EXISTS payments (
    id          BIGSERIAL PRIMARY KEY,
    user_id     BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    amount      NUMERIC(10,2),
    currency    TEXT DEFAULT 'RUB',
    status      TEXT DEFAULT 'pending',        -- pending | success | failed
    provider    TEXT DEFAULT 'cloudpayments',  -- заглушка
    provider_tx TEXT,                          -- id транзакции от провайдера
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- Админы клиники (Артур)
CREATE TABLE IF NOT EXISTS admins (
    user_id     BIGINT PRIMARY KEY,
    role        TEXT DEFAULT 'owner'
);
INSERT INTO admins (user_id, role) VALUES (199790247, 'owner')
    ON CONFLICT (user_id) DO NOTHING;
