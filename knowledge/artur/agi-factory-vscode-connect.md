# Как подключиться к VS Code Tunnel (база знаний Завода Джарвисов)

Источник: статья kb.mcdenil.com, прислана Артуром 24.08.2026.

## Суть
Раньше 3 шага через браузер, теперь одна команда /connect в Telegram. Бот сам поднимает туннель и шлёт ссылку.

## Способ 1 — /connect (рекомендуется)
1. /connect в чате.
2. GitHub авторизация: github.com/login/device → ввести код XXXX-XXXX → подтвердить.
3. Туннель поднят → кнопка 🔗 Открыть в браузере → vscode.dev с файлами.

## Способ 2 — десктопный VS Code
VS Code → Cmd/Ctrl+Shift+P → Remote-Tunnels: Connect to Tunnel → выбрать туннель (agent-XXXXXXXX).

## Способ 3 — ручной
vscode.dev → Open Remote Window → Connect to Tunnel → GitHub → выбрать туннель.

## Отключение
⏹ Отключить или /connect → кнопка.

## Проблемы
- Timeout → /connect снова.
- 2FA на GitHub → подтвердить вторым фактором.
- Tunnel offline → подождать 30 сек.

## Применение к нашему заводу
У нас доступ к файлам сервера уже есть напрямую: exec (команды) + read/write/edit (файлы) + SSH к MacBook через Tailscale. VS Code Tunnel не нужен — Артур просит меня, я работаю с файлами сам.
