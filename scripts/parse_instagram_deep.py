#!/usr/bin/env python3
"""
УГЛУБЛЕННЫЙ ПАРСИНГ INSTAGRAM — анализ структуры контента.
Использование: python3 parse_instagram_deep.py <username>
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import json
from datetime import datetime

def analyze_post_structure(driver, post_elem):
    """Анализирует структуру одного поста"""
    
    post_data = {
        'type': None,  # 'post', 'reel', 'story', 'carousel'
        'hook': None,  # Первый элемент (текст/изображение)
        'media_type': None,  # 'image', 'video', 'carousel'
        'caption': None,  # Текст описания
        'caption_structure': None,  # Как написан текст (hook + body + cta)
        'hashtags': [],
        'mentions': [],
        'cta': None,  # Call to action (если есть)
        'engagement': {
            'likes': None,
            'comments': None,
            'saves': None,
        },
        'metadata': {
            'date': None,
            'time_posted': None,
        },
        'hooks_detected': [],  # Какой hook использован (эмоция/вопрос/образ)
        'psychology': None,  # Психологический триггер
    }
    
    try:
        # Определяем тип контента
        if 'video' in post_elem.get_attribute('class') or post_elem.find_element(By.TAG_NAME, 'video'):
            post_data['media_type'] = 'video'
            # Анализируем видео (Reel)
            post_data['type'] = 'reel'
            # Парсим: длину, переходы, музыку (если доступно)
        else:
            post_elem.find_elements(By.XPATH, './/img[@alt]')
            if len(post_elem.find_elements(By.XPATH, './/img[@alt]')) > 1:
                post_data['type'] = 'carousel'
                post_data['media_type'] = 'carousel'
            else:
                post_data['type'] = 'post'
                post_data['media_type'] = 'image'
    except:
        post_data['type'] = 'unknown'
    
    try:
        # Извлекаем подпись (caption)
        caption_elem = post_elem.find_element(By.XPATH, './/span[@data-caption]')
        caption_text = caption_elem.text
        post_data['caption'] = caption_text
        
        # Анализируем структуру подписи
        lines = caption_text.split('\n')
        post_data['caption_structure'] = {
            'hook': lines[0] if lines else None,  # Первая строка (hook)
            'body': '\n'.join(lines[1:-1]) if len(lines) > 2 else None,  # Основной текст
            'cta': lines[-1] if lines else None,  # Последняя строка (CTA)
        }
        
        # Ищем хештеги
        hashtags = []
        for word in caption_text.split():
            if word.startswith('#'):
                hashtags.append(word)
        post_data['hashtags'] = hashtags
        
        # Ищем упоминания
        mentions = []
        for word in caption_text.split():
            if word.startswith('@'):
                mentions.append(word)
        post_data['mentions'] = mentions
        
        # Анализируем психологический триггер в hook'е
        hook = post_data['caption_structure']['hook'].lower()
        if any(word in hook for word in ['как', 'какой', 'почему', 'что если']):
            post_data['hooks_detected'].append('question')
            post_data['psychology'] = 'curiosity'
        elif any(word in hook for word in ['вау', 'OMG', 'ужас', 'шок', '😱']):
            post_data['hooks_detected'].append('emotion')
            post_data['psychology'] = 'emotional_response'
        elif any(word in hook for word in ['попробуй', 'нажми', 'смотри', 'читай']):
            post_data['hooks_detected'].append('action')
            post_data['psychology'] = 'urgency'
        elif any(word in hook for word in ['все', 'никто', 'каждый', '90%']):
            post_data['hooks_detected'].append('social_proof')
            post_data['psychology'] = 'social_proof'
            
    except:
        pass
    
    try:
        # Извлекаем метрики engagement
        engagement_elems = post_elem.find_elements(By.XPATH, './/span[@data-count]')
        if len(engagement_elems) >= 1:
            post_data['engagement']['likes'] = engagement_elems[0].text
        if len(engagement_elems) >= 2:
            post_data['engagement']['comments'] = engagement_elems[1].text
    except:
        pass
    
    return post_data

def parse_instagram_deep(username: str):
    """Глубокий парсинг профиля Instagram"""
    
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Загружаем профиль
        url = f"https://www.instagram.com/{username}/"
        driver.get(url)
        time.sleep(5)
        
        profile_data = {
            'username': username,
            'profile_info': {
                'name': None,
                'bio': None,
                'followers': None,
                'following': None,
                'posts_count': None,
            },
            'posts_analysis': [],
            'content_patterns': {
                'most_common_type': None,
                'avg_engagement': None,
                'top_hooks': [],
                'psychology_triggers': [],
                'best_performing_format': None,
            },
            'recommendations': [],
        }
        
        # Парсим профиль
        try:
            name = driver.find_element(By.XPATH, "//h1[@data-e2e='profile_name_header']")
            profile_data['profile_info']['name'] = name.text
        except:
            pass
        
        try:
            bio = driver.find_element(By.XPATH, "//h2[@data-e2e='profile_bio_header']")
            profile_data['profile_info']['bio'] = bio.text
        except:
            pass
        
        # Прокручиваем вниз и загружаем посты
        last_height = driver.execute_script("return document.body.scrollHeight")
        for _ in range(5):  # Скроллим 5 раз
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Парсим посты
        posts = driver.find_elements(By.XPATH, "//article[@data-e2e='post']")
        for post in posts[:10]:  # Первые 10 постов
            post_analysis = analyze_post_structure(driver, post)
            profile_data['posts_analysis'].append(post_analysis)
        
        # Анализируем паттерны
        if profile_data['posts_analysis']:
            # Какой тип контента популярнее?
            type_counts = {}
            for post in profile_data['posts_analysis']:
                post_type = post['type']
                type_counts[post_type] = type_counts.get(post_type, 0) + 1
            
            profile_data['content_patterns']['most_common_type'] = max(type_counts, key=type_counts.get)
            
            # Какие hooks работают?
            all_hooks = []
            for post in profile_data['posts_analysis']:
                all_hooks.extend(post['hooks_detected'])
            profile_data['content_patterns']['top_hooks'] = list(set(all_hooks))
            
            # Какие психологические триггеры?
            triggers = [p['psychology'] for p in profile_data['posts_analysis'] if p['psychology']]
            profile_data['content_patterns']['psychology_triggers'] = list(set(triggers))
        
        # Рекомендации
        if 'reel' in profile_data['content_patterns']['most_common_type']:
            profile_data['recommendations'].append('✅ Reels показывают хорошие результаты — продолжай')
        else:
            profile_data['recommendations'].append('⚠️ Попробуй добавить Reels (алгоритм их приоритизирует)')
        
        if 'carousel' in profile_data['content_patterns']['most_common_type']:
            profile_data['recommendations'].append('Карусели работают — используй их для storytelling')
        
        return profile_data
        
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram_deep.py <username>")
        sys.exit(1)
    
    result = parse_instagram_deep(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
