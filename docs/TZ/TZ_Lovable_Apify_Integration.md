# ТЕХНИЧЕСКОЕ ЗАДАНИЕ
## "Insta Navigator AI" — Интеграция Apify Store скраперов

**Дата:** 15.07.2026  
**Версия:** 2.1 (с Apify интеграцией)  
**Статус:** В разработку

---

## 1. ОБЗОР ИНТЕГРАЦИИ

### Цель
Интегрировать **6 лучших скраперов из Apify Store** в существующую систему "Insta Navigator AI" для расширенного анализа Instagram.

### Текущие Apify скраперы (уже интегрированы)
```
✅ Instagram Scraper (основной — профиль + посты)
✅ Instagram Followers Scraper
✅ Instagram Comments Scraper
✅ Instagram Hashtag Scraper
✅ Instagram Story Scraper
✅ Instagram Full Parser (все 5 вместе)
```

### Новые скраперы для интеграции (ТОП 6 из Store)
1. **Instagram Mentions Scraper** — кто упоминает профиль?
2. **Instagram Reels Scraper** — отдельный анализ Reels
3. **Instagram User Info Scraper** — глубокий анализ юзера
4. **Instagram Location Scraper** — анализ по геолокации
5. **TikTok Scraper** — анализ TikTok аккаунтов
6. **YouTube Channel Scraper** — анализ YouTube каналов

---

## 2. МОДУЛИ ИНТЕГРАЦИИ

### 2.1 Tavily (Свежие данные) → Расширить

#### Текущее
```
- Общая информация об аккаунте
- Свежие Reels тренды
- Анализ контента
```

#### Новое (добавить)
```
┌──────────────────────────────────┐
│  TAVILY v2.0 (Enhanced)          │
├──────────────────────────────────┤
│                                  │
│ 1️⃣ MENTIONS TRACKER             │
│   └─ Где упоминают аккаунт?     │
│   └─ Sentiment analysis          │
│   └─ Influencer mentions         │
│                                  │
│ 2️⃣ REELS DEEP DIVE              │
│   └─ Views per reel              │
│   └─ Watch time analysis         │
│   └─ Best performing reels       │
│                                  │
│ 3️⃣ COMPETITOR INTEL             │
│   └─ Top 3 конкурента            │
│   └─ Их лучшие посты             │
│   └─ Их хештеги                  │
│                                  │
│ 4️⃣ LOCATION INSIGHTS            │
│   └─ Географический анализ       │
│   └─ Regional trends             │
│   └─ Location-based engagement   │
└──────────────────────────────────┘
```

#### API Интеграция
```javascript
// Mentions Scraper
{
  "username": "kiselevy_creo",
  "type": "mentions"
}

// Reels Detailed
{
  "username": "kiselevy_creo",
  "type": "reels_only",
  "metrics": ["views", "shares", "saves"]
}

// Competitor Analysis
{
  "username": "kiselevy_creo",
  "type": "competitor_find",
  "niche": "vibe_coding"
}

// Location Scraper
{
  "location_id": "123456",
  "type": "location_posts"
}
```

---

### 2.2 InstaProducer AI (Поиск + Создание) → Расширить

#### Текущее
```
- Поиск аккаунтов по нише
- Создание Reels сценариев
- Идеи контента
```

#### Новое (добавить)
```
┌──────────────────────────────────┐
│  INSTAPRODUCER AI v2.0           │
├──────────────────────────────────┤
│                                  │
│ 📍 FIND ACCOUNTS                 │
│   ├─ By niche (через Mentions)   │
│   ├─ By location (через Location)│
│   ├─ By engagement (через Reels) │
│   └─ Competitor accounts         │
│                                  │
│ 🎬 ANALYZE REELS                 │
│   ├─ What makes them viral?      │
│   ├─ Hook techniques             │
│   ├─ Music & transitions         │
│   └─ Best reels templates        │
│                                  │
│ 📊 GET INSIGHTS                  │
│   ├─ Optimal posting time        │
│   ├─ Best content type           │
│   ├─ Engagement multipliers      │
│   └─ Growth predictions          │
│                                  │
│ 🎯 CREATE CONTENT                │
│   ├─ Based on top performers     │
│   ├─ AI suggestions              │
│   ├─ Hashtag recommendations     │
│   └─ Caption templates           │
└──────────────────────────────────┘
```

#### API Интеграция
```javascript
// Find competitors
{
  "type": "find_competitors",
  "niche": "photography",
  "limit": 5,
  "metrics": ["followers", "engagement"]
}

// Analyze reels
{
  "type": "analyze_reels",
  "username": "competitor_account",
  "depth": "detailed"
}

// Get insights
{
  "type": "get_insights",
  "username": "kiselevy_creo",
  "period": 30
}
```

---

### 2.3 Strategist (Стратегия) → Расширить

#### Новое (добавить раздел)
```
┌──────────────────────────────────┐
│  COMPETITOR STRATEGY MODULE      │
├──────────────────────────────────┤
│                                  │
│ 🎯 ANALYZE COMPETITORS           │
│   ├─ Top 5 в нише               │
│   ├─ Их контент-стратегия       │
│   ├─ Их posting schedule        │
│   ├─ Их engagement rate         │
│   └─ Их growth trajectory       │
│                                  │
│ 📊 BENCHMARK ANALYSIS           │
│   ├─ Сравнение с ними          │
│   ├─ Gap analysis               │
│   ├─ Opportunities              │
│   └─ Threats                    │
│                                  │
│ 💡 RECOMMENDATIONS              │
│   ├─ What to copy               │
│   ├─ What to improve            │
│   ├─ New trends to adopt        │
│   └─ Content gaps to fill       │
└──────────────────────────────────┘
```

#### SQL Schema
```sql
CREATE TABLE competitor_analysis (
  id PRIMARY KEY,
  username VARCHAR(255),
  competitor_username VARCHAR(255),
  followers INT,
  engagement_rate FLOAT,
  avg_likes INT,
  top_posts JSON,
  content_strategy TEXT,
  posting_frequency INT,
  collected_at TIMESTAMP
)
```

---

### 2.4 Multi-Channel (Новый модуль)

#### TikTok Integration
```javascript
// TikTok Scraper
{
  "username": "kiselevy_creo_tiktok",
  "metrics": [
    "followers",
    "views",
    "engagement_rate",
    "best_videos"
  ]
}

RESPONSE:
{
  "followers": 15200,
  "total_views": 520000,
  "engagement_rate": "12.5%",
  "avg_likes": 1890,
  "top_video": {
    "views": 45000,
    "likes": 5200,
    "comments": 320,
    "shares": 890
  }
}
```

#### YouTube Integration
```javascript
// YouTube Channel Scraper
{
  "channel_id": "UCxxxxx",
  "metrics": [
    "subscribers",
    "views",
    "video_stats",
    "upload_frequency"
  ]
}

RESPONSE:
{
  "subscribers": 8500,
  "total_channel_views": 1200000,
  "videos": 145,
  "avg_views_per_video": 8275,
  "best_video": {
    "title": "...",
    "views": 125000,
    "likes": 8900
  }
}
```

---

## 3. APIFY API ENDPOINTS

### 3.1 Scraper URLs (все используют Apify)
```
apify/instagram-scraper
apify/instagram-followers-scraper
apify/instagram-comments-scraper
apify/instagram-hashtag-scraper
apify/instagram-story-scraper
apify/instagram-mentions-scraper (новое)
apify/instagram-reels-scraper (новое)
apify/tiktok-scraper (новое)
apify/youtube-scraper (новое)
```

### 3.2 Authentication
```javascript
const client = ApifyClient(apiKey: "apify_…9u8e")

// Параметры запроса (универсальные):
{
  "apiToken": "apify_…9u8e",
  "username": "kiselevy_creo",
  "resultsLimit": 50,
  "fields": ["engagement", "metadata", "metrics"]
}
```

### 3.3 Response Format (стандартный для всех)
```json
{
  "profile": {
    "username": "kiselevy_creo",
    "followers": 2534,
    "following": 340,
    "bio": "...",
    "verified": false
  },
  "content": [
    {
      "id": "abc123",
      "type": "reel",
      "caption": "...",
      "likes": 340,
      "comments": 12,
      "shares": 45,
      "saves": 120,
      "timestamp": "2026-07-15"
    }
  ],
  "analytics": {
    "engagement_rate": 8.2,
    "avg_likes": 340,
    "avg_comments": 12
  }
}
```

---

## 4. UI СТРУКТУРА (обновленная)

```
┌──────────────────────────────────────────────────┐
│             INSTA NAVIGATOR AI v2.0              │
├──────┬───────────────────────────────────────────┤
│      │                                            │
│ 🏠   │ Home (Dashboard + все метрики)            │
│      │                                            │
│ 🌐   │ Tavily ENHANCED                           │
│ MENU │   ├─ Mentions Tracker                     │
│      │   ├─ Reels Deep Dive                      │
│      │   ├─ Competitor Intel                     │
│      │   └─ Location Insights                    │
│      │                                            │
│ 📋   │ Strategist ENHANCED                       │
│      │   └─ Competitor Strategy Module           │
│      │                                            │
│ 💰   │ Accountant                                │
│      │                                            │
│ 🎬   │ InstaProducer AI ENHANCED                 │
│      │   ├─ Find Accounts (by niche)            │
│      │   ├─ Analyze Reels                       │
│      │   ├─ Get Insights                        │
│      │   └─ Create Content                      │
│      │                                            │
│ 🌍   │ MultiChannel (НОВОЕ)                      │
│      │   ├─ TikTok Analytics                    │
│      │   ├─ YouTube Analytics                   │
│      │   └─ Cross-platform comparison           │
│      │                                            │
│ 📊   │ Analytics Dashboard                       │
│      │   ├─ Growth Charts                       │
│      │   ├─ Engagement Trends                   │
│      │   └─ Forecasting                         │
│      │                                            │
└──────┴───────────────────────────────────────────┘
```

---

## 5. РАСШИРЕННЫЕ ФУНКЦИИ

### 5.1 Mentions Tracker (детально)
```
Input: Username
Output:
┌────────────────────────────────┐
│ MENTIONS FOUND: 347             │
├────────────────────────────────┤
│ ✅ Positive mentions: 289 (83%) │
│ 😐 Neutral: 45 (13%)           │
│ ❌ Negative: 13 (4%)           │
├────────────────────────────────┤
│ TOP MENTIONS:                  │
│ 1. @influencer1 (12 mentions) │
│ 2. @partner_account (8)        │
│ 3. @fan_account (5)            │
├────────────────────────────────┤
│ TRENDS:                         │
│ - "kiselevy_creo лучший" ↑     │
│ - "вайбкодинг от @kiselevy" ↑ │
│ - "красивый контент" →         │
└────────────────────────────────┘
```

### 5.2 Reels Deep Dive (детально)
```
Input: Username
Output:
┌────────────────────────────────┐
│ TOP PERFORMING REELS            │
├────────────────────────────────┤
│ 1. "Вайбкодинг туториал"      │
│    Views: 45,000 ↑             │
│    Engagement: 12.5%           │
│    Hook: Question (0-1 sec)    │
│    Music: Electronic pop       │
│    Duration: 28 sec            │
│    Best watch time: 18 sec     │
│                                │
│ 2. "За кулисами"             │
│    Views: 32,000              │
│    Engagement: 9.2%           │
│    Hook: Curiosity            │
│    Music: Lo-fi beats         │
│    Duration: 35 sec           │
│    Best watch time: 22 sec    │
│                                │
│ RECOMMENDATIONS:               │
│ ✓ Используй question hooks    │
│ ✓ Музыка electronic/lo-fi     │
│ ✓ Длина 25-35 сек            │
│ ✓ Оптимум при 18-22 сек      │
└────────────────────────────────┘
```

### 5.3 Competitor Analysis (детально)
```
Input: Your username
Output:
┌────────────────────────────────┐
│ TOP 3 COMPETITORS (в нише)     │
├────────────────────────────────┤
│ 🥇 @competitor1                │
│    Followers: 15K (+45% vs)   │
│    Engagement: 12.5% (+50%)   │
│    Best content: Tutorials    │
│    Posting: Mon-Fri, 18:00   │
│    Growth: +150/day            │
│                                │
│ 🥈 @competitor2                │
│    Followers: 8.5K (-20% vs)  │
│    Engagement: 6.2% (-30%)    │
│    Best content: Behind-scenes│
│    Posting: Daily random      │
│    Growth: +30/day             │
│                                │
│ 🥉 @competitor3                │
│    Followers: 4.2K (-80% vs)  │
│    Engagement: 4.1% (-50%)    │
│    Best content: Trending     │
│    Posting: 3x per week       │
│    Growth: +5/day              │
│                                │
│ YOUR POSITION: #2 (emerging)   │
│ Potential: 1st place (3-4 мес) │
└────────────────────────────────┘
```

---

## 6. ТЕХНИЧЕСКИЕ ТРЕБОВАНИЯ

### 6.1 API Quotas (Apify)
```
Free tier:
- 50 запусков в месяц (на все скраперы)
- 500 результатов в месяц
- Апдейты раз в неделю

Paid tier (рекомендуемо):
- Unlimited запусков
- Ежедневные апдейты
- Priority support
- Custom integrations

СТОИМОСТЬ: $30-100/месяц (зависит от использования)
```

### 6.2 Database Schema (расширенная)
```sql
-- Основные таблицы (существуют)
CREATE TABLE instagram_profiles (...)
CREATE TABLE instagram_posts (...)
CREATE TABLE instagram_comments (...)
CREATE TABLE hashtag_data (...)

-- Новые таблицы (добавить)
CREATE TABLE instagram_mentions (
  id PRIMARY KEY,
  username VARCHAR(255),
  mention_from VARCHAR(255),
  caption TEXT,
  sentiment VARCHAR(20), -- positive/neutral/negative
  collected_at TIMESTAMP
)

CREATE TABLE instagram_reels_analytics (
  id PRIMARY KEY,
  reels_id VARCHAR(255),
  username VARCHAR(255),
  views INT,
  average_watch_time INT, -- in seconds
  hook_type VARCHAR(50), -- question/emotion/action/curiosity
  music_genre VARCHAR(100),
  duration INT,
  collected_at TIMESTAMP
)

CREATE TABLE competitor_tracking (
  id PRIMARY KEY,
  username VARCHAR(255),
  competitor_username VARCHAR(255),
  followers INT,
  engagement_rate FLOAT,
  content_strategy TEXT,
  posting_schedule JSON,
  growth_rate FLOAT, -- followers/day
  last_updated TIMESTAMP
)

CREATE TABLE tiktok_analytics (
  id PRIMARY KEY,
  tiktok_username VARCHAR(255),
  followers INT,
  total_likes INT,
  total_views BIGINT,
  engagement_rate FLOAT,
  avg_likes_per_video INT,
  top_video_id VARCHAR(255),
  collected_at TIMESTAMP
)

CREATE TABLE youtube_analytics (
  id PRIMARY KEY,
  channel_id VARCHAR(255),
  subscribers INT,
  total_views BIGINT,
  total_videos INT,
  avg_views_per_video INT,
  upload_frequency INT, -- videos per week
  best_video_id VARCHAR(255),
  collected_at TIMESTAMP
)
```

### 6.3 Cron Jobs (автоматизация)
```
Daily (09:00 UTC):
  └─ fetch_instagram_profile()
  └─ fetch_instagram_posts()
  └─ calculate_engagement_metrics()

Weekly (Monday 00:00 UTC):
  └─ fetch_competitor_data()
  └─ analyze_reels_performance()
  └─ generate_weekly_report()

Monthly (1st day 00:00 UTC):
  └─ fetch_tiktok_analytics()
  └─ fetch_youtube_analytics()
  └─ generate_monthly_strategy()
```

---

## 7. ПРИОРИТИЗАЦИЯ ВНЕДРЕНИЯ

### ФАЗА 1 (НЕДЕЛЯ 1-2): КРИТИЧНОЕ
```
☑ Mentions Tracker (Tavily)
☑ Reels Deep Dive (InstaProducer)
☑ Dashboard Analytics
```
**Время:** 10 дней  
**Ценность:** 🔥🔥🔥 Критично

### ФАЗА 2 (НЕДЕЛЯ 3): ВАЖНОЕ
```
☑ Competitor Analysis (Strategist)
☑ Location Insights (Tavily)
☑ Growth Tracker
```
**Время:** 5 дней  
**Ценность:** 🔥🔥 Важно

### ФАЗА 3 (НЕДЕЛЯ 4-5): РАСШИРЕНИЕ
```
☑ TikTok Analytics (MultiChannel)
☑ YouTube Analytics (MultiChannel)
☑ Cross-platform Dashboard
```
**Время:** 7 дней  
**Ценность:** 🔥 Улучшение

---

## 8. СМЕТЧ РАЗВЕРТЫВАНИЯ

| Компонент | Время | Статус |
|-----------|-------|--------|
| Mentions Tracker | 2 дня | To-Do |
| Reels Analytics | 3 дня | To-Do |
| Dashboard | 4 дня | To-Do |
| Competitor Module | 3 дня | To-Do |
| Location Insights | 2 дня | To-Do |
| TikTok Integration | 3 дня | To-Do |
| YouTube Integration | 3 дня | To-Do |
| Testing & QA | 4 дня | To-Do |
| Deployment | 1 день | To-Do |
| **ИТОГО** | **25 дней** | - |

---

## 9. УСПЕШНОСТЬ (Success Metrics)

### Dashboard
- ✅ Все графики загружаются <2сек
- ✅ Мобильная версия адаптивна
- ✅ Экспорт работает (PDF/CSV)
- ✅ Lighthouse score >85

### Mentions Tracker
- ✅ Находит все упоминания
- ✅ Sentiment анализ >90% точность
- ✅ Обновляется ежедневно
- ✅ UI интуитивен

### Competitor Analysis
- ✅ Анализирует топ конкурентов
- ✅ Сравнение корректно
- ✅ Рекомендации полезны
- ✅ Обновляется еженедельно

### Multi-Channel
- ✅ TikTok данные парсятся
- ✅ YouTube данные парсятся
- ✅ Cross-platform comparison работает
- ✅ Все источники синхронизированы

---

## 10. ДОКУМЕНТАЦИЯ

### 10.1 User Guides
- [ ] How to use Mentions Tracker
- [ ] How to analyze Reels
- [ ] Competitor analysis workflow
- [ ] Multi-channel setup

### 10.2 API Documentation
- [ ] Apify integration guide
- [ ] Database schema docs
- [ ] Webhook setup instructions
- [ ] Error handling guide

### 10.3 Video Tutorials
- [ ] 5-minute overview
- [ ] Dashboard walkthrough
- [ ] Competitor research guide
- [ ] Setting up alerts

---

## 11. BUDGET & RESOURCES

### Development
- Frontend: 50 hours ($1500)
- Backend/API: 60 hours ($1800)
- Database: 20 hours ($600)
- Testing: 20 hours ($600)
- **Total Dev:** 150 hours = **$4,500**

### Infrastructure (monthly)
- Apify API: $50
- Database hosting: $20
- Hosting: $30
- Monitoring: $10
- **Total/month:** **$110**

### Total Cost
- **Development:** $4,500 (one-time)
- **Monthly:** $110

---

## 12. КОНТАКТЫ

**Заказчик:** Артур Киселев (@KISELEVY_CREO)  
**Email:** Dj.mr.fobs@gmail.com  
**Telegram:** @KISELEVY_CREO  
**Сроки:** ASAP (25 дней)

---

**Подготовлено:** Нейро (AI Assistant)  
**Версия:** 2.1 с Apify интеграцией  
**Дата:** 15.07.2026
