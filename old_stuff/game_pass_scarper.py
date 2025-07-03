import requests
from bs4 import BeautifulSoup
import csv
import re

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
        time_val = (float(time_val[1]) + float(time_val[0])) / 2
    except:
        if time_val == ['1000+']:
            time_val = 1000
        else:
            print("Still broken!")
            print(time_val)
    return str(time_val)


# Create lists to store the game names and completion times
games = []
completion_times = []
ta_diffs = []
diff_rates = []

for page in range(1, 6):
    url = f'https://www.trueachievements.com/xbox-game-pass/games?page={page}'

    # Send a GET request to the URL
    response = requests.get(url)

    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the parent element containing the game information
    parent_element = soup.find('div', {'id': 'oGameListContent', 'class': 'listcontent'})

    # Find all child elements with class 'gamebox'
    game_boxes = parent_element.find_all('tr', {'class': 'even'}) + parent_element.find_all('tr', {'class': 'odd'})

    # Iterate through each game box
    for game_box in game_boxes:
        # Find the element containing the game name
        name_element = (game_box.find('td', {'class': 'game'})).find('a').text

        score_elemet = game_box.find('td', {'class': 'score'}).text
        score_elemet = score_elemet.split(' ')

        ta_score = str_to_int(score_elemet[0])

        gs_score = string_to_num(score_elemet[1])

        ta_diff = str(ta_score - gs_score)

        time_element = game_box.find('a', {'title': "View all time estimates for this game"})
        if time_element is None:
            time_element = "None"
            diff_rate = "None"
        else:
            time_element = time_element.text
            time_element = adjust_time(time_element)
            diff_rate = str(float(ta_diff) / float(time_element))


        # Add the game nanme to the list
        games.append(name_element)
        completion_times.append(time_element)
        ta_diffs.append(ta_diff)

        diff_rates.append(diff_rate)

# Combine the game names and completion times into a list of lists
game_data = list(zip(games, completion_times, ta_diffs, diff_rates))

# Write the game names and completion times to a CSV file
with open('xbox_game_pass_games.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file, delimiter=',')
    writer.writerow(['Game', 'Estimated Completion Time', 'TA Diff', 'Diff Rates'])
    for i in range(len(games)):
        writer.writerow([games[i].encode('utf-8').decode('utf-8'), 
                         completion_times[i].encode('utf-8').decode('utf-8'), 
                         ta_diffs[i].encode('utf-8').decode('utf-8'),
                         diff_rates[i].encode('utf-8').decode('utf-8')])


print('Done!')
