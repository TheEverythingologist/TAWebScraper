import pandas as pd
from tqdm import tqdm
from game import Game
import os
from utils import Utils as utils
from game_box import GameBox
from tagdict import TagDict
from base_scraper import BaseScraper
import yaml


def check_game_for_scan_need(game_box_object: GameBox):
    # We use objects now
    game_file = f"game_data/{game_box_object.game_name_url}.yaml"
    # If the game is unreleased or has no TA score, don't bother scanning it.
    if game_box_object.ratio == '-' or game_box_object.ta_score == "0":
        # Don't scan a game that hasn't been released has no TA score or no ratio.
        game_box_object.ta_score = 'Unreleased'
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
            # Sometimes games have buggy pages. This catches those games and forces a rescan.
            print(f"\nError with {game_file} \n Removing the file and rescanning.")
            os.remove(game_file)
            return True
        new_ta = float(game_box_object.ta_score)
        if abs((new_ta - previous_ta) / previous_ta) >= .025:
            # If ta score changed by +/- 2.5 percent, rescan
            return True
    return False


def format_game_row(input_game: dict):
    # If the game doesn't have a valid completion time or install size, do NOT output its row. It's likely either bugged or unreleased.
    try:
        overall_time_list = input_game['Base Completion Time']
        if int(overall_time_list[0]) == -1 or overall_time_list[1] == 0 or input_game['Install Size'] is None:
            return None
    except TypeError:
        return None
    time_val = max(float(overall_time_list[0]), 0.5)
    min_time, max_time = input_game['Overall Completion Time'][0], input_game['Overall Completion Time'][1] 
    # num_achievements = len(input_game['Base Game Achievements']) + len(input_game['Add On Achievements']) + len(input_game['Update Achievements'])
    # tad_val = input_game['Overall TA'] - input_game['Overall GS']
    # tad = input_game['Base TA'] - input_game['Base GS']
    # num_achievements = len(input_game['Base Game Achievements']) + len(input_game['Update Achievements'])
    game_row = [
        input_game['Game Name'],
        input_game['Overall TA'],
        input_game['Overall GS'],
        input_game['Site Rating'],
        input_game['Number of Gamers'],
        input_game['Percentage Completed'],
        min_time,
        max_time,
        input_game['Overall Ratio'],
        input_game['Release Date'],
        input_game['Install Size'],
        input_game['Developer'],
        input_game['Publisher']
    ]
    new_row = pd.DataFrame([game_row], columns=utils.columns_list)
    return new_row 


def main():
    games_scanned = 0
    bs = BaseScraper()
    gamebox_trs = bs.scrape_all_gamebox_trs()

    for game_box_tr in tqdm(gamebox_trs):
        # Find the element of the url
        game_box_obj = GameBox(game_box_tr)
        need_to_scan = check_game_for_scan_need(game_box_object=game_box_obj)
        if need_to_scan:
            games_scanned += 1
            game = Game(_url = game_box_obj.game_url, _tag_dict = TagDict())
            if game.unreleased == False:
                game_data_path = f"game_data/{game_box_obj.game_name_url}.yaml"
                try:
                    game.output_to_yaml(path=game_data_path)
                except AttributeError:
                    print(f"Troublesome game: {game_box_obj.game_url}")

    # We get here once we have iterated all other games. This is for the all games output
    df_overall = pd.DataFrame(columns=utils.columns_list)
    print(f"All scans completed. Games scanned = {games_scanned}\nDumping ALL game data to csv")
    for yaml_file in tqdm(os.listdir("game_data/")):
        game_data_path = f"game_data/{yaml_file}"
        with open(game_data_path, 'r') as game_file:
            game_data = yaml.safe_load(game_file)
            game_row = format_game_row(game_data)
            if game_row is None:
                continue
        df_overall = pd.concat([df_overall, game_row], ignore_index=True)

    # Alphabetize the dataframe, and dump to csv
    df_overall = df_overall.sort_values(by=['Game Name'], ascending=False)
    df_overall = df_overall.reset_index(drop=True)        
    df_overall.to_csv(utils.output_file, index=False)


if __name__ == "__main__":
    main()
    print('Done!')
