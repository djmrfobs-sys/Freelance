#!/usr/bin/env python3
"""
ПОЛНЫЙ АНАЛИЗ INSTAGRAM АККАУНТА — использует все скраперы.
Использование: python3 parse_instagram_full.py <username>
"""

import subprocess
import json
import sys
import os

def run_scraper(script_name: str, *args):
    """Запускает скрипт скрапера и возвращает результат"""
    try:
        cmd = [sys.executable, f"/root/.openclaw/workspace-neuro/scripts/{script_name}.py"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            # Извлекаем JSON из вывода (пропускаем stderr)
            output_lines = result.stdout.strip().split('\n')
            json_start = -1
            for i, line in enumerate(output_lines):
                if line.startswith('{'):
                    json_start = i
                    break
            if json_start >= 0:
                return json.loads('\n'.join(output_lines[json_start:]))
        return None
    except Exception as e:
        print(f"Error running {script_name}: {e}", file=sys.stderr)
        return None

def analyze_instagram_full(username: str):
    """Полный анализ Instagram аккаунта"""
    
    print(f"🔍 Начинаю полный анализ @{username}...\n", file=sys.stderr)
    
    report = {
        'username': username,
        'timestamp': __import__('datetime').datetime.now().isoformat(),
        'sections': {},
        'summary': {},
    }
    
    # 1. Основной профиль
    print("📊 Шаг 1/5: Профиль и посты...", file=sys.stderr)
    profile = run_scraper("parse_instagram_apify", username)
    if profile:
        report['sections']['profile'] = profile
    
    # 2. Stories
    print("📱 Шаг 2/5: Stories...", file=sys.stderr)
    stories = run_scraper("parse_instagram_stories", username)
    if stories:
        report['sections']['stories'] = stories
    
    # 3. Followers (берем топ 200)
    print("👥 Шаг 3/5: Подписчики...", file=sys.stderr)
    followers = run_scraper("parse_instagram_followers", username, "200")
    if followers:
        report['sections']['followers'] = followers
    
    # 4. Хештеги (парсим топ хештеги из постов)
    if profile and 'posts' in profile:
        top_hashtags = {}
        for post in profile.get('posts', [])[:20]:
            caption = post.get('caption', '')
            hashtags = [word for word in caption.split() if word.startswith('#')]
            for tag in hashtags[:5]:
                top_hashtags[tag] = top_hashtags.get(tag, 0) + 1
        
        if top_hashtags:
            print("🏷️ Шаг 4/5: Анализ хештегов...", file=sys.stderr)
            top_tag = max(top_hashtags, key=top_hashtags.get)
            hashtag_analysis = run_scraper("parse_instagram_hashtags", top_tag, "30")
            if hashtag_analysis:
                report['sections']['hashtags'] = hashtag_analysis
    
    # 5. Комментарии (парсим топ пост)
    if profile and 'posts' in profile:
        top_post = max(profile.get('posts', []), key=lambda x: x.get('likes', 0) + x.get('comments', 0), default=None)
        if top_post and top_post.get('url'):
            print("💬 Шаг 5/5: Анализ комментариев...", file=sys.stderr)
            comments = run_scraper("parse_instagram_comments", top_post['url'], "200")
            if comments:
                report['sections']['comments'] = comments
    
    # Составляем сводку
    print("📝 Составляю итоговый отчёт...\n", file=sys.stderr)
    
    if 'profile' in report['sections'] and report['sections']['profile'].get('profile_info'):
        profile_info = report['sections']['profile']['profile_info']
        stats = report['sections']['profile'].get('statistics', {})
        
        report['summary'] = {
            'name': profile_info.get('name'),
            'bio': profile_info.get('bio'),
            'followers': profile_info.get('followers'),
            'following': profile_info.get('following'),
            'total_posts_analyzed': stats.get('total_posts'),
            'avg_engagement_per_post': {
                'likes': stats.get('avg_likes'),
                'comments': stats.get('avg_comments'),
            },
        }
        
        # Добавляем insights
        if 'stories' in report['sections']:
            stories_data = report['sections']['stories'].get('analysis', {})
            report['summary']['stories_insights'] = {
                'total_stories': stories_data.get('total_stories'),
                'interactive_stories': stories_data.get('interactive_stories'),
            }
        
        if 'hashtags' in report['sections']:
            hashtag_data = report['sections']['hashtags'].get('analysis', {})
            report['summary']['top_hashtag_insights'] = hashtag_data.get('hashtag_stats')
    
    return report

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_full.py <username>")
        sys.exit(1)
    
    result = analyze_instagram_full(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
