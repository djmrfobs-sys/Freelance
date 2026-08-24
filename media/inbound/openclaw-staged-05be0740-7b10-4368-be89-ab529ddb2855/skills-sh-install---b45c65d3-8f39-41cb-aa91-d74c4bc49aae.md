# Установка готовых скиллов с skills.sh

Выполнить на сервере (там, где установлен openclaw / есть node+npm).

## 1. verification-before-completion (obra/superpowers)
Готовая, более прокачанная версия "Правила отчётности" — не считать задачу закрытой без реальной проверки сырым выводом.

    npx skills add obra/superpowers/verification-before-completion

Опционально из того же набора (тоже полезны, но не обязательны сразу):
    npx skills add obra/superpowers/systematic-debugging
    npx skills add obra/superpowers/writing-plans

## 2. skill-creator (официальный Anthropic)
Учит агента правильно писать новые скиллы — снижает шанс новых дублей вроде тех 95, что уже разбирали.

    npx skills add anthropics/skills/skill-creator

## 3. to-questionnaire (mattpocock)
Готовый алгоритм сбора требований через структурированные вопросы — дополняет ваш tz-gathering.

    npx skills add mattpocock/skills/to-questionnaire

---

## После установки
1. Проверить, что скиллы появились: `ls ~/.openclaw-neuro/skills/` (или актуальный путь) — должны быть новые папки verification-before-completion, skill-creator, to-questionnaire
2. Добавить их в skills/INDEX.md — по вашему же правилу: перед добавлением скилла сверяться с реестром, и после добавления — дописывать строку
3. Прислать сырой вывод `ls` после установки для подтверждения
