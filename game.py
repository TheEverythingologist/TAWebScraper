from bs4 import BeautifulSoup
from achievement import Achievement
import requests
import re
import yaml
import math
import cloudscraper
import time

class Game:
    def __init__(self, _url, _tag_dict) -> None:
        self.url = _url
        _scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'Edge'})  # Emulate Edge
        _response = _scraper.get(_url)
        
        # Wait briefly if needed (sometimes Cloudflare needs time)
        time.sleep(5)
        # Retry if title is still "Just a moment..."
        if "Just a moment..." in _response.text:
            print("[!] Still got challenge page, retrying after delay...")
            time.sleep(5)
            response = _scraper.get(_url)
        _soup = BeautifulSoup(_response.content, 'html.parser')
        
        self.unreleased = False
        self.base_achievements: list[Achievement] = []
        self.dlc_achievements: list[Achievement] = []
        self.update_achievements: list[Achievement] = []
        self.page_info = _soup.find('div', {'class': "page ta"})
        self.game_name = self.find_game_name()
        if self.game_name == -1:
            self.unreleased == True
            return None

        self.parse_all_achievements(_tag_dict)

        self.developer = self.find_developer()
        self.num_gamers = self.find_num_gamers()
        if self.num_gamers == 0:
            self.unreleased == True
        
        elif self.unreleased == False:
            self.site_rating = self.find_site_rating()
            self.server_closure = self.find_server_closure()
            self.delisted = self.check_delisted()
            self.install_size = self.check_install_size()
            self.publisher = self.find_publisher()
            self.release_date = self.find_release_date()
            self.pdu = self.find_pdu()
            self.overall_ta = self.find_overall_ta()
            self.overall_gs = self.find_overall_gs()
            self.overall_completion_time = self.find_overall_completion_time()
            self.genres = self.find_genres()
            self.walkthrough = self.find_walkthrough()
            self.num_completions = self.find_num_completions()
            self.percentage_completed = self.calculate_percentage_completed()
            self.base_ta = self.find_base_ta()
            self.base_gs = self.find_base_gs()
            self.base_completion_time = self.find_base_completion_time()
            self.overall_ratio = self.find_overall_ratio()
            self.base_ratio = self.find_base_ratio()

            self.dlc_ta = self.find_dlc_ta()
            self.dlc_gs = self.find_dlc_gs()

            self.data_dict = self.convert_to_dict()

    def find_game_name(self):
        try:
            return (self.page_info.find('h2')).text
        except AttributeError:
            print(f"Problem url: {self.url}")
            return -1

    def find_overall_ta(self):
        try:
            return string_to_num(self.page_info.find('div', {'title':"Maximum TrueAchievement"}).text)
        except AttributeError:
            self.unreleased = True
            return None

    def find_overall_gs(self):
        try:
            return string_to_num(self.page_info.find('div', {'title':"Maximum Gamerscore"}).text)
        except AttributeError:
            self.unreleased = True
            return None
    
    def find_overall_completion_time(self):
        try:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements (Including all DLC)"}).text
        except AttributeError:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements"})
            if time_str is None:
                return self.fetch_completion_time()
            time_str = time_str.text
        return adjust_time(time_str)

    def find_base_ta(self):
        base_info = self.page_info('div', {'class': "pnl-hd no-pills no-pr game"})
        if (base_info is None) or (base_info == []):
            return self.overall_ta
        base_ta = string_to_num(base_info[0].find("div", {"title": "Maximum TrueAchievement"}).text)
        # Include updates since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Update':
                base_ta += string_to_num(div_element.find('div', {'title':"Maximum TrueAchievement"}).text)
        return base_ta

    def find_base_gs(self):
        base_info = self.page_info('div', {'class': "pnl-hd no-pills no-pr game"})
        if (base_info is None) or (base_info == []):
            return self.overall_gs
        base_gs = string_to_num(base_info[0].find("div", {"title": "Maximum Gamerscore"}).text)
        # Include updates since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Update':
                base_gs += string_to_num(div_element.find('div', {'title':"Maximum Gamerscore"}).text)
        return base_gs

    def find_base_completion_time(self):
        base_info = self.page_info('div', {'class': "pnl-hd no-pills no-pr game"})
        if (base_info is None) or (base_info == []):
            return (self.overall_completion_time).copy()
        
        base_time = base_info[0].find("a", {"title": "Estimated time to unlock all achievements"})
        if base_time is None:
            base_time = self.fetch_completion_time()
        else:
            base_time = adjust_time(base_time.text)
        # Include updates since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Update':
                time_to_add = div_element.find('span', {'title':"Estimated time to unlock all achievements"})
                if time_to_add is None:
                    continue
                time_to_add = adjust_time(time_to_add.text)
                base_time = [a+b for a,b in zip(time_to_add, base_time)]
        return base_time

    def find_dlc_ta(self):
        dlc_ta = 0
        base_info = self.page_info('div', {'class': "pnl-hd no-pills no-pr game"})
        if (base_info is None) or (base_info == []):
            return 0
        # Iterate through all dlc since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Add-on':
                dlc_ta += string_to_num(div_element.find('div', {'title':"Maximum TrueAchievement"}).text)
        return dlc_ta

    def find_dlc_gs(self):
        dlc_gs = 0
        base_info = self.page_info('div', {'class': "pnl-hd no-pills no-pr game"})
        if (base_info is None) or (base_info == []):
            return 0
        # Iterate through all dlc since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Add-on':
                dlc_gs += string_to_num(div_element.find('div', {'title':"Maximum Gamerscore"}).text)
        return dlc_gs
    
    def parse_all_achievements(self, _tag_dict):
        ul_classes = self.page_info.find_all("ul", {"class": "ach-panels"})
        for ul_class in ul_classes:
            check_div = ul_class.find_previous_sibling('div')
            while check_div and not (('gh-btn' in check_div.get('class', [])) or 'pnl-hd' in check_div.get('class', [])):
                check_div = check_div.find_previous_sibling()
            check_val = check_div.find("div", {"class": "img"})
            for li_style in ul_class.find_all("li"):
                achievement = Achievement(li_style=li_style, tag_dict=_tag_dict)
                if check_val is None:
                    self.base_achievements.append(achievement)
                elif check_val.text == 'Base':
                    self.base_achievements.append(achievement)
                elif check_val.text == 'Add-on':
                    self.dlc_achievements.append(achievement)
                elif check_val.text == 'Update':
                    self.update_achievements.append(achievement)

    def find_developer(self):
        developers = (self.page_info).find_all('a', href=lambda href: href and '/developer/' in href)
        return ', '.join([d.text for d in developers])

    def find_num_gamers(self):
        try:
            gamers = ((self.page_info).find('a', href=lambda href: href and '/gamers' in href and '/game/' in href)).text
            return string_to_num(gamers)
        except AttributeError:
            # If this doesn't exist, the game has no gamers and is not released.
            self.unreleased == True
            return 0

    def find_site_rating(self):
        try:
            rating = ((self.page_info).find('span', title=lambda title: title and 'out of 5' in title)).text
        except AttributeError:
            return "None"
        if rating.endswith('*'):
            rating = rating[:-1]
        return float(rating)

    def find_server_closure(self):
        closure = (self.page_info).find('div', {"class": "warningspanel"})
        if closure is None:
            return False
        elif "closure" in closure.text:
            return True
        else:
            return False

    def check_delisted(self):
        closure = (self.page_info).find('div', {"class": "warningspanel"})
        if closure is None:
            return False
        elif "removed from the Microsoft Store" in closure.text:
            return True
        else:
            return False

    def check_install_size(self):
        dt = (self.page_info).find('dt', string='Size:')
        try:
            dd = dt.find_next_sibling('dd')
        except AttributeError:
            return None
        size = dd.text
        if size.endswith("GB"):
            size = size[:-2]
            return float(size) * 1000
        elif size.endswith("MB"):
            size = size[:-2]
            return float(size)

    def find_publisher(self):
        publishers = (self.page_info).find_all('a', href=lambda href: href and '/publisher/' in href)
        if len(publishers) > 1:
            return ', '.join([p.text for p in publishers])
        elif len(publishers) == 0:
            return []
        else:
            return (publishers[0]).text
        
    def find_release_date(self):
        dt = (self.page_info).find('dt', string='Release')
        dd = dt.find_next_sibling('dd')
        return dd.text

    def find_pdu(self):
        closure = (self.page_info).find_all('div', {"class": "warningspanel"})
        if closure[:-1] == []:
            return 0
        for warning in closure:
            pdu = warning.find('a', href = lambda href: href and 'unobsdiscos=1' in href)
            if not (pdu is None):
                pdu = pdu.text
                break
        if pdu is None:
            return 0
        elif "Discontinued" in pdu or "Unobtainable" in pdu:
            numbers = re.findall(r'\d+', pdu)
            return sum(int(num) for num in numbers)
        else:
            return 0

    def find_genres(self):
        genre_data = (self.page_info).find_all('a', href=lambda href: href and '/genre/' in href)
        if len(genre_data) == 0:
            return "None"
        elif len(genre_data) > 1:
            return ', '.join([p.text for p in genre_data])
        else:
            return (genre_data[0]).text
        
    def find_walkthrough(self):
        walkthrough_data = (self.page_info).find('a', href=lambda href: href and '/walkthrough' in href)
        star_check = walkthrough_data.find('span', {'class': 'alert'})
        if star_check is None:
            return False
        else:
            return True
        
    def find_overall_ratio(self):
        if self.overall_gs == 0:
            return 0
        else:
            return self.overall_ta / self.overall_gs
        
    def find_base_ratio(self):
        if self.base_gs == 0:
            return 0
        else:
            return self.base_ta / self.base_gs
    
    def find_num_completions(self):
        completion_href = (self.page_info).find('a', href=lambda href: href and '/completionists' in href)
        completionists = (completion_href.text).split(' ')[0]
        completionists = completionists.replace(',', '')
        return int(completionists)
    
    def calculate_percentage_completed(self):
        if self.num_gamers == 0:
            return 0
        return round(100* self.num_completions / self.num_gamers, 2)
    
    def fetch_completion_time(self):
        completionists_url = self.url.replace("/achievements", "/completionists")
        _scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'Edge'})  # Emulate Edge
        time_response = _scraper.get(completionists_url)
        time.sleep(5)
        # Retry if title is still "Just a moment..."
        if "Just a moment..." in time_response.text:
            print("[!] Still got challenge page, retrying after delay...")
            time.sleep(5)
            time_response = _scraper.get(completionists_url)

        time_soup = BeautifulSoup(time_response.content, 'html.parser')
        _page_info = time_soup.find('div', {'class': "page ta"})
        trs = _page_info.find_all('tr', {'class': 'even'}) + _page_info.find_all('tr', {'class': 'odd'})
        tds = []
        hours, minutes, times = 0, 0, 0
        for tr in trs:
            _tds = tr.find_all("td")
            time_text = (_tds[-1]).text
            if time_text == '0 mins':
                continue
            time_list = time_text.split(' ')
            if len(time_list) == 4:
                # time is greater than 1 hour
                hours += int(time_list[0])
                minutes += int(time_list[2])
            elif len(time_list) == 2:
                # time is less than 1 hour
                minutes += int(time_list[0])
            times += 1
        if times == 0:
            self.unreleased == True
            return [-1, -1]
        average_time = (hours + minutes / 60) / times
        return [math.floor(average_time), math.ceil(average_time)]
        
        
    def convert_to_dict(self):
        data_dict = {
            'Game Name': self.game_name,
            'Overall TA': self.overall_ta,
            'Base TA': self.base_ta,
            'Overall GS': self.overall_gs,
            'Base GS': self.base_gs,
            'Overall Ratio': self.overall_ratio,
            'Base Ratio': self.base_ratio,
            'Developer': self.developer,
            'Publisher': self.publisher,
            'Number of Gamers': self.num_gamers,
            'Site Rating': self.site_rating,
            'Server Closure': self.server_closure,
            'Delisted': self.delisted,
            'Install Size': self.install_size,
            'Release Date': self.release_date,
            'PDU': self.pdu,
            'Genres': self.genres,
            'Base Completion Time': self.base_completion_time,
            'Overall Completion Time': self.overall_completion_time,
            'Walkthrough': self.walkthrough,
            'Number of Completions': self.num_completions,
            'Percentage Completed': self.percentage_completed,
            'Base Game Achievements': [a.output_as_dict() for a in self.base_achievements],
            'Add On Achievements': [a.output_as_dict() for a in self.dlc_achievements],
            'Update Achievements': [a.output_as_dict() for a in self.update_achievements]
        }
        return data_dict

    def output_to_yaml(self, path):
        with open(path, 'w') as file:
            yaml.dump(self.data_dict, file)
        

def string_to_num(s):
    pattern = r'\D*(\d{1,3}(,\d{3})*(\.\d+)?)\D*'
    match = re.search(pattern, s)
    if match:
        return int(match.group(1).replace(',', ''))
    else:
        return None


def str_to_int(s):
    return int(s.replace(",", ""))


def adjust_time(time_string):
    time_val = (time_string.split(' '))[0]
    time_val = time_val.split('-')
    for i, val in enumerate(time_val):
        if i == 0 and val == '1000+h':
            time_val = ['1000', '1000h']
        if i == 1 and val == '1000+h':
            time_val[i] = '1000h'
    if time_val == ['200+']:
        print("200+ !")
        return [200, 200]
    else:
        time_val = [float(time_val[0]), float(time_val[1][:-1])]
        return time_val

def max_time(time_string):
    time_val = (time_string.split(' '))[0]
    time_val = time_val.split('-')
    try:
        time_val = float(time_val[0])
    except:
        if time_val == ['1000+'] or (time_string == '1000+h'):
            time_val = 200
        elif time_val == ['200+']:
            time_val = 200
        # elif len(time_val) > 1:
        #     time_val = time_val[0]
        else:
            print("Still broken!")
            print(time_val)
    return str(time_val)