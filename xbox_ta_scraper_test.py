from xbox_ta_scraper import Game

import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
from tqdm import tqdm


def test_game_generation(input_url) -> None:
    test_game = Game(input_url)
    print(test_game.game_name)


def main() -> None:
    test_url = "https://www.trueachievements.com/game/LEGO-Star-Wars-3/achievements?gamerid=735979"
    test_game_generation(test_url)


if __name__ == "__main__":
    main()