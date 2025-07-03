import cloudscraper
import time
from bs4 import BeautifulSoup

scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'Edge'})
url = "https://www.trueachievements.com/game/Age-of-Empires-II-Definitive-Edition/achievements"

response = scraper.get(url)
time.sleep(5)
if "Just a moment..." in response.text:
    print("[!] Still got challenge page, retrying after delay...")
    time.sleep(5)
    response = scraper.get(url)
print(response.status_code)
print(response.text)  # Check if the page loads