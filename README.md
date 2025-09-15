# TAWebScraper
This is a webscraper designed to get most/all data for most/all games and achievements on `trueachievements.com`. All data is pulled and stored as yaml files within the `game_data/` directory.

The script also posesses the functionality to dump all game data into a csv.

## Setting Up the Project Environment (Windows)
This project uses a **virtual environment** to keep dependencies isolated and reproducible.  
We use `setup.bat` to make setup quick and easy.  

### Run setup script
- Navigate to the project directory in your terminal. 
- Run `setup.bat`. This will do the following:
1. Install any and all required modules. Listed in `requirements.txt`.
2. Activate the virtual environment. 


## Running the Script
Running `xbox_ta_scraper.py` runs the webscraper. This should be all that is required to get game data.

### Dumping to csv
To dump all data to a csv file, you will need to edit the column headers in `utils.py` and the `format_game_row` function in `xbox_ta_scraper.py`.
It is currently future work to streamline this process.

## Notes on Running
It is HIGHLY recommended that users use a VPN when running the script as cloudflare can detect too many requests and prevent crucial data from loading. 
Currently, the script is designed with delays built in to stagger requests and be considerate of the TA servers, but nonetheless, cloudflare trips can happen.
A simple way to tell if your IP address is being flagged as throttling is to check `https://www.trueachievements.com/games.aspx`. If no games load, your IP address 
is currently being flagged and you will need to change IP addresses to run the script or simply wait.

This project is for **educational and personal use only**.  
Please do **not use this script to overload or damage TrueAchievements' servers**.  
The author is not responsible for any violation of TrueAchievements’ Terms of Service.

**Please be considerate of TA servers and do NOT run this script more than once every 24 hours.**

### Criteria for Rescan
Games are rescanned if and only if any of the following criteria are met:
* The game has never been scanned before and there is no yaml file for it in `game_data/`.
* The game's TA score has increased or decreased by 2.5%.
* The script detects an error in the game's yaml file.