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

        self.max_completion_time = self.find_max_completion_time()

        self.is_360 = self.check_360()

        if self.unleased == False:
            self.base_ta = self.find_base_ta()
            self.base_gs = self.find_base_gs()
            self.base_completion_time = self.find_base_completion_time()

            self.dlc_ta = self.find_dlc_ta()
            self.dlc_gs = self.find_dlc_gs()

            self.overall_tad_rate = (self.overall_ta - self.overall_gs) / self.overall_completion_time
            self.base_tad_rate = (self.base_ta - self.base_gs) / self.base_completion_time
            self.base_std_score = self.find_base_std_score()
            
            self.bcmx_val = self.calc_bcmx()


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
    
    def find_max_completion_time(self):
        try:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements (Including all DLC)"}).text
        except AttributeError:
            time_str = self.page_info.find('a', {'title':"Estimated time to unlock all achievements"})
            if time_str is None:
                self.unleased = True
                return None
            time_str = time_str.text
        time_val = (time_str.split(' '))[0]
        time_val = time_val.split('-')
        try:
            time_val = float(time_val[1][:-1])
        except:
            if time_val == ['1000+'] or (time_str == '1000+h'):
                time_val = 1000
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
        rating = ((self.page_info).find('span', title=lambda title: title and 'out of 5' in title)).text
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
        closure = (self.page_info).find('div', {"class": "warningspanel"})
        if closure is None:
            return 0
        pdu = (closure.find('a')).text
        if "Discontinued" in pdu or "Unobtainable" in pdu:
            numbers = re.findall(r'\d+', pdu)
            return sum(int(num) for num in numbers)
        else:
            return 0


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

def max_time(time_string):
    time_val = (time_string.split(' '))[0]
    time_val = time_val.split('-')
    try:
        time_val = float(time_val[1][:-1])
    except:
        if time_val == ['1000+'] or (time_string == '1000+h'):
            time_val = 1000
        elif time_val == ['200+']:
            time_val = 200
        # elif len(time_val) > 1:
        #     time_val = time_val[0]
        else:
            print("Still broken!")
            print(time_val)
    return str(time_val)

def csv_to_pandas_loader(csv_path):
    _df = pd.read_csv(csv_path)
    return _df


def check_game_for_rescan_need(output_file, game_box):
    # TODO remove this after first run.
    return True
    # Load new data
    game_overall_ta_gs = (game_box.find('td', {'class': "score"}).text).split(' ')
    game_overall_ta = float(str_to_int(game_overall_ta_gs[0]))
    game_overall_gs = float(str_to_int(game_overall_ta_gs[1][1:-1]))

    game_max_time_str = (game_box.find('a', href=lambda href: href and '/completiontime' in href and '/game/' in href)).text
    game_max_time = max_time(game_max_time_str)

    _td = game_box.find('td', {'class': "game"})
    game_name = (_td.find('a')).text
    _df = pd.read_csv(output_file)
    _df = _df.loc[_df['Name'] == game_name]
    # Load old data
    old_ta = _df.at[0, 'Overall TA']
    old_gs = _df.at[0, 'Overall GS']
    old_max_time = _df.at[0, 'Overall Max Time']
    # Check data
    if game_overall_ta >= 1.05*old_ta or game_overall_ta <= 0.95*old_ta:
        return True
    elif game_overall_gs != old_gs:
        return True
    elif game_max_time != old_max_time:
        return True
    else:
        return False


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
                input_game.max_completion_time,
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
                input_game.install_size
                ]
    return game_row 

def main():
    urls = ['https://www.trueachievements.com/xbox-game-pass/games', "https://www.trueachievements.com/xbox-one/games", "https://www.trueachievements.com/xbox-360/games", "https://www.trueachievements.com/windows/games"]
    output_files = ['xbox_game_pass_games.csv' ,'xbox_one_games.csv', 'xbox_360_games.csv', 'windows_games.csv']

    columns_list = ["Name",
                    "Base TA",
                    "Overall TA",
                    "Base GS",
                    "Overall GS",
                    "Base Ratio",
                    "Overall Ratio",
                    "Base Time",
                    "Overall Time",
                    "Max Time",
                    "Site Rating",
                    "Num Gamers",
                    "Base Num Achievements",
                    "Overall Num Achievements",
                    "Base SSD",
                    "Base TAD Rate",
                    "Overall SSD Rate",
                    "Overall TAD Rate",
                    "Developer(s)",
                    "Publisher(s)",
                    "is 360?",
                    "BCMX Value",
                    "PDU",
                    "Server Closure",
                    "Delisted",
                    "Install Size"
                    ]

    for url, output_file in zip(urls, output_files):
        print(f"Scanning {url}")
        df_overall = pd.DataFrame(columns=columns_list)

        all_urls = []

        response = requests.get(url)

        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.content, 'html.parser')
        page_elements = soup.find('ul', {'class': 'pagination'})
        page_elements = page_elements.find_all('li', {'class': 'prevnext'})
        page_links = [page_element.find('a')['href'] for page_element in page_elements]
        # The game pass list uses a different format, page links must be adjusted accordingly.
        if output_file == 'xbox_game_pass_games.csv':
            page_links = [f'https://www.trueachievements.com/xbox-game-pass/games?page={i}' for i in range(1, 6)]
            
        game_boxes = []

        for page in tqdm(page_links):
            # Update the soup
            response = requests.get(page)
            soup = BeautifulSoup(response.content, 'html.parser')
            # Find the parent element containing the game information
            parent_element = soup.find('table', {'id': 'oGameList', 'class': 'maintable'})

            game_boxes += parent_element.find_all('tr', {'class': 'even'}) + parent_element.find_all('tr', {'class': 'odd'})

        # Iterate through each game box
        for game_box in game_boxes:
            # Find the element of the url
            url_element = game_box.find('td', {'class': 'game'}).find('a')['href']
            all_urls.append(url_element)

        print("All URLs scanned in. Now iterating through games.")
        # Iterate through all of the game urls
        for url_value in tqdm(all_urls):
            formatted_url = f"http://trueachievements.com{url_value}"
            # First check if the game is in the corresponding output csv. If not, continue.
            specific_game_box = find_game_box(game_boxes, url_value)
            if specific_game_box is None:
                # There is currently a caching bug with Game Pass Games list. Need TA to fix this.
                continue
            # Second check if the game's gamebox data is different enough from the data in the csv. If not, continue
            need_to_rescan = check_game_for_rescan_need(output_file=output_file, game_box=specific_game_box)

            # Third actually create a game object. In theory, this should have us skip most games and save on runtime and server requests.
            try:
                game = Game(_url=formatted_url)
            except AttributeError:
                continue
            # Skip the game if it hasn't been released yet.
            if game.unleased == True:
                continue
            # If the game data is in the dataframe, overwrite it. If not, create the row.
            game_row = format_game_row(game)
            # TODO change this after first run
            if False:
                df_overall.loc[df_overall['Name'] == game.game_name] = game_row
            if True:
                df_overall.loc[len(df_overall)] = game_row
            # Output the dataframe to a csv.


        # Sort the dataframes
        df_overall = df_overall.sort_values(by=['Name'], ascending=False)
        df_overall = df_overall.reset_index(drop=True)

        # Concatenate the dataframes
        # Convert the dataframes to csv files        
        df_overall.to_csv(output_file, index=False)


if __name__ == "__main__":
    main()
    print('Done!')
