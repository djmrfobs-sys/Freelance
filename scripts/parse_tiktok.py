#!/usr/bin/env python3
"""
TikTok парсер через Selenium + Chromium.
Использование: python3 parse_tiktok.py <username>
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
import json

def parse_tiktok_profile(username: str):
    """Парсит профиль TikTok"""
    
    # Опции Chromium (headless режим)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        # Загружаем профиль
        url = f"https://www.tiktok.com/@{username}"
        driver.get(url)
        time.sleep(8)  # Даём странице загрузиться (TikTok медленнее)
        
        data = {
            'username': username,
            'url': url,
            'followers': None,
            'following': None,
            'likes': None,
            'bio': None,
            'name': None,
            'verified': False,
            'avatar': None,
        }
        
        # Парсим имя
        try:
            name_elem = driver.find_element(By.XPATH, "//h1[@data-e2e='user-title']")
            data['name'] = name_elem.text
        except:
            pass
        
        # Парсим био
        try:
            bio_elem = driver.find_element(By.XPATH, "//h2[@data-e2e='user-bio']")
            data['bio'] = bio_elem.text
        except:
            pass
        
        # Парсим статистику
        try:
            stats = driver.find_elements(By.XPATH, "//strong[@data-e2e='user-stat']")
            if len(stats) >= 3:
                # Формат: [следующие, следующие, нравится]
                data['following'] = stats[0].text.split()[0]
                data['followers'] = stats[1].text.split()[0]
                data['likes'] = stats[2].text.split()[0]
        except:
            pass
        
        # Проверяем галочку верификации
        try:
            verify = driver.find_element(By.XPATH, "//*[@data-e2e='user-verified']")
            data['verified'] = True
        except:
            data['verified'] = False
        
        # Парсим аватар
        try:
            avatar = driver.find_element(By.XPATH, "//img[@alt='user-avatar']")
            data['avatar'] = avatar.get_attribute('src')
        except:
            pass
        
        return data
        
    except Exception as e:
        return {'error': str(e), 'username': username}
        
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: parse_tiktok.py <username>")
        sys.exit(1)
    
    result = parse_tiktok_profile(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
