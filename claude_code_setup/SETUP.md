# Инструкция по настройке Claude Code Agent — KISELEVY CREO

## 1. Создать CLAUDE.md в корне проекта

Скопируй файл CLAUDE.md в папку, откуда будешь запускать Claude Code.
Лучше всего — в корень ~/Desktop/Project/ или в ~/Desktop/Project/Мои проекты/

```bash
cp ~/Desktop/Project/CLAUDE.md ~/Desktop/Project/CLAUDE.md
```

## 2. Настроить MCP-сервера

Скопируй .mcp.json в корень проекта:

```bash
cp ~/Desktop/Project/.mcp.json ~/Desktop/Project/.mcp.json
```

### GitHub токен (пропусти — у тебя уже есть SSH-ключи)

Будешь работать через SSH — GitHub MCP-сервер запросит токен при первом запуске. Создай его если нужно:
1. https://github.com/settings/tokens → Generate new token (classic) → repo, workflow
2. Добавь в ~/.zshrc:
   ```bash
   export GITHUB_TOKEN="токен"
   ```
   Потом `source ~/.zshrc`

### Supabase MCP
Запусти Claude Code и выполни аутентификацию:
```bash
claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp"
claude /mcp
```
Выбери "supabase" → "Authenticate" → откроется браузер, войди в Supabase.

## 3. Запуск агента

```bash
cd ~/Desktop/Project
claude
```

Или для конкретного подпроекта:
```bash
cd ~/Desktop/Project/Мои\ проекты
claude
```

## 4. Примеры команд агенту

После запуска пиши задачи прямо в терминал Claude Code:

**Кодинг:**
- "Посмотри структуру проекта в Мои проекты и опиши что там"
- "Найди баг в файле bot.py и почини"
- "Создай GitHub репозиторий для нового бота и запушь код"
- "Сделай рефакторинг main.py — вынеси логику в отдельные модули"

**Анализ:**
- "Прочитай все файлы в этой папке и скажи что за проект"
- "Найди все упоминания API-ключей в коде"

**Supabase:**
- "Покажи структуру таблиц в Supabase"
- "Напиши SQL-запрос для создания таблицы users"

**Telegram-посты (через файлы):**
- "Создай файл post.md с постом для @ecstatic_dance_mantra про новую мантру"

## 5. Быстрые команды

- `/plan` — Claude составит план перед тем как писать код
- `/debug` — найти и исправить ошибку
- `/review` — проверить код
- `claude mcp list` — посмотреть подключенные MCP-сервера
- `claude mcp test supabase` — проверить соединение с Supabase
