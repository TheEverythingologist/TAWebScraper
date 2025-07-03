from xbox_ta_scraper import *

def main():
    urls = ['https://www.trueachievements.com/xbox-game-pass/games', "https://www.trueachievements.com/xbox-one/games", "https://www.trueachievements.com/xbox-360/games", "https://www.trueachievements.com/windows/games"]
    output_files = ['xbox_game_pass_games_june.csv' ,'xbox_one_games_june.csv', 'xbox_360_games_june.csv', 'windows_games_june.csv']

    columns_list_overall_tad = ["Name", "Completion Time", "Ratio", "BCMX Score", "Site Rating"]


if __name__ == "__main__":
    main()