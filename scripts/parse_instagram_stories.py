#!/usr/bin/env python3
"""
Instagram Story Scraper — парсим stories профиля.
Использование: python3 parse_instagram_stories.py <username>
"""

from apify_client import ApifyClient
import json
import sys
import os

def scrape_stories(username: str):
    """Парсит stories Instagram профиля"""
    
    api_key_file = os.path.expanduser("~/.openclaw-neuro/.apify_key")
    with open(api_key_file) as f:
        api_key = f.read().strip()
    
    client = ApifyClient(api_key)
    
    run_input = {
        "username": username,
    }
    
    print(f"🔍 Парсим stories @{username}...", file=sys.stderr)
    
    run = client.actor("apify/instagram-story-scraper").call(run_input=run_input)
    
    dataset_client = client.dataset(run.get("defaultDatasetId"))
    items = dataset_client.list_items().items if dataset_client else []
    
    # Анализируем stories
    analysis = {
        'username': username,
        'total_stories': len(items),
        'stories_analysis': {
            'interactive_stories': 0,  # С опросами, вопросами
            'video_stories': 0,  # Видео
            'image_stories': 0,  # Картинки
            'story_types': {},
        },
        'stories': items,
    }
    
    if items:
        for story in items:
            story_type = story.get('type', 'unknown')
            analysis['stories_analysis']['story_types'][story_type] = analysis['stories_analysis']['story_types'].get(story_type, 0) + 1
            
            # Считаем интерактивные
            if story.get('hasInteractiveElements'):
                analysis['stories_analysis']['interactive_stories'] += 1
            
            # Считаем видео и картинки
            if story_type == 'video':
                analysis['stories_analysis']['video_stories'] += 1
            elif story_type == 'image':
                analysis['stories_analysis']['image_stories'] += 1
    
    result = {
        'username': username,
        'analysis': analysis,
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_stories.py <username>")
        sys.exit(1)
    
    result = scrape_stories(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
