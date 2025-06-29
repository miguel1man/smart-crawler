import json
import os
import re


def normalize_string(s):
    """Normalize string by lowercasing and removing extra whitespace."""
    return re.sub(r"\s+", " ", s).strip().lower()


def classify_products(file_path=None):
    output_folder = "output"
    configs_folder = "configs"

    if file_path:
        latest_file_path = file_path
    else:
        # Find the latest file in the output folder
        output_files = [f for f in os.listdir(output_folder) if f.endswith(".json")]
        if not output_files:
            print("No files found in the output folder.")
            return

        latest_file = max(
            output_files, key=lambda f: os.path.getmtime(os.path.join(output_folder, f))
        )
        latest_file_path = os.path.join(output_folder, latest_file)

    # Read the alternative names
    alternative_names_path = os.path.join(configs_folder, "alternative_names.json")
    with open(alternative_names_path, "r") as f:
        alternative_names_data = json.load(f)

    # Create a mapping from normalized alternative name to product ID
    name_to_id_map = {}
    for product in alternative_names_data:
        for name in product["alternative_names"]:
            normalized_name = normalize_string(name)
            name_to_id_map[normalized_name] = product["id"]

    # Read the scraped data and classify it
    with open(latest_file_path, "r") as f:
        scraped_data = json.load(f)

    for item in scraped_data:
        normalized_item_name = normalize_string(item["Name"])
        item["product_id"] = name_to_id_map.get(normalized_item_name, "")

    # Write the classified data back to the same file
    with open(latest_file_path, "w") as f:
        json.dump(scraped_data, f, indent=2)


if __name__ == "__main__":
    classify_products()
