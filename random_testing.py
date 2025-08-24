import requests
import cloudscraper
from bs4 import BeautifulSoup
import time

BASE_URL = "https://www.trueachievements.com"
START_PAGE = 1

def better_scraper(url):
    scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'Edge'})
    response = scraper.get(url)
    time.sleep(5)
    if "Just a moment..." in response.text:
        print("[!] Still got challenge page, retrying after delay...")
        time.sleep(5)
        response = scraper.get(url)
    return response

def scrape_page(page: int):
    url = f"{BASE_URL}/allgames.aspx?page={page}"
    resp = better_scraper(url=url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')

    rows = soup.select("table.generic_list tbody tr")
    if not rows:
        print(f"⚠️ No rows found on page {page}")
        return []

    results = []
    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 6:
            continue

        title_tag = cols[1].find("a")
        title = title_tag.text.strip()
        link = BASE_URL + title_tag["href"]

        score = cols[2].text.strip()
        ratio = cols[3].text.strip()
        completion_percent = cols[4].text.strip()
        completion_time = cols[5].text.strip()

        results.append({
            "title": title,
            "link": link,
            "score": score,
            "ratio": ratio,
            "completion_percent": completion_percent,
            "completion_time": completion_time
        })

    return results

def scrape_all(max_pages=1):
    all_games = []
    for page in range(1, max_pages + 1):
        print(f"🔄 Scraping page {page}...")
        page_data = scrape_page(page)
        if not page_data:
            break
        all_games.extend(page_data)
        time.sleep(1)  # be polite to their server
    return all_games

if __name__ == "__main__":
    games = scrape_all(max_pages=5)  # Scrape first 5 pages
    print(f"✅ Total games scraped: {len(games)}")
    for g in games[:5]:
        print(g)