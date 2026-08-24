#!/usr/bin/env python3
"""
YouTube парсер через yt-dlp.
Использование: python3 parse_youtube.py <URL или канал>
"""

import yt_dlp
import json
import sys

def parse_youtube_video(url: str):
    """Парсит видео YouTube"""
    
    ydl_opts = {
        'quiet': False,
        'no_warnings': False,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        data = {
            'title': info.get('title'),
            'channel': info.get('channel'),
            'duration': info.get('duration'),
            'views': info.get('view_count'),
            'likes': info.get('like_count'),
            'upload_date': info.get('upload_date'),
            'description': info.get('description'),
            'tags': info.get('tags', []),
            'thumbnail': info.get('thumbnail'),
            'url': url,
        }
        
        return data

def parse_youtube_channel(channel_url: str):
    """Парсит информацию о канале"""
    
    ydl_opts = {
        'quiet': False,
        'extract_flat': 'in_playlist',
        'playlistend': 10,  # Первые 10 видео
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_url, download=False)
        
        videos = []
        for entry in info.get('entries', []):
            videos.append({
                'title': entry.get('title'),
                'url': entry.get('url'),
                'id': entry.get('id'),
            })
        
        return {
            'channel': info.get('title'),
            'url': channel_url,
            'videos': videos,
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_youtube.py <video_url_or_channel_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    # Определяем тип URL
    if '/channel/' in url or '/c/' in url or '/@' in url:
        result = parse_youtube_channel(url)
    else:
        result = parse_youtube_video(url)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
