#!/usr/bin/env python3
"""
Instagram Comments Scraper — парсим комментарии под постами.
Использование: python3 parse_instagram_comments.py <post_url>
"""

from apify_client import ApifyClient
import json
import sys
import os

def scrape_comments(post_url: str, limit: int = 500):
    """Парсит комментарии под Instagram постом"""
    
    api_key_file = os.path.expanduser("~/.openclaw-neuro/.apify_key")
    with open(api_key_file) as f:
        api_key = f.read().strip()
    
    client = ApifyClient(api_key)
    
    run_input = {
        "postUrls": [post_url],
        "resultsLimit": limit,
    }
    
    print(f"🔍 Парсим комментарии...", file=sys.stderr)
    
    run = client.actor("apify/instagram-comments-scraper").call(run_input=run_input)
    
    dataset_client = client.dataset(run.get("defaultDatasetId"))
    items = dataset_client.list_items().items if dataset_client else []
    
    # Анализируем комментарии
    analysis = {
        'total_comments': len(items),
        'engagement_analysis': {
            'avg_likes_per_comment': 0,
            'sentiment_triggers': [],
            'top_commenters': [],
        },
        'comments': items[:100],  # Первые 100
    }
    
    if items:
        # Рассчитываем среднее лайков
        likes = [c.get('likesCount', 0) for c in items]
        analysis['engagement_analysis']['avg_likes_per_comment'] = sum(likes) / len(likes) if likes else 0
        
        # Ищем топ комментаторов
        from collections import Counter
        authors = [c.get('ownerUsername') for c in items if c.get('ownerUsername')]
        analysis['engagement_analysis']['top_commenters'] = Counter(authors).most_common(10)
    
    result = {
        'post_url': post_url,
        'analysis': analysis,
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_comments.py <post_url> [limit]")
        sys.exit(1)
    
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    result = scrape_comments(sys.argv[1], limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
