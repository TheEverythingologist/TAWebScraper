from bs4 import BeautifulSoup
import requests
import re

class GameBox:
    def __init__(self, game_box_tr):
        self.game_box_tr = game_box_tr
        self.ta_score = self.get_ta_score()
        self.game_url = self.get_game_url()
        self.game_name_url = self.get_game_name_url()

    def get_ta_score(self):
        game_score = self.game_box_tr.find('td', {'class': 'score'}).text
        current_ta = (game_score.split(' '))[0].replace(',', '')
        return current_ta
    
    def get_game_url(self):
        try:
            game_url = ((self.game_box_tr.find('a', href=lambda href: href and '/game/' in href and '/achievements' in href))['href'])
            game_url = f"https://www.trueachievements.com{game_url}"
            if game_url == "https://www.trueachievements.com/game/METAL-SUITS-Counterattack/achievements":
                # I have no idea why, but this game is broken for some reason.
                return "https://www.trueachievements.com/game/Metal-Suits-Counter-Attack/achievements"
            return game_url
        except TypeError or AttributeError:
            self.ta_score = 'Unreleased'
            return None


    def get_game_name_url(self):
        if self.game_url == None:
            return None
        else:
            game_title = (((self.game_box_tr.find('a', href=lambda href: href and '/game/' in href and '/achievements' in href))['href']).split('/'))[2]
            return game_title