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
from game_box import GameBox
from tagdict import TagDict
import yaml

def csv_to_pandas_loader(csv_path):
    _df = pd.read_csv(csv_path)
    return _df


def check_game_for_scan_need(game_box_object: GameBox):
    # We use objects now
    game_file = f"game_data/{game_box_object.game_name_url}.yaml"
    # If the game is unreleased, don't bother scanning it.
    if game_box_object.ta_score == "Unreleased":
        return False
    if not os.path.isfile(game_file):
        # If the game's yaml doesn't exist, we automatically know it needs a scan
        return True
    else:
        with open(game_file, 'r') as file:
            game_yaml_data = yaml.load(file, Loader=yaml.FullLoader)
        try:    
            previous_ta = game_yaml_data['Overall TA']
        except TypeError:
            print(f"\nError with {game_file} \n Removing the file and rescanning.")
            os.remove(game_file)
            return True
        new_ta = float(game_box_object.ta_score)
        if abs((new_ta - previous_ta) / previous_ta) >= .025:
            # If ta score changed by +/- 2.5 percent, rescan
            return True
    return False
    
    
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
    tag_dict = TagDict()

    for url, output_file in zip(urls, output_files[:-1]):
        # Iterate through all of the urls to grab all of the game
        print(f"Scanning {url}")
        df_overall = pd.DataFrame(columns=columns_list)

        page_links = get_page_links(url)
        game_box_trs = []

        for page in tqdm(page_links):
            # Update the soup
            response = requests.get(page)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the parent element containing the game information
            parent_element = soup.find('table', {'id': 'oGameList', 'class': 'maintable'})

            game_box_trs += parent_element.find_all('tr', {'class': 'even'}) + parent_element.find_all('tr', {'class': 'odd'})

        # Iterate through each game box
        print("Now checking games for rescan need")
        for game_box_tr in tqdm(game_box_trs):
            # Find the element of the url
            game_box_obj = GameBox(game_box_tr)
            need_to_scan = check_game_for_scan_need(game_box_object=game_box_obj)
            if need_to_scan:
                game = Game(_url = game_box_obj.game_url, _tag_dict = tag_dict)
                if game.unreleased == False:
                    game_data_path = f"game_data/{game_box_obj.game_name_url}.yaml"
                    try:
                        game.output_to_yaml(path=game_data_path)
                    except AttributeError:
                        print(f"Troublesome game: {game_box_obj.game_url}")
        # Sort the dataframes
        # df_overall = df_overall.sort_values(by=['Name'], ascending=True)
        # df_overall = df_overall.reset_index(drop=True)

        # # Concatenate the dataframes
        # # Convert the dataframes to csv files        
        # df_overall.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
    print('Done!')
