# 🏭 НЕЙРОЗАВОД KISELEVY CREO - ЕДИНЫЙ РЕЕСТР ПРОДУКТОВ
### Этап 1 - Память и структура. Эта карта = вся империя цифровых продуктов в одном месте.

Правило: код ботов НЕ переносим (запущены systemd с абсолютными путями). Эта карта - навигатор, где что лежит и что делает.

---

## A. TELEGRAM-БОТЫ (активные, на systemd)

### A1. @Investor_fobs_bot - Мистер Фобс (фин. аналитик)
- Роль: личный финансовый аналитик, капитал от $1000, мыслит как миллиардер
- Код: /root/workspace/fobs_projects/investor/
- Cервис: fobs_investor_bot.service
- Можно: разбор сумм, дайджест, риск, обучение, симулятор
- Статус: МVP работает

### A2. @Fobs_djarvis_bot - личный ассистент Артура
- Роль: психолог + бухгалтер + юрист (также цех "Ментус")
- Код: /root/workspace/fobs_assistant_bot.py
- Сервис: fobs_assistant_bot.service
- Статус: работает

### A3. @translater_fobs_bot - переводчик серб⇄рус
- Роль: перевод текста/голоса/фото, озвучка
- Код: projects/serbian_translator_bot/bot.py
- Сервис: serbian-translator-bot.service
- Стек: DeepSeek + Groq Whisper + Google TTS
- Последнее: добавлена озвучка русским голосом при переводе на русский (13.08)
- Статус: работает

### A4. @TZ_fobs_bot_bot - МегаМозг
- Роль: аналитик, разбор ссылок, генератор идей и ТЗ для нейрофабрики
- Код: projects/zavod/01_megamind/ (также projects/megamind_bot/)
- Сервис: megamind-bot.service
- Статус: в работе (добавлен /analyze)

### A5. @Fobs_djarvis_bot (Ментус) - психо/бух/юрист
- Код: projects/zavod/02_mentus/
- Роль: психолог/бухгалтер/юрист, OCR чеков
- Статус: тестируем OCR чеков

### A6. Karen Bro (karen-bot)
- Код: projects/zavod/04_karen/ (также projects/karen-bot/)
- Сервис: karen-bot.service
- Статус: работает

### A7. @Nigt_help_bot - Content Poster
- Роль: автопосты в каналы KISELEVY CREO
- Код: projects/zavod/05_content_bot/ (также projects/content_bot/)
- Сервис: content-bot.service
- Статус: работает

### A8. @maks_lab_neuro_bot - Нейро-ассистент Максима
- Код: projects/zavod/07_maksim_bot/
- Сервис: maksim-bot.service
- Статус: работает

### A9. Bagovskaya бот (сервис клиника/бухгалтерия)
- Код: bagovskaya_bot.py (корень workspace)
- Сервис: отдельный (проверить имя)
- Статус: работает, лог bagovskaya_bot.log

---

## B. КЛИНИКИ (медицинские боты)

### B1. Клиника Рядом - комплекс (7 ботов)
- Код: projects/clinic_ryadom/
- Сервисы: clinic-ryadom-main, clinic-ryadom-dermatolog, clinic-ryadom-gastro, clinic-ryadom-kardiolog, clinic-ryadom-nevrolog, clinic-ryadom-psiholog, clinic-ryadom-terapevt
- Роль: запись к врачам-специалистам
- Статус: все активны
- Задача клиники: добавить голосовые (Whisper/Groq), чтение фото (Vision), генерацию картинок (Gemini/Flux)

### B2. Клиника 140 - личный бот для Кети
- Роль: Doctors_for_kety_bot
- Код: projects/clinic140/
- Сервис: clinic140.service
- Статус: активен

---

## C. САЙТЫ И ЛЕНДИНГИ

### C1. KISELEVY CREO сайт (основной)
- Код: projects/kiselevy_creo_site/ + projects/kiselevy-creo-site/ + kiselevy_creo_site.html (корень)
- Dev: kiselevy-creo-oprosnik/ (опросник)
- Статус: готов, дорабатывается

### C2. Bagovskaya Boho (клиентский сайт)
- Projeкт: Lovable - https://lovable.dev/projects/201e09af...
- Preview: https://bagovskaia-boho-ru.lovable.app

---

## D. НЕЙРОПОМОЩНИКИ (направление, прайс готов)

Прейскурант утверждён, страница в прайсе собрана (услуги+нейро+пакеты). Пункты:
1. Нейропродавец - 149 000 ₽
2. Нейрокоуч - 129 000 ₽
3. Нейропсихолог - 129 000 ₽
4. Нейроконсультант - 99 000 ₽
5. Нейропомощник под задачу - от 99 000 ₽
6. Для личного пользования - от 49 000 ₽
- Прайс-файлы: projects/kiselevy_creo/Наш Прайс/

---

## E. ПРАЙС И ДОКУМЕНТЫ
- Папка «Наш Прайс»: projects/kiselevy_creo/Наш Прайс/
  - КИСЕЛЁВЫ_КРЕО_прайс.pdf (6 стр)
  - Прайс_база_внутренняя.pdf (12 стр) + .md
- Договоры: projects/dogovor/, projects/contracts/, бартерные шаблоны

---

## F. ЗАВОД (projects/zavod/) - структура цехов
- 01_megamind, 02_mentus, 03_translater, 04_karen, 05_content_bot, 06_site_projects, 07_maksim_bot
- template/TZ.md - форма ТЗ для нового заказа
- archive/ - завершённые
- projects.md - реестр завода (обновить статусы)

---

## СТРУКТУРА ПАПОК (новая, для памяти)
- memory/ - память (daily notes, MEMORY.md, STRUCTURE.md, inbox.md)
- products/ - robots, sites, neuro_assistants, funnels
- clients/ - по клиентам
- content/ - channels, reels, campaigns
- docs/ - TZ, contracts
- research/ - анализ, парсинг, аудиты
- playbooks/ - чек-листы и схемы работы
- referrals/ - партнёрства
- assets/ - images, audio, documents
