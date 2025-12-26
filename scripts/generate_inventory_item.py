import json
import uuid
from PIL import Image
import numpy as np
import torch
import clip

# -----------------------------
# CONFIG
# -----------------------------
 #IMAGE_PATH = "images/clean/shirt_test.png"

# -----------------------------
# COLOR EXTRACTION
# -----------------------------
def extract_dominant_rgb(image_path):
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)

    rgb_pixels = data[data[:, :, 3] > 0][:, :3]
    avg_color = np.mean(rgb_pixels, axis=0)

    return tuple(int(x) for x in avg_color)



def map_color_group(rgb):
    r, g, b = rgb

    if abs(r - g) < 20 and abs(g - b) < 20:
        if r > 200:
            return "white"
        if r < 80:
            return "black"
        return "neutral"

    if r > g + 25 and r > b + 25:
        return "red"
    if g > r + 25 and g > b + 25:
        return "green"
    if b > r + 25 and b > g + 25:
        return "blue"

    return "neutral"


def map_color_name(rgb):
    r, g, b = rgb

    if abs(r - g) < 20 and abs(g - b) < 20:
        if r > 200:
            return "off white"
        if r < 80:
            return "black"
        return "beige"

    if b > r + 25:
        return "blue"
    if r > g + 25:
        return "red"
    if g > r + 25:
        return "green"

    return "neutral"


# -----------------------------
# TYPE CLASSIFICATION (CLIP)
# -----------------------------
def classify_type(image_path):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model, preprocess = clip.load("ViT-B/32", device=device)

    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    labels = [
        "a photo of a shirt",
        "a photo of a t-shirt",
        "a photo of pants",
        "a photo of shorts",
        "a photo of shoes",
        "a photo of accessories"
    ]

    text = clip.tokenize(labels).to(device)

    with torch.no_grad():
        logits, _ = model(image, text)
        probs = logits.softmax(dim=-1).cpu().numpy()[0]

    scored = list(zip(labels, probs))
    scored.sort(key=lambda x: x[1], reverse=True)

    top_label, top_score = scored[0]
    second_label, second_score = scored[1]

    # -----------------------------
    # MULTI-GARMENT VALIDATION
    # -----------------------------
    if (
        top_score >= 0.50 and
        second_score >= 0.30 and
        abs(top_score - second_score) <= 0.20
    ):
        raise ValueError(
            f"Multi-garment image detected "
            f"({top_label}: {top_score:.2f}, {second_label}: {second_score:.2f})"
        )

    return top_label



def map_inventory_type(label):
    if "shirt" in label and "t-shirt" not in label:
        return "topwear", "shirt"
    if "t-shirt" in label:
        return "topwear", "tshirt"
    if "pants" in label:
        return "bottomwear", "pants"
    if "shorts" in label:
        return "bottomwear", "shorts"

    return "unknown", "unknown"


# -----------------------------
# INVENTORY GENERATION
# -----------------------------
def generate_inventory_item(image_path):
    rgb = extract_dominant_rgb(image_path)
    color_group = map_color_group(rgb)
    color_name = map_color_name(rgb)

    label = classify_type(image_path)
    category, item_type = map_inventory_type(label)

    item = {
        "id": f"auto_{uuid.uuid4().hex[:6]}",
        "category": category,
        "type": item_type,
        "subtype": "unknown",
        "color": {
            "name": color_name,
            "rgb": list(rgb),
            "group": color_group
        },
        "fit": "unknown",
        "formality": "unknown",
        "season": [],
        "image": image_path
    }

    return item

# Allow reuse in other scripts
if __name__ == "__main__":
    test_image = "images/clean/shirt_test.png"
    item = generate_inventory_item(test_image)
    print(json.dumps(item, indent=2))
