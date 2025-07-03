from achievement import Achievement
from game import Game
from bs4 import BeautifulSoup
from tagdict import TagDict
import requests

tag_dict = TagDict()
game_name = "SUPERBEAT-XONiC-EX"
url = f"https://www.trueachievements.com/game/{game_name}/achievements"
test_game = Game(_url = url, _tag_dict=tag_dict)
game_data_path = f"game_data/{game_name}.yaml"
test_game.output_to_yaml(path=game_data_path)

print("Done")