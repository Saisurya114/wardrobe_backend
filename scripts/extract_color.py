from PIL import Image
import numpy as np
import os

IMAGE_PATH = "images/clean/shirt_test.png"

def extract_dominant_rgb(image_path):
    img = Image.open(image_path).convert("RGBA")
    data = np.array(img)

    # Remove transparent pixels
    rgb_pixels = data[data[:, :, 3] > 0][:, :3]

    # Compute average RGB
    avg_color = np.mean(rgb_pixels, axis=0)
    return tuple(avg_color.astype(int))

def map_color_group(rgb):
    r, g, b = rgb

    # Neutral detection (very important)
    if abs(r - g) < 20 and abs(g - b) < 20:
        if r > 200:
            return "white"
        if r < 80:
            return "black"
        return "neutral"

    # Dominant channel logic (with margin)
    if r > g + 25 and r > b + 25:
        return "red"
    if g > r + 25 and g > b + 25:
        return "green"
    if b > r + 25 and b > g + 25:
        return "blue"

    return "neutral"



rgb = extract_dominant_rgb(IMAGE_PATH)
group = map_color_group(rgb)

print("Detected Color:")
print("RGB :", rgb)
print("Group:", group)
