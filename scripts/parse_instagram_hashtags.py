#!/usr/bin/env python3
"""
Instagram Hashtag Scraper — парсим данные о хештегах.
Использование: python3 parse_instagram_hashtags.py <hashtag>
"""

from apify_client import ApifyClient
import json
import sys
import os

def scrape_hashtags(hashtag: str, limit: int = 50):
    """Парсит данные о хештеге в Instagram"""
    
    api_key_file = os.path.expanduser("~/.openclaw-neuro/.apify_key")
    with open(api_key_file) as f:
        api_key = f.read().strip()
    
    client = ApifyClient(api_key)
    
    # Убираем # если есть
    hashtag = hashtag.lstrip('#')
    
    run_input = {
        "hashtags": [hashtag],
        "resultsLimit": limit,
    }
    
    print(f"🔍 Парсим хештег #{hashtag}...", file=sys.stderr)
    
    run = client.actor("apify/instagram-hashtag-scraper").call(run_input=run_input)
    
    dataset_client = client.dataset(run.get("defaultDatasetId"))
    items = dataset_client.list_items().items if dataset_client else []
    
    # Анализируем данные
    analysis = {
        'hashtag': hashtag,
        'posts_count': len(items),
        'hashtag_stats': {},
        'top_posts': [],
        'recommendations': [],
    }
    
    if items:
        # Рассчитываем среднее engagement
        likes_list = [p.get('likesCount', 0) for p in items]
        comments_list = [p.get('commentsCount', 0) for p in items]
        
        analysis['hashtag_stats'] = {
            'avg_likes': round(sum(likes_list) / len(likes_list), 1) if likes_list else 0,
            'avg_comments': round(sum(comments_list) / len(comments_list), 1) if comments_list else 0,
        }
        
        # Топ посты по этому хештегу
        top_posts = sorted(items, key=lambda x: x.get('likesCount', 0) + x.get('commentsCount', 0), reverse=True)[:5]
        analysis['top_posts'] = [
            {
                'caption': p.get('caption', '')[:100],
                'likes': p.get('likesCount'),
                'comments': p.get('commentsCount'),
            }
            for p in top_posts
        ]
        
        # Рекомендации
        if analysis['hashtag_stats']['avg_likes'] > 1000:
            analysis['recommendations'].append("✅ Популярный хештег, используй его!")
        elif analysis['hashtag_stats']['avg_likes'] < 100:
            analysis['recommendations'].append("⚠️ Нишевый хештег, добавь посты с большим охватом")
        else:
            analysis['recommendations'].append("✓ Хороший хештег для роста")
    
    result = {
        'hashtag': hashtag,
        'analysis': analysis,
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_hashtags.py <hashtag> [limit]")
        sys.exit(1)
    
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    result = scrape_hashtags(sys.argv[1], limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
