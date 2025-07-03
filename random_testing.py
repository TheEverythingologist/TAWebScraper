import os

def delete_empty_yaml_files(directory):
    """
    Deletes all empty .yaml and .yml files in the given directory.
    An empty file is defined as either 0 bytes or containing only whitespace.
    """
    deleted_files = []

    for filename in os.listdir(directory):
        if filename.lower().endswith((".yaml", ".yml")):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as file:
                    content = file.read()
                    if not content.strip():  # File is empty or only whitespace
                        os.remove(filepath)
                        deleted_files.append(filename)
                        print(f"Deleted: {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")

    if not deleted_files:
        print("No empty YAML files found.")
    else:
        print(f"\nTotal deleted: {len(deleted_files)}")

# Example usage:
# delete_empty_yaml_files("path/to/your/directory")
delete_empty_yaml_files("C:/Users/TKD12/OneDrive/Desktop/CodingRepos/TAWebScraper/game_data")