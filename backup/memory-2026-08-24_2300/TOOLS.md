# TOOLS.md - Local Notes

## Lovable
- Email: dj.mr.fobs@gmail.com
- Pass: Xt26&.ydE9@sW4.8
- Проект Bagovskaya Boho: https://lovable.dev/projects/201e09af-4032-4301-ab21-e488f36824dd
- Preview: https://bagovskaia-boho-ru.lovable.app

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## MacBook Артура (SSH)
- SSH: mr.fobs@100.121.95.85 (через Tailscale)
- macOS 26.5.2, MacBook Air «MR»
- Tailscale: сервер 100.104.175.5, MacBook 100.121.95.85
- Подписка Claude Max (dj.mr.fobs@gmail.com)
- Claude Code на СЕРВЕРЕ (основной, 24/7): ~/.local/bin/claude (v2.1.241), залогинен через Max. Запуск: ~/.local/bin/claude -p "..." (print-mode headless).
- Claude Code на MacBook: ~/.local/bin/claude, тоже залогинен. Запуск через SSH: ssh -t mr.fobs@100.121.95.85 '~/.local/bin/claude -p "..."'
- Рабочая папка Артура на MacBook: ~/Desktop/«Мои РАБОТЫ И ДАННЫЕ» - беру оттуда фото/текст/материалы через SSH.

## Парсинг документов (установлено 24.08.2026)
- PDF: pdftotext (poppler-utils)
- Word: python-docx
- Excel: openpyxl
- Читаю договоры .docx/.pdf/.xlsx как текст для анализа.

## Related

- [Agent workspace](/concepts/agent-workspace)
