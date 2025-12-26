import os
import torch
import clip
from PIL import Image

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
IMAGE_DIR = "images/clean"

LABELS = [
    "a photo of a shirt",
    "a photo of a t-shirt",
    "a photo of pants",
    "a photo of shorts",
    "a photo of shoes",
    "a photo of accessories"
]

PRIMARY_CONFIDENCE_THRESHOLD = 0.50
SECONDARY_CONFIDENCE_THRESHOLD = 0.30
MAX_CONFIDENCE_DIFF = 0.20

# --------------------------------------------------
# LOAD MODEL ONCE
# --------------------------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
text_tokens = clip.tokenize(LABELS).to(device)

# --------------------------------------------------
# VALIDATION FUNCTION
# --------------------------------------------------
def validate_image(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        logits, _ = model(image, text_tokens)
        probs = logits.softmax(dim=-1).cpu().numpy()[0]

    scored = list(zip(LABELS, probs))
    scored.sort(key=lambda x: x[1], reverse=True)

    top_label, top_score = scored[0]
    second_label, second_score = scored[1]

    # Multi-garment detection
    if (
        top_score >= PRIMARY_CONFIDENCE_THRESHOLD
        and second_score >= SECONDARY_CONFIDENCE_THRESHOLD
        and abs(top_score - second_score) <= MAX_CONFIDENCE_DIFF
    ):
        return False, scored, f"Multi-garment detected ({top_label} vs {second_label})"

    return True, scored, top_label

# --------------------------------------------------
# BATCH PROCESS
# --------------------------------------------------
print("\n🔍 Validating images in:", IMAGE_DIR, "\n")

for file in os.listdir(IMAGE_DIR):
    if not file.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        continue

    path = os.path.join(IMAGE_DIR, file)
    print(f"📸 {file}")

    valid, scored, result = validate_image(path)

    for label, prob in scored:
        print(f"   {label:<30}: {prob:.2f}")

    if valid:
        print(f"   ✅ ACCEPTED → {result}\n")
    else:
        print(f"   ❌ REJECTED → {result}")
        print("   👉 Upload ONE garment per image\n")
