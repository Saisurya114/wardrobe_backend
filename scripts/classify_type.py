import torch
import clip
from PIL import Image

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
IMAGE_PATH = "images/clean/shirt_test.png"

LABELS = [
    "a photo of a shirt",
    "a photo of a t-shirt",
    "a photo of pants",
    "a photo of shorts",
    "a photo of shoes",
    "a photo of accessories"
]

# Validation thresholds (tunable)
PRIMARY_CONFIDENCE_THRESHOLD = 0.50
SECONDARY_CONFIDENCE_THRESHOLD = 0.30
MAX_CONFIDENCE_DIFF = 0.20

# --------------------------------------------------
# LOAD MODEL
# --------------------------------------------------
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

# --------------------------------------------------
# PREPROCESS IMAGE
# --------------------------------------------------
image = preprocess(Image.open(IMAGE_PATH)).unsqueeze(0).to(device)
text = clip.tokenize(LABELS).to(device)

# --------------------------------------------------
# RUN CLIP
# --------------------------------------------------
with torch.no_grad():
    logits_per_image, _ = model(image, text)
    probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]

# --------------------------------------------------
# DISPLAY SCORES
# --------------------------------------------------
print("\nClassification results:\n")

scored = list(zip(LABELS, probs))
scored.sort(key=lambda x: x[1], reverse=True)

for label, prob in scored:
    print(f"{label:<30}: {prob:.2f}")

# --------------------------------------------------
# MULTI-GARMENT VALIDATION
# --------------------------------------------------
top_label, top_score = scored[0]
second_label, second_score = scored[1]

if (
    top_score >= PRIMARY_CONFIDENCE_THRESHOLD
    and second_score >= SECONDARY_CONFIDENCE_THRESHOLD
    and abs(top_score - second_score) <= MAX_CONFIDENCE_DIFF
):
    print("\n❌ REJECTED IMAGE")
    print("Reason: Possible multi-garment photo detected")
    print(
        f"Top match    : {top_label} ({top_score:.2f})\n"
        f"Second match : {second_label} ({second_score:.2f})"
    )
    print("\n👉 Please upload a photo containing ONLY ONE clothing item.")
    exit(1)

# --------------------------------------------------
# ACCEPTED RESULT
# --------------------------------------------------
print("\n✅ ACCEPTED IMAGE")
print(f"Detected TYPE: {top_label} (confidence: {top_score:.2f})")
