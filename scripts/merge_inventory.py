import json
import os

WARDROBE_FILE = "inventory/wardrobe.json"
BATCH_FILE = "inventory/batch_output.json"


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def generate_smart_id(category, item_type, existing_items):
    """
    Generates IDs like:
    top_shirt_01
    bottom_pants_02
    """
    # topwear -> top, bottomwear -> bottom
    category_prefix = category.replace("wear", "")
    prefix = f"{category_prefix}_{item_type}"

    existing_ids = [
        item["id"] for item in existing_items
        if item.get("id", "").startswith(prefix)
    ]

    next_seq = len(existing_ids) + 1
    return f"{prefix}_{str(next_seq).zfill(2)}"


def merge_inventory():
    wardrobe = load_json(WARDROBE_FILE, [])
    batch_items = load_json(BATCH_FILE, [])

    existing_images = {item["image"] for item in wardrobe}

    new_items = []

    for item in batch_items:
        # Skip duplicates (same image already in wardrobe)
        if item["image"] in existing_images:
            continue

        # Generate smart ID using existing + new items
        smart_id = generate_smart_id(
            item["category"],
            item["type"],
            wardrobe + new_items
        )

        item["id"] = smart_id
        new_items.append(item)

    if not new_items:
        print("ℹ️ No new items to add.")
        return

    wardrobe.extend(new_items)
    save_json(WARDROBE_FILE, wardrobe)

    print(f"✅ Added {len(new_items)} new items to wardrobe.")
    print(f"📦 Total items in wardrobe: {len(wardrobe)}")


if __name__ == "__main__":
    merge_inventory()
