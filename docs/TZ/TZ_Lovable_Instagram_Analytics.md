# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
## "Insta Navigator AI" — Расширение модулей аналитики

**Дата:** 15.07.2026  
**Версия:** 2.0  
**Статус:** В разработку

---

## 1. ОБЗОР ПРОЕКТА

### Цель
Расширить существующую систему "Insta Navigator AI" тремя критичными модулями аналитики для глубокого анализа Instagram аккаунтов и отслеживания их роста.

### Текущее состояние
- ✅ Instagram Parser (профиль, посты, комменты)
- ✅ Telegram Parser
- ✅ Content Plans
- ✅ Reels Scenarios
- ✅ Audits
- ❌ Dashboard Analytics (новое)
- ❌ Growth Tracker (новое)
- ❌ Hashtag Research (новое)

### Новые модули (приоритет)
1. **Dashboard Analytics** — визуальная аналитика
2. **Growth Tracker** — отслеживание роста
3. **Hashtag Research** — исследование хештегов

---

## 2. МОДУЛЬ 1: DASHBOARD ANALYTICS 📊

### Описание
Визуальный дашборд с графиками и метриками роста Instagram аккаунта.

### Функциональные требования

#### 2.1 Основные метрики (Cards)
```
┌─────────────────────────────────────────┐
│  Total Followers  │  Avg Likes/Post     │
│     2,534 (↑3%)   │     340 (↑12%)      │
├─────────────────────────────────────────┤
│  Engagement Rate  │  Best Post Type     │
│     8.2% (↑1.5%)  │    Reels (62%)      │
└─────────────────────────────────────────┘
```

#### 2.2 Графики
1. **Followers Growth Chart**
   - Тип: Line chart
   - Период: 7, 30, 90 дней
   - Y-axis: Кол-во подписчиков
   - X-axis: День/неделя/месяц
   - Тренд: ↑/↓ линия тренда

2. **Engagement Trend**
   - Тип: Bar chart
   - Метрики: Likes, Comments, Saves
   - Период: 7, 30, 90 дней
   - Сравнение: % изменение

3. **Post Performance Distribution**
   - Тип: Pie chart
   - Данные: 
     - Reels: % от всех постов
     - Carousel: % от всех постов
     - Posts: % от всех постов
     - Stories: % от всех постов

4. **Optimal Posting Time Heatmap**
   - Тип: Heat map
   - X-axis: Час дня (0-23)
   - Y-axis: День недели (Пн-Вс)
   - Цвет: Интенсивность лайков (red=best, blue=worst)

#### 2.3 Фильтры
- Период: Last 7 days, 30 days, 90 days, Custom range
- Post type: All, Reels, Carousel, Posts, Stories
- Metric: Engagement Rate, Reach, Saves, Shares

#### 2.4 Экспорт
- PDF report (автоматически)
- CSV (для таблиц)
- PNG (для графиков)

### Технические требования
- **Data source:** Apify Instagram Scraper API
- **Update frequency:** Ежедневно (00:00 UTC)
- **Chart library:** Chart.js или Recharts
- **Data points:** Минимум 30 последних дней
- **Performance:** Загрузка <2сек

---

## 3. МОДУЛЬ 2: GROWTH TRACKER 📈

### Описание
Отслеживание истории роста профиля с прогнозами и аналитикой.

### Функциональные требования

#### 3.1 История роста (Timeline)
```
Дата      | Followers | Daily Change | Engagement | Notes
━━━━━━━━━━╋═══════════╋══════════════╋════════════╋═════════
15.07.26  |   2,534   |      +5      |   8.2%     | New Reels
14.07.26  |   2,529   |      +2      |   7.8%     | -
13.07.26  |   2,527   |     +15      |   9.1%     | Collab
```

#### 3.2 Growth Analytics
1. **Weekly/Monthly Summary**
   - Среднее добавление в день
   - Best day (максимум)
   - Worst day (минимум)
   - Total change

2. **Growth Rate Chart**
   - Линейный или полиноминальный тренд
   - Прогноз на 30 дней вперёд
   - Confidence interval (95%)

3. **Engagement Correlation**
   - Сравнение: Posts published vs Followers gained
   - Correlation score (%)

#### 3.3 Прогнозирование
```
Current:    2,534 followers
7 days:     ~2,600 (+2.6%)
30 days:    ~2,800 (+10.5%)
90 days:    ~3,200 (+26.2%)
Confidence: 85%
```

#### 3.4 Метрики
- Followers growth rate (%)
- Average daily growth
- Best performing content (по followers)
- Content frequency impact
- Engagement trend

### Технические требования
- **Data storage:** Database (Firebase/MongoDB)
- **Update:** Daily snapshots
- **Forecast algorithm:** Linear regression или ARIMA
- **Historical data:** Минимум 90 дней для точности

---

## 4. МОДУЛЬ 3: HASHTAG RESEARCH 🏷️

### Описание
Исследование хештегов: популярность, сложность, рекомендации.

### Функциональные требования

#### 4.1 Поиск хештегов
```
Input: Введи хештег или тему
Output:
┌─────────────────────────────────┐
│ #вайбкодинг                     │
├─────────────────────────────────┤
│ Posts: 45.2K                    │
│ Difficulty: 6/10 (Medium)       │
│ Engagement: 3.2%                │
│ Growth: ↑12% (last 30 days)     │
│ Trend: Hot 🔥                   │
└─────────────────────────────────┘
```

#### 4.2 Метрики хештега
1. **Basic Stats**
   - Total posts with hashtag
   - Post frequency (posts/day)
   - Top posts ranking

2. **Difficulty Score** (0-10)
   ```
   = (Total posts) / 1000
   - <5K posts: Easy (0-3)
   - 5K-50K: Medium (4-6)
   - 50K-500K: Hard (7-8)
   - >500K: Very Hard (9-10)
   ```

3. **Engagement Metrics**
   - Avg likes per post
   - Avg comments per post
   - Avg saves per post
   - Engagement rate (%)

4. **Growth Trend**
   - Last 7 days change
   - Last 30 days change
   - Trend direction (↑/↓/→)
   - Prediction

#### 4.3 Рекомендации
```
🎯 TOP HASHTAGS FOR YOUR NICHE:

1. #вайбкодинг (Easy, 45.2K posts)
   → Engagement: 3.2% | Trend: ↑12%
   → Recommendation: USE (high traffic, low competition)

2. #цифровойфасад (Medium, 120K posts)
   → Engagement: 2.8% | Trend: ↑5%
   → Recommendation: USE (balanced)

3. #автоматизация (Hard, 580K posts)
   → Engagement: 1.2% | Trend: ↓3%
   → Recommendation: SKIP (high competition, low engagement)

STRATEGY:
- Use 3-5 Easy hashtags (high reach, low effort)
- Use 2-3 Medium hashtags (balanced)
- Skip Hard/Very Hard (waste of space)
```

#### 4.4 Related Hashtags
```
#вайбкодинг Related:
├─ #веб-разработка (145K posts)
├─ #фронтенд (89K posts)
├─ #javascript (2.3M posts) ❌ Skip
└─ #ui-дизайн (56K posts)
```

#### 4.5 Hashtag Tracking
- Сохранение избранных хештегов
- Отслеживание истории (как менялась сложность)
- Compare с конкурентами

### Технические требования
- **Data source:** Apify Hashtag Scraper
- **Update:** Еженедельно (по средам)
- **Database:** Кэш для быстрого поиска
- **Search performance:** <1сек

---

## 5. API ИНТЕГРАЦИИ

### 5.1 Apify API
```javascript
// Instagram Full Parser
POST https://api.apify.com/v2/acts/apify~instagram-scraper/runs
{
  "usernames": ["kiselevy_creo"],
  "resultsLimit": 50
}

// Response: профиль, посты, метрики
```

### 5.2 Database Schema

#### Users_Analytics
```sql
CREATE TABLE user_analytics (
  id PRIMARY KEY,
  username VARCHAR(255),
  date DATE,
  followers INT,
  engagement_rate FLOAT,
  posts_count INT,
  avg_likes INT,
  avg_comments INT,
  avg_saves INT,
  created_at TIMESTAMP
)
```

#### Hashtag_Data
```sql
CREATE TABLE hashtag_data (
  id PRIMARY KEY,
  hashtag VARCHAR(255),
  posts_count INT,
  engagement_rate FLOAT,
  difficulty_score INT,
  trend_direction VARCHAR(1), -- ↑↓→
  collected_at TIMESTAMP
)
```

---

## 6. UI/UX ТРЕБОВАНИЯ

### 6.1 Layout
```
┌─────────────────────────────────────────────┐
│  HEADER (Navigation)                        │
├────┬──────────────────────────────────────┤
│    │ Dashboard Analytics                  │
│ S  ├────────────────────────────────────┤
│ I  │ [Growth Tracker]                    │
│ D  ├────────────────────────────────────┤
│ E  │ [Hashtag Research]                  │
│ B  └────────────────────────────────────┘
│ A
│ R
└────┴──────────────────────────────────────┘
```

### 6.2 Color Scheme
- Primary: #2563eb (Blue)
- Success: #10b981 (Green)
- Warning: #f59e0b (Orange)
- Danger: #ef4444 (Red)
- Background: #f9fafb (Light Gray)

### 6.3 Typography
- Headings: Inter (700, 24px)
- Body: Inter (400, 14px)
- Mono: JetBrains Mono (code)

### 6.4 Responsive
- Desktop: 1920px
- Tablet: 768px
- Mobile: 375px

---

## 7. СРОКИ РАЗРАБОТКИ

| Модуль | Время | Статус |
|--------|-------|--------|
| Dashboard Analytics | 5 дней | To-Do |
| Growth Tracker | 4 дня | To-Do |
| Hashtag Research | 3 дня | To-Do |
| Testing & QA | 2 дня | To-Do |
| **ИТОГО** | **14 дней** | - |

---

## 8. КРИТЕРИИ ПРИЁМА

### Для Dashboard Analytics ✅
- [ ] Все 4 графика отображаются корректно
- [ ] Фильтры работают (7/30/90/Custom)
- [ ] Экспорт PDF/CSV/PNG функционирует
- [ ] Загрузка <2сек
- [ ] Мобильная версия адаптивна

### Для Growth Tracker ✅
- [ ] История отображается полностью
- [ ] Прогноз на 30/90 дней работает
- [ ] Correlation анализ корректен
- [ ] БД хранит историю правильно
- [ ] Обновление происходит ежедневно

### Для Hashtag Research ✅
- [ ] Поиск работает <1сек
- [ ] Difficulty score вычисляется правильно
- [ ] Рекомендации логичны
- [ ] Related hashtags корректны
- [ ] Сохранение в favorites работает

---

## 9. ДОПОЛНИТЕЛЬНЫЕ ТРЕБОВАНИЯ

### 9.1 Performance
- First paint: <2s
- Time to interactive: <3s
- Lighthouse score: >80

### 9.2 Security
- API ключи в .env
- Rate limiting (100 req/min)
- Data encryption (sensitive info)

### 9.3 Analytics
- Track user interactions
- Log API calls
- Monitor errors

### 9.4 Documentation
- API docs (Swagger)
- User guide (PDF)
- Video tutorial (3 мин)

---

## 10. КОНТАКТЫ И ВОПРОСЫ

**Заказчик:** Артур Киселев (@KISELEVY_CREO)  
**Email:** Dj.mr.fobs@gmail.com  
**Telegram:** @KISELEVY_CREO  

---

**Подготовлено:** Нейро (AI Assistant)  
**Дата:** 15.07.2026
