import cloudscraper
import random
from bs4 import BeautifulSoup
import time
from tqdm import tqdm
from requests.exceptions import ConnectionError, HTTPError, Timeout

class BaseScraper:
    def __init__(self, base_url: str = "https://www.trueachievements.com/games.aspx", time_delay: int = 5):
        self.base_url = base_url

    def safe_get(self, scraper, url, retries=5, backoff=2):
        """
        Try fetching a URL with retries and exponential backoff.
        Returns response.text on success.
        """
        attempt = 0
        while attempt < retries:
            try:
                resp = scraper.get(url, timeout=10)
                resp.raise_for_status()
                return resp.text
            except (ConnectionError, Timeout) as e:
                attempt += 1
                wait = backoff ** attempt
                print(f"[!] Connection error, retry {attempt}/{retries} in {wait}s: {e}")
                time.sleep(wait)
            except HTTPError as e:
                print(f"[!] HTTP error: {e}")
                break
        raise Exception(f"Failed to fetch {url} after {retries} retries")

    def make_scraper(self):
        """Return a cloudscraper session with browser-like headers."""
        scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'Edge'})
        return scraper


    def get_total_pages(self, scraper):
        """Return total number of pages in the games list."""
        html = self.safe_get(scraper=scraper, url=self.base_url)
        time.sleep(5)
        soup = BeautifulSoup(html, "html.parser")

        pagination = soup.find("ul", {"class": "pagination"})
        pagemax = pagination.find("li", {"class": "l"}).text
        return int(pagemax)


    def get_gamebox_trs(self, scraper, page_num):
        """
        Return all <tr> elements (gamebox rows) for a given page.
        Uses query parameter to fetch specific page.
        """
        url = f"{self.base_url}?page={page_num}"
        html = self.safe_get(scraper=scraper, url=self.base_url)
        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table", {"id": "oGameList"})
        if not table:
            return []

        rows = table.find_all("tr")[1:]  # skip header row
        return rows


    def scrape_all_gamebox_trs(self):
        """
        Scrape all pages and return a list of <tr> elements
        for every game in the Xbox games list.
        """
        scraper = self.make_scraper()
        total_pages = self.get_total_pages(scraper)
        print(f"Found {total_pages} pages.")

        all_rows = []
        for page in tqdm(range(1, total_pages + 1)):
            rows = self.get_gamebox_trs(scraper, page)
            all_rows.extend(rows)
            time_delay = random.uniform(2,5)
            time.sleep(time_delay)  # be polite to server

        return all_rows


# Example usage
if __name__ == "__main__":
    bs = BaseScraper()
    gamebox_trs = bs.scrape_all_gamebox_trs()
    print(f"Collected {len(gamebox_trs)} total game rows.")
    print(gamebox_trs[0].prettify()[:500])
