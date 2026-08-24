#!/usr/bin/env python3
"""
Instagram Followers Scraper — парсим подписчиков.
Использование: python3 parse_instagram_followers.py <username>
"""

from apify_client import ApifyClient
import json
import sys
import os

def scrape_followers(username: str, limit: int = 100):
    """Парсит подписчиков Instagram профиля"""
    
    api_key_file = os.path.expanduser("~/.openclaw-neuro/.apify_key")
    with open(api_key_file) as f:
        api_key = f.read().strip()
    
    client = ApifyClient(api_key)
    
    run_input = {
        "username": username,
        "resultsLimit": limit,
    }
    
    print(f"🔍 Парсим подписчиков @{username}...", file=sys.stderr)
    
    run = client.actor("apify/instagram-followers-scraper").call(run_input=run_input)
    
    dataset_client = client.dataset(run.get("defaultDatasetId"))
    items = dataset_client.list_items().items if dataset_client else []
    
    result = {
        'username': username,
        'followers_parsed': len(items),
        'followers': items,
    }
    
    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_followers.py <username> [limit]")
        sys.exit(1)
    
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    result = scrape_followers(sys.argv[1], limit)
    print(json.dumps(result, ensure_ascii=False, indent=2))
