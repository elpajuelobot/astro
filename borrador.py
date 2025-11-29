import json

with open("astro_promt.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(data['content'])
