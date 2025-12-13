import json

filename = '/caps_crawler/caps_pages.jsonl'

try:
    with open(filename, 'r') as file:
        for line in file:
            json_obj = json.loads(line)

            print(f"{json_obj}\n\n")
            continue

except Exception as e:
    print(f"ERROR: {e}")