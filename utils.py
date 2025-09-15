import pyautogui

class Utils:
    output_file = 'overall_data.csv'
    columns_list = ["Game Name",
                    "TA",
                    "GS",
                    "Rating",
                    "Number of Players",
                    "Completion Percentage",
                    "Completion Time (min)",
                    "Completion TIme (max)",
                    "TA Ratio",
                    "Release Date",
                    "Install Size",
                    "Developer",
                    "Publisher"]
    
    pyautogui.FAILSAFE = True
    def stay_awake():
        pyautogui.moveRel(0, 15)
        pyautogui.press('left')
        pyautogui.moveRel(0, -15)