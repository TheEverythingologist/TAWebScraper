import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
from tqdm import tqdm
import time
import pyautogui
from game import Game
import os
from utils import Utils as utils

def csv_to_pandas_loader(csv_path):
    _df = pd.read_csv(csv_path)
    return _df


def check_game_for_rescan_need(game_box_tr):
    # Start from the tr class in the games list page
    game_score = game_box_tr.find('td', {'class': 'score'}).text
    # If the game isn't released, don't scanning it.
    if game_score == 'Unreleased':
        return False
    game_title = (((game_box_tr.find('a', href=lambda href: href and '/game/' in href and '/achievements' in href))['href']).split('/'))[2]
    game_data_path = f"game_data/{game_title}.yaml"
    # if the yaml for the file doesn't exist, it automatically needs a rescan
    if not os.path.isfile(game_data_path):
        return True
    current_ta = (game_score.split(' '))[0].replace(',', '')
    # TODO Finish this
    
    
def get_page_links(games_list_url):
    response = requests.get(games_list_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    page_elements = soup.find('ul', {'class': 'pagination'})
    if 'game-pass' in games_list_url:
        max_page = int(page_elements.find('li', {'class': 'l'}).text)
        page_links = [f'https://www.trueachievements.com/game-pass-ultimate/games?page={i}' for i in range(1, max_page + 1)]
    elif 'series-x' in games_list_url:
        max_page = int(page_elements.find('li', {'class': 'l'}).text)
        page_links = [f'https://www.trueachievements.com/xbox-series-x/games?page={i}' for i in range(1, max_page + 1)]
    else:
        page_elements = page_elements.find_all('li', {'class': 'prevnext'})
        page_links = [page_element.find('a')['href'] for page_element in page_elements]
    return page_links


def find_game_box(inputted_game_boxes, inputted_url):
    for tr in inputted_game_boxes:
        a_tag = tr.find('a')['href']
        if a_tag == inputted_url:
            return tr
    return None


def format_game_row(input_game: Game):
    game_row = [
                input_game.game_name,
                input_game.base_ta,
                input_game.overall_ta,
                input_game.base_gs,
                input_game.overall_gs,
                input_game.base_ta / input_game.base_gs,
                input_game.overall_ta / input_game.overall_gs,
                input_game.base_completion_time,
                input_game.overall_completion_time,
                input_game.min_completion_time,
                input_game.site_rating,
                input_game.num_gamers,
                input_game.base_num_achievements,
                input_game.overall_num_achievements,
                input_game.base_ssd,
                input_game.base_tad_rate,
                input_game.overall_ssd / input_game.overall_completion_time,
                input_game.overall_tad_rate,
                input_game.developer,
                input_game.publisher,
                input_game.is_360,
                input_game.bcmx_val,
                input_game.pdu,
                input_game.server_closure,
                input_game.delisted,
                input_game.install_size,
                input_game.genres
                ]
    return game_row 


pyautogui.FAILSAFE = True
def stay_awake():
    pyautogui.moveRel(0, 15)
    pyautogui.press('left')
    pyautogui.moveRel(0, -15)


def main():
    urls = utils.urls
    output_files = utils.output_files
    columns_list = utils.columns_list    

    for url, output_file in zip(urls, output_files[:-1]):
        # Iterate through all of the urls to grab all of the game
        print(f"Scanning {url}")
        df_overall = pd.DataFrame(columns=columns_list)

        all_urls = []
        page_links = get_page_links(url)

        game_boxes = []
        for page in tqdm(page_links):
            # Update the soup
            response = requests.get(page)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the parent element containing the game information
            parent_element = soup.find('table', {'id': 'oGameList', 'class': 'maintable'})

            game_boxes += parent_element.find_all('tr', {'class': 'even'}) + parent_element.find_all('tr', {'class': 'odd'})

        # Iterate through each game box
        for game_box in game_boxes:
            # Find the element of the url
            url_element = game_box.find('td', {'class': 'game'}).find('a')['href']
            all_urls.append(url_element)

        """
        This is where we are going to start off next time. In the above for loop, check need for rescan in there and create the Game object there as well.
        No need to have the two for loops.
        """

        print("All URLs scanned in. Now iterating through games.")
        # Iterate through all of the game urls
        for url_value in tqdm(all_urls):
            formatted_url = f"http://trueachievements.com{url_value}"
            # First check if the game is in the corresponding output csv. If not, continue.
            specific_game_box = find_game_box(game_boxes, url_value)
            if specific_game_box is None:
                # There is currently a caching bug with Game Pass Games list. Need TA to fix this.
                continue
            # Second check if the game's gamebox data is different enough from the data in the csv. If not, continue
            need_to_rescan = check_game_for_rescan_need(game_box=specific_game_box)

            # Third actually create a game object. In theory, this should have us skip most games and save on runtime and server requests.
            game = Game(_url=formatted_url)
            # Skip the game if it hasn't been released yet.
            if game.unleased == True:
                continue
            # If the game data is in the dataframe, overwrite it. If not, create the row.
            game_row = format_game_row(game)
            # TODO change this after first run
            if False:
                df_overall.loc[df_overall['Name'] == game.game_name] = game_row
            if True:
                df_overall.loc[len(df_overall)] = game_row
            # Output the dataframe to a csv.
            # stay_awake()


        # Sort the dataframes
        df_overall = df_overall.sort_values(by=['Name'], ascending=True)
        df_overall = df_overall.reset_index(drop=True)

        # Concatenate the dataframes
        # Convert the dataframes to csv files        
        df_overall.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
    print('Done!')
