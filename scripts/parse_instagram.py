#!/usr/bin/env python3
"""
Instagram парсер через Selenium + Chromium.
Использование: python3 parse_instagram.py <username>
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys

def parse_instagram_profile(username: str):
    """Парсит профиль Instagram"""
    
    # Опции Chromium (headless режим)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Загружаем профиль
        url = f"https://www.instagram.com/{username}/"
        driver.get(url)
        time.sleep(5)  # Даём странице загрузиться
        
        # Ищем информацию
        data = {
            'username': username,
            'url': url,
            'followers': None,
            'following': None,
            'posts': None,
            'bio': None,
            'name': None,
        }
        
        # Парсим имя
        try:
            name_elem = driver.find_element(By.XPATH, "//h1")
            data['name'] = name_elem.text
        except:
            pass
        
        # Парсим био
        try:
            bio_elem = driver.find_element(By.XPATH, "//span[@data-needs-padding]")
            data['bio'] = bio_elem.text
        except:
            pass
        
        # Парсим статистику
        try:
            stats = driver.find_elements(By.XPATH, "//span[contains(@class, 'html-span')]")
            if len(stats) >= 3:
                data['posts'] = stats[0].text
                data['followers'] = stats[1].text
                data['following'] = stats[2].text
        except:
            pass
        
        return data
        
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_instagram.py <username>")
        sys.exit(1)
    
    result = parse_instagram_profile(sys.argv[1])
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
