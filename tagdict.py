import yaml

class TagDict:
    yaml_path = "C:/Users/TKD12/OneDrive/Desktop/CodingRepos/TAWebScraper/tagdict.yaml"

    def __init__(self):
        self.tagdict = None
        self.load_yaml()

    def update_yaml(self, data_to_append: dict[str, list[str]]):
        with open(self.yaml_path, 'a') as file:
            yaml_text = yaml.dump(data_to_append)
            file.write(yaml_text)

    def load_yaml(self):
        with open(self.yaml_path, 'r') as file:
            temp_data = yaml.safe_load(file)
        self.tagdict = temp_data
        

if __name__ == '__main__':
    tester = TagDict()
    # tester.update_yaml(data_to_append={'flg-50000000': ['Offline Game Mode', 'Single Player']})
    tester.load_yaml()
    print("Done!")