import json
import math

def distribute_levels(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_topics = len(data)
    if total_topics == 0:
        print("No topics found in the JSON.")
        return

    # Distribute as evenly as possible
    items_per_level = math.ceil(total_topics / 3)

    for i, item in enumerate(data):
        level = (i // items_per_level) + 1
        # Make sure we don't exceed level 3
        if level > 3:
            level = 3
        item["Level"] = str(level)

    # Use ensure_ascii=False so that non-ASCII characters (e.g., Arabic) remain readable
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_filename = "JS/JS4.json"  # or the correct path to your file
    output_filename = "JS4.json"
    distribute_levels(input_filename, output_filename)
    print(f"Levels have been distributed and saved to '{output_filename}'.")
