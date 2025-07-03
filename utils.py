class Utils:
    urls = ['https://www.trueachievements.com/game-pass-ultimate/games', 
            "https://www.trueachievements.com/xbox-one/games", 
            "https://www.trueachievements.com/xbox-360/games", 
            "https://www.trueachievements.com/windows/games", 
            "https://www.trueachievements.com/xbox-series-x/games"]
    output_files = ['game_pass_games_times.csv',
                    'xbox_one_games_times.csv', 
                    'xbox_360_games_times.csv', 
                    'windows_games_times.csv',
                    'series_x_games_times.csv',
                    'all_games_times.csv']
    columns_list = ["Game Name",
                    "TA",
                    "GS",
                    "TAD",
                    "Num",
                    "Time",
                    "Score"]