import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import re
from tqdm import tqdm

class Game:
    def __init__(self, _url) -> None:
        _response = requests.get(_url)
        _soup = BeautifulSoup(_response.content, 'html.parser')
        self.unleased = False
        self.base_num_achievements = 0
        self.overall_num_achievements = 0
        self.page_info = _soup.find('div', {'class': "page ta"})
        self.game_name = self.find_game_name()
        self.overall_ta = self.find_overall_ta()
        self.overall_gs = self.find_overall_gs()
        self.overall_completion_time = self.find_overall_completion_time()
        self.overall_std_score = self.find_overall_std_score()
        if self.unleased == False:
            self.base_ta = self.find_base_ta()
            self.base_gs = self.find_base_gs()
            self.base_completion_time = self.find_base_completion_time()
            self.dlc_ta = self.find_dlc_ta()
            self.dlc_gs = self.find_dlc_gs()
            self.overall_tad_rate = (self.overall_ta - self.overall_gs) / self.overall_completion_time
            self.base_tad_rate = (self.base_ta - self.base_gs) / self.base_completion_time
            self.base_std_score = self.find_base_std_score()

    def find_game_name(self):
        return (self.page_info.find('h2')).text

    def find_overall_ta(self):
        try:
            return string_to_num(self.page_info.find('div', {'title':"Maximum TrueAchievement"}).text)
        except AttributeError:
            self.unleased = True
            return None

    def find_overall_gs(self):
        try:
            return string_to_num(self.page_info.find('div', {'title':"Maximum Gamerscore"}).text)
        except AttributeError:
            self.unleased = True
            return None
    
    def find_overall_completion_time(self):
        try:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements (Including all DLC)"}).text
        except AttributeError:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements"})
            if time_str is None:
                self.unleased = True
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
                        ach_ta = str_to_int(ul_class.find('a')['data-af'])
                        ach_gs = int(((ul_class.find('p')['data-bf']).split(' '))[0])
                        if ach_gs == 0:
                            continue
                        ach_ratio = ach_ta / ach_gs
                        std_val += 10 * (ach_ratio - 1)
            except AttributeError:
                for li_style in ul_class.find_all("li"):
                    self.base_num_achievements += 1
                    ach_ta = str_to_int(ul_class.find('a')['data-af'])
                    ach_gs = int(((ul_class.find('p')['data-bf']).split(' '))[0])
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
                ach_ta = str_to_int(ul_class.find('a')['data-af'])
                ach_gs = int(((ul_class.find('p')['data-bf']).split(' '))[0])
                if ach_gs == 0:
                    continue
                ach_ratio = ach_ta / ach_gs
                std_val += 10 * (ach_ratio - 1)
        self.overall_ssd = std_val
        return std_val


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
            time_val = 1000
        elif time_val == ['200+']:
            time_val = 200
        elif len(time_val) > 1:
            time_val = time_val[0]
        else:
            print("Still broken!")
            print(time_val)
    return str(time_val)


def main():
    urls = ['https://www.trueachievements.com/xbox-game-pass/games', "https://www.trueachievements.com/xbox-one/games", "https://www.trueachievements.com/xbox-360/games", "https://www.trueachievements.com/windows/games"]
    output_files = ['xbox_game_pass_games.csv' ,'xbox_one_games.csv', 'xbox_360_games.csv', 'windows_games.csv']

    columns_list_overall_tad = ["Name Overall TAD", "Overall TA", "Overall GS", "Overall TAD Completion Time", "Overall TAD Rate"]
    columns_list_base_tad = ["Name Base TAD", "Base TA", "Base GS", "Base TAD Completion Time", "Base TAD Rate"]
    columns_list_overall_ssd = ["Name Overall SSD", "Overall SSD", "Overall SSD Completion Time", "Overall SSD Rate"]
    columns_list_base_ssd = ["Name Base SSD", "Base SSD", "Base SSD Completion Time", "Base SSD Rate"]

    for url, output_file in zip(urls, output_files):
        print(f"Scanning {url}")
        df_overall_tad = pd.DataFrame(columns=columns_list_overall_tad)
        df_base_tad = pd.DataFrame(columns=columns_list_base_tad)
        df_overall_ssd = pd.DataFrame(columns=columns_list_overall_ssd)
        df_base_ssd = pd.DataFrame(columns=columns_list_base_ssd)

        all_urls = []

        response = requests.get(url)

        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')
        page_elements = soup.find('ul', {'class': 'pagination'})
        page_elements = page_elements.find_all('li', {'class': 'prevnext'})
        page_links = [page_element.find('a')['href'] for page_element in page_elements]
        # The game pass list uses a different format, page links must be adjusted accordingly.
        if output_file == 'xbox_game_pass_games.csv':
            page_links = [f'https://www.trueachievements.com/xbox-game-pass/games?page={i}' for i in range(1, 5)]
            
        for page in tqdm(page_links):
            # Update the soup
            response = requests.get(page)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the parent element containing the game information
            parent_element = soup.find('table', {'id': 'oGameList', 'class': 'maintable'})

            game_boxes = parent_element.find_all('tr', {'class': 'even'}) + parent_element.find_all('tr', {'class': 'odd'})

            # Iterate through each game box
            for game_box in game_boxes:
                # Find the element of the url
                url_element = game_box.find('td', {'class': 'game'}).find('a')['href']
                all_urls.append(url_element)

        print("All URLs scanned in. Now iterating through games.")
        # Iterate through all of the game urls
        for url_value in tqdm(all_urls):
            try:
                game = Game(_url=f"http://trueachievements.com{url_value}")
            except AttributeError:
                continue
            # Skip the game if it hasn't been released yet.
            if game.unleased == True:
                continue

            df_overall_tad.loc[len(df_overall_tad)] = [game.game_name, game.overall_ta, game.overall_gs, game.overall_completion_time, game.overall_tad_rate]
            df_base_tad.loc[len(df_base_tad)] = [game.game_name, game.base_ta, game.base_gs, game.base_completion_time, game.base_tad_rate]
            df_overall_ssd.loc[len(df_overall_ssd)] = [game.game_name, game.overall_ssd, game.overall_completion_time, game.overall_ssd/game.overall_completion_time]
            df_base_ssd.loc[len(df_base_ssd)] = [game.game_name, game.base_ssd, game.base_completion_time, game.base_ssd/game.base_completion_time]
        # Sort the dataframes
        df_overall_tad = df_overall_tad.sort_values(by=['Overall TAD Rate'], ascending=False)
        df_overall_tad = df_overall_tad.reset_index(drop=True)
        df_base_tad = df_base_tad.sort_values(by=['Base TAD Rate'], ascending=False)
        df_base_tad = df_base_tad.reset_index(drop=True)
        df_overall_ssd = df_overall_ssd.sort_values(by=['Overall SSD Rate'], ascending=False)
        df_overall_ssd = df_overall_ssd.reset_index(drop=True)
        df_base_ssd = df_base_ssd.sort_values(by=['Base SSD Rate'], ascending=False)
        df_base_ssd = df_base_ssd.reset_index(drop=True)
        # Concatenate the dataframes
        df_concat = pd.concat([df_base_tad, df_overall_tad, df_base_ssd, df_overall_ssd], axis=1)
        # Convert the dataframes to csv files        
        df_concat.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
    print('Done!')
