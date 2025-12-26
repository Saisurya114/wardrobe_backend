import json

with open("inventory/wardrobe.json") as f:
    wardrobe = json.load(f)

print("Your wardrobe contains:")
for item in wardrobe:
    print(f"- {item['category']} ({item['color']}, {item['formality']})")
