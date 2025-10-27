#!/usr/bin/env python3
"""
Script to convert bandcamp_bilbaotags_clean.csv to JSON format
"""

import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    """
    Convert a CSV file to JSON format

    Args:
        csv_file_path: Path to the input CSV file
        json_file_path: Path to the output JSON file
    """
    data = []

    # Read CSV file
    with open(csv_file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        # Convert each row to a dictionary and add to data list
        for row in csv_reader:
            data.append(row)

    # Write JSON file
    with open(json_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2, ensure_ascii=False)

    print(f"Successfully converted {csv_file_path} to {json_file_path}")
    print(f"Total records: {len(data)}")

if __name__ == "__main__":
    csv_file = "bandcamp_bilbaotags_clean.csv"
    json_file = "bandcamp_bilbaotags_clean.json"

    csv_to_json(csv_file, json_file)
