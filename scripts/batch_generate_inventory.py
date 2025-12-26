import os
import json
from generate_inventory_item import generate_inventory_item

# -----------------------------
# CONFIG
# -----------------------------
IMAGE_DIR = "images/clean"
OUTPUT_FILE = "inventory/batch_output.json"

# -----------------------------
# BATCH PROCESS
# -----------------------------
items = []

for file in os.listdir(IMAGE_DIR):
    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        image_path = os.path.join(IMAGE_DIR, file)
        print(f"Processing: {file}")

        try:
            item = generate_inventory_item(image_path)
            items.append(item)
        except Exception as e:
            print(f"❌ Failed for {file}: {e}")

# -----------------------------
# SAVE OUTPUT
# -----------------------------
os.makedirs("inventory", exist_ok=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(items, f, indent=2)

print(f"\n✅ Batch inventory saved to {OUTPUT_FILE}")
print(f"Total items processed: {len(items)}")
