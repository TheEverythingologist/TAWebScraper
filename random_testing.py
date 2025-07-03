import os

def delete_empty_yaml_files(directory):
    """
    Recursively delete all .yml/.yaml files that are empty or contain only whitespace.
    """
    deleted_files = []
    skipped_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith((".yaml", ".yml")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        contents = f.read()

                    if not contents.strip():  # Empty or whitespace only
                        try:
                            os.remove(path)
                            deleted_files.append(path)
                            print(f"🗑️ Deleted: {path}")
                        except PermissionError:
                            print(f"🚫 Skipped (in use or permission denied): {path}")
                            skipped_files.append(path)
                except Exception as e:
                    print(f"⚠️ Error reading {path}: {e}")
                    skipped_files.append(path)

    print(f"\n✅ Done. Deleted {len(deleted_files)} file(s). Skipped {len(skipped_files)}.")

# Example usage:
# delete_empty_yaml_files("path/to/your/directory")
delete_empty_yaml_files("C:/Users/TKD12/OneDrive/Desktop/CodingRepos/TAWebScraper/game_data")