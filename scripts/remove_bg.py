import os
from PIL import Image
from app.services.cloth_extractor import extract_cloth

INPUT_DIR = "images/raw"
OUTPUT_DIR = "images/clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for file in os.listdir(INPUT_DIR):
    if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        input_path = os.path.join(INPUT_DIR, file)
        output_path = os.path.join(
            OUTPUT_DIR,
            os.path.splitext(file)[0] + "_cloth.png"
        )

        with Image.open(input_path).convert("RGB") as img:
            output = extract_cloth(img)
            output.save(output_path)

        print(f"🧥 Processed: {file}")

print("🎉 Face removed + background removed.")
