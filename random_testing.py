from bs4 import BeautifulSoup
import time
import cloudscraper

BASE_URL = "https://www.trueachievements.com/games.aspx"



    


# Example: loop through the first 3 pages
if __name__ == "__main__":
    for page in range(1, 4):  # change to (1, 134) for all pages
        soup = get_page_selenium(page)
        print(f"Page {page} title:", soup.title.string)

        # Example: extract game names from the table
        table = soup.find("table", {"id": "cphContent_gvGames"})
        if table:
            rows = table.find_all("tr")[1:]  # skip header row
            for row in rows:
                cols = row.find_all("td")
                if cols:
                    game_name = cols[0].get_text(strip=True)
                    print(" -", game_name)
