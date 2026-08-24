#!/usr/bin/env python3
"""
INSTAGRAM ПАРСЕР через APIFY — быстрый и мощный.
Использование: python3 parse_instagram_apify.py <username>
"""

from apify_client import ApifyClient
import json
import sys
import os

def parse_instagram_apify(username: str):
    """Парсит Instagram профиль через Apify"""
    
    # Читаем API ключ
    api_key_file = os.path.expanduser("~/.openclaw-neuro/.apify_key")
    with open(api_key_file) as f:
        api_key = f.read().strip()
    
    # Инициализируем Apify клиент
    client = ApifyClient(api_key)
    
    # Параметры для Instagram Scraper
    run_input = {
        "usernames": [username],
        "searchType": "user",
        "resultsLimit": 50,  # Получаем до 50 постов
    }
    
    print(f"🔍 Парсим {username}...", file=sys.stderr)
    
    # Запускаем актора
    run = client.actor("apify/instagram-scraper").call(run_input=run_input)
    
    # Получаем результаты
    dataset_client = client.dataset(run.get("defaultDatasetId"))
    items = dataset_client.list_items().items if dataset_client else []
    
    # Обработка результатов
    profile_data = {
        'username': username,
        'profile_info': {},
        'posts': [],
        'statistics': {
            'total_posts': 0,
            'avg_likes': 0,
            'avg_comments': 0,
            'total_followers': 0,
            'total_following': 0,
        },
        'content_analysis': {
            'most_common_type': None,
            'top_hooks': [],
            'best_engagement_posts': [],
        }
    }
    
    if items and len(items) > 0:
        # Первый элемент это информация о профиле
        profile = items[0]
        
        profile_data['profile_info'] = {
            'name': profile.get('name'),
            'bio': profile.get('biography'),
            'followers': profile.get('followersCount'),
            'following': profile.get('followingCount'),
            'url': profile.get('url'),
            'verified': profile.get('verified'),
            'profile_pic_url': profile.get('profilePicUrl'),
        }
        
        profile_data['statistics']['total_followers'] = profile.get('followersCount', 0)
        profile_data['statistics']['total_following'] = profile.get('followingCount', 0)
        
        # Остальные элементы это посты
        posts = items[1:] if len(items) > 1 else []
        profile_data['statistics']['total_posts'] = len(posts)
        
        likes_list = []
        comments_list = []
        
        for post in posts:
            post_data = {
                'id': post.get('id'),
                'caption': post.get('caption'),
                'type': post.get('type'),  # IMAGE, VIDEO, CAROUSEL
                'likes': post.get('likesCount', 0),
                'comments': post.get('commentsCount', 0),
                'timestamp': post.get('timestamp'),
                'url': post.get('url'),
            }
            
            profile_data['posts'].append(post_data)
            likes_list.append(post_data['likes'])
            comments_list.append(post_data['comments'])
        
        # Рассчитываем среднее
        if likes_list:
            profile_data['statistics']['avg_likes'] = round(sum(likes_list) / len(likes_list), 1)
        if comments_list:
            profile_data['statistics']['avg_comments'] = round(sum(comments_list) / len(comments_list), 1)
        
        # Анализируем контент
        type_counts = {}
        for post in posts:
            post_type = post.get('type', 'UNKNOWN')
            type_counts[post_type] = type_counts.get(post_type, 0) + 1
        
        if type_counts:
            profile_data['content_analysis']['most_common_type'] = max(type_counts, key=type_counts.get)
        
        # Топ посты по engagement
        top_posts = sorted(posts, key=lambda x: x.get('likesCount', 0) + x.get('commentsCount', 0), reverse=True)[:5]
        profile_data['content_analysis']['best_engagement_posts'] = [
            {
                'caption': p.get('caption', '')[:100],
                'likes': p.get('likesCount'),
                'comments': p.get('commentsCount'),
                'type': p.get('type'),
            }
            for p in top_posts
        ]
    
    return profile_data

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_apify.py <username>")
        sys.exit(1)
    
    result = parse_instagram_apify(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
