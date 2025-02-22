from bs4 import BeautifulSoup
import requests
import re

class Achievement:
    def __init__(self, li_style, tag_dict):
        self.li_style = li_style
        self.achievement_name: str = self.find_name()
        self.description: str = self.find_description()
        self.ta: float = self.find_ta()
        self.gs: int = self.find_gs()
        self.ratio: float = self.find_ratio()
        self.guide_exists: bool = self.find_guide()
        self.num_gamers: int = self.find_num_gamers()
        self.percentage: int = self.find_percentage()
        self.url: str = self.find_url()
        self.tags: list[str] = self.find_tags(tag_dict)


    def find_name(self) -> str:
        name = (self.li_style).find("a", {"class": "title"}).text
        return name

    def find_description(self) -> str:
        desc = (self.li_style).find("p").text
        return desc

    def find_ta(self):
        ta = (self.li_style).find('a', {'class': 'title'})['data-af']
        return ta
    
    def find_gs(self):
        gs = (self.li_style).find('p')['data-bf']
        gs = (gs.split(' - '))[0]
        return gs

    def find_ratio(self):
        progress_bar = (self.li_style).find('div', {'class': 'progress-bar'})['data-af']
        if progress_bar == '0 tracked gamers':
            return 'NA'
        else:
            val = progress_bar.split(' = ')
            val = float(val[1].replace(')', ''))
            return val


    def find_guide(self):
        val = (self.li_style).find('div', {'class': 'info'})
        guide = val.find('span')
        if guide is None:
            return False
        else:
            return True

    def find_num_gamers(self):
        progress_bar = (self.li_style).find('div', {'class': 'progress-bar'})['data-af']
        if progress_bar == '0 tracked gamers':
            return 0
        elif '1 tracked gamer ' in progress_bar:
            return 1
        else:
            val = progress_bar.split(' tracked gamers ')
            val = int(val[0].replace(',', ''))
            return val

    def find_percentage(self):
        progress_bar = (self.li_style).find('div', {'class': 'progress-bar'})['data-af']
        if progress_bar == '0 tracked gamers':
            return 'NA'
        else:
            val = progress_bar.split(' (')
            val = (val[1]).split(' - ')
            val = val[0]
            return val

    def find_url(self):
        link = (self.li_style).find('a', {'class': 'title'})['href']
        url = f"https://www.trueachievements.com{link}"
        return url
    
    def find_tags(self, tag_dict):
        flg = self.li_style.find("i", class_=lambda c: c and "flg" in c)
        flg = flg['class'][0]
        if flg in tag_dict.tagdict:
            tags = tag_dict.tagdict[flg]
        else:
            _response = requests.get(self.url)
            _soup = BeautifulSoup(_response.content, 'html.parser')
            _imgs = _soup.find_all('img', src=lambda src: src and "/sprites/flags/" in src)
            tags = [((val['title']).split(' - '))[0] for val in _imgs]
            tag_dict.update_yaml({flg: tags})
            tag_dict.load_yaml()
        return tags.copy()
    
    def output_as_dict(self):
        return {
            "Achievement Name": self.achievement_name,
            "Description": self.description,
            "TA": self.ta,
            "GS": self.gs,
            "Ratio": self.ratio,
            "Guide": self.guide_exists,
            "Number of Gamers": self.num_gamers,
            "Percentage of Gamers": self.percentage,
            "Tags": self.tags
        }