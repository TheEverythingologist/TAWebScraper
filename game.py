from bs4 import BeautifulSoup
import requests
import re

class Game:
    def __init__(self, _url) -> None:
        _response = requests.get(_url)
        _soup = BeautifulSoup(_response.content, 'html.parser')
        self.unreleased = False

        self.base_num_achievements = 0
        self.overall_num_achievements = 0
        self.page_info = _soup.find('div', {'class': "page ta"})


        self.game_name = self.find_game_name()
        self.developer = self.find_developer()
        self.num_gamers = self.find_num_gamers()
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
        self.overall_std_score = self.find_overall_std_score()

        self.min_completion_time = self.find_min_completion_time()

        self.is_360 = self.check_360()
        self.genres = self.find_genres()

        if self.unreleased == False:
            self.base_ta = self.find_base_ta()
            self.base_gs = self.find_base_gs()
            self.base_completion_time = self.find_base_completion_time()

            self.dlc_ta = self.find_dlc_ta()
            self.dlc_gs = self.find_dlc_gs()

            self.overall_tad_rate = (self.overall_ta - self.overall_gs) / self.overall_completion_time
            self.base_tad_rate = (self.base_ta - self.base_gs) / self.base_completion_time
            self.base_std_score = self.find_base_std_score()
            
            # self.bcmx_val = self.calc_bcmx()
            self.bcmx_val = "None"

    def find_game_name(self):
        return (self.page_info.find('h2')).text

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
                self.unreleased = True
                return None
            time_str = time_str.text
        return float(adjust_time(time_str))

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
            return self.overall_completion_time
        base_time = float(adjust_time(base_info[0].find("a", {"title": "Estimated time to unlock all achievements"}).text))
        # Include updates since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Update':
                base_time += float(adjust_time(div_element.find('span', {'title':"Estimated time to unlock all achievements"}).text))
        return base_time
    
    def find_min_completion_time(self):
        try:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements (Including all DLC)"}).text
        except AttributeError:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements"})
            if time_str is None:
                self.unreleased = True
                return None
            time_str = time_str.text
        time_val = (time_str.split(' '))[0]
        time_val = time_val.split('-')
        try:
            time_val = float(time_val[0])
        except:
            if time_val == ['1000+'] or (time_str == '1000+h'):
                time_val = 200
            elif time_val == ['200+']:
                time_val = 200
            elif len(time_val) > 1:
                time_val = time_val[0]
            else:
                print("Still broken!")
                print(time_val)
        return float(time_val)


    def find_dlc_completion_times(self):
        base_info = self.page_info('div', {'class': "pnl-hd no-pills no-pr game"})
        if (base_info is None) or (base_info == []):
            return None
        dlc_time = float(adjust_time(base_info[0].find("a", {"title": "Estimated time to unlock all achievements"}).text))
        # Include updates since they are free
        for div_element in self.page_info.find_all("div", {"class": "pnl-hd no-pills no-pr game dlc"}):
            if div_element.find("div", {"class": "img"}).text == 'Add-on':
                new_time = div_element.find('span', {'title':"Estimated time to unlock all achievements"})
                if new_time == None:
                    return 
                dlc_time += float(adjust_time(new_time.text))
        return dlc_time

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
    
    def find_base_std_score(self):
        div_element = self.page_info.find("div", {"class": "main middle"})
        ul_classes = div_element.find_all("ul", {"class": "ach-panels"})
        std_val = 0
        for ul_class in ul_classes:
            check_div = ul_class.find_previous_sibling()
            try:
                check_val = check_div.find("div", {"class": "img"}).text
                if check_val == 'Add-on':
                    continue
                else:
                    for li_style in ul_class.find_all("li"):
                        self.base_num_achievements += 1
                        ach_ta = str_to_int(li_style.find('a')['data-af'])
                        ach_gs = int(((li_style.find('p')['data-bf']).split(' '))[0])
                        if ach_gs == 0:
                            continue
                        ach_ratio = ach_ta / ach_gs
                        std_val += 10 * (ach_ratio - 1)
            except AttributeError:
                for li_style in ul_class.find_all("li"):
                    self.base_num_achievements += 1
                    ach_ta = str_to_int(li_style.find('a')['data-af'])
                    ach_gs = int(((li_style.find('p')['data-bf']).split(' '))[0])
                    if ach_gs == 0:
                        continue
                    ach_ratio = ach_ta / ach_gs
                    std_val += 10 * (ach_ratio - 1)
                    
        self.base_ssd = std_val
        return std_val
        

    
    def find_overall_std_score(self):
        div_element = self.page_info.find("div", {"class": "main middle"})
        ul_classes = div_element.find_all("ul", {"class": "ach-panels"})
        std_val = 0
        for ul_class in ul_classes:
            for li_style in ul_class.find_all("li"):
                self.overall_num_achievements += 1
                ach_ta = str_to_int(li_style.find('a')['data-af'])
                ach_gs = int(((li_style.find('p')['data-bf']).split(' '))[0])
                if ach_gs == 0:
                    continue
                ach_ratio = ach_ta / ach_gs
                std_val += 10 * (ach_ratio - 1)
        self.overall_ssd = std_val
        return std_val
    
    def calc_bcmx(self):
        if self.is_360:
            return self.max_completion_time * (self.overall_ta / self.overall_gs + 0.5) ** 1.5 * 1.5
        else:
            return self.max_completion_time * (self.overall_ta / self.overall_gs) ** 1.5

    def check_360(self):
        if "Xbox 360" in self.game_name:
            return True
        elif len((self.page_info).find_all("a", {"href": "/xbox-360/games"})) != 0:
            return True
        else:
            return False
        
    def find_developer(self):
        developers = (self.page_info).find_all('a', href=lambda href: href and '/developer/' in href)
        return ', '.join([d.text for d in developers])

    def find_num_gamers(self):
        gamers = ((self.page_info).find('a', href=lambda href: href and '/gamers' in href and '/game/' in href)).text
        return string_to_num(gamers)

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
        dd = dt.find_next_sibling('dd')
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
        pdu = (closure[-1].find('a')).text
        if "Discontinued" in pdu or "Unobtainable" in pdu:
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
        
    def convert_to_dict(self):
        data_dict = {
            'Game Name': self.game_name,
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
            'Base Game Achievements': self.base_game_achievements,
            'Add On Achievements': self.dlc_achievements,
            'Update Achievements': self.update_achievements
        }
        return data_dict

    def output_to_yaml(self):
        pass
        

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
    try:
        time_val = (float(time_val[1][:-1]) + float(time_val[0])) / 2
    except:
        if time_val == ['1000+'] or (time_string == '1000+h'):
            time_val = 200
        elif time_val == ['200+']:
            time_val = 200
        elif len(time_val) > 1:
            time_val = time_val[0]
        else:
            print("Still broken!")
            print(time_val)
    return str(time_val)

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