Perfect 👍
Below is a **clean, beginner-friendly `plan.md`** you can keep in your repo.
It explains **what the project is**, **how data flows**, and **which commands to run + what they do** — exactly for *future you* or a new contributor.

You can **copy–paste this entire content** into `docs/plan.md`.

---

# 🧥 AI Stylist – Project Plan & Run Guide

This document explains **how the AI Stylist project works**, the **overall flow**, and **which commands to run at each step**.

The goal of this project is to build a **personal AI stylist** that:

* Understands my wardrobe
* Uses ONLY my existing clothes
* Suggests outfits based on context (occasion, weather, time)
* Works on **iOS, Android, and Web**

---

## 📁 Project Structure

```
ai-stylist/
│
├── backend/              # Python – AI, vision, inventory
│   ├── scripts/
│   ├── images/
│   ├── inventory/
│   ├── venv/
│   └── requirements.txt
│
├── frontend/             # Flutter – UI (iOS, Android, Web)
│   └── ai_stylist_app/
│
├── docs/
│   └── plan.md           # This file
│
└── README.md
```

---

## 🧠 High-Level System Flow

```
Raw clothing photos
      ↓
Background removal
      ↓
Clean images (transparent)
      ↓
Vision-based validation (single garment only)
      ↓
Color + type classification
      ↓
Structured inventory (JSON)
      ↓
AI reasoning (outfit suggestions)
      ↓
UI (mobile + web)
```

---

## 🔧 Backend Setup (One-time)

### 1️⃣ Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

**What this does**

* Creates an isolated Python environment
* Prevents dependency conflicts
* Keeps the project clean

---

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

**What this does**

* Installs all required Python libraries:

  * background removal
  * image processing
  * AI models
  * OpenAI client (later)

---

## 🖼️ Image Processing Pipeline

### Folder meanings

```
images/raw/    → Original uploaded photos
images/clean/  → Background-removed images (used by AI)
```

---

### 3️⃣ Remove background from all raw images

```bash
python scripts/remove_bg.py
```

**What this does**

* Reads all images from `images/raw/`
* Removes background using AI
* Saves transparent images to `images/clean/`

**Why**

* Ensures clean color detection
* Removes noise (walls, people, floor)

---

## 👁️ Vision Validation & Inventory Generation

### Rule enforced

> **One image must contain only ONE clothing item**

Multi-garment images are rejected automatically.

---

### 4️⃣ Batch generate inventory items

```bash
python scripts/batch_generate_inventory.py
```

**What this does**

* Reads all images from `images/clean/`
* Validates each image (single garment check)
* Detects:

  * clothing type (shirt, pants, shoes, accessories)
  * dominant color (RGB + group)
* Outputs structured data to:

  ```
  inventory/batch_output.json
  ```

**Invalid images**

* Are skipped
* Printed as errors
* Never added to inventory

---

## 🧾 Inventory Persistence

### 5️⃣ Merge batch output into wardrobe

```bash
python scripts/merge_inventory.py
```

**What this does**

* Reads existing `inventory/wardrobe.json`
* Reads new `batch_output.json`
* Avoids duplicates using image path
* Generates smart IDs like:

  ```
  top_shirt_01
  bottom_pants_01
  shoes_01
  ```
* Updates `wardrobe.json` safely

**Why**

* `wardrobe.json` is the single source of truth
* Enables outfit recommendations

---

## 🤖 AI Outfit Recommendation (Later)

### Input to AI

* `wardrobe.json` (your clothes)
* User context:

  * occasion
  * weather
  * time of day

### Output from AI

* Outfit suggestions
* Uses ONLY existing inventory
* Explains reasoning
* No hallucinated clothes

(Requires OpenAI API key – added later)

---

## 🎨 Frontend (Flutter – Single Codebase)

### One app → three platforms

* iOS
* Android
* Web

### Why Flutter

* One codebase
* Consistent UI
* Fast iteration
* Ideal for AI-driven apps

---

### Create Flutter app (one-time)

```bash
cd frontend
flutter create ai_stylist_app
cd ai_stylist_app
flutter run -d chrome
```

**What this does**

* Creates a Flutter app
* Runs it as a web app
* Same code works for mobile later

---

## 🔒 Key Design Principles

* Vision logic ≠ UI logic
* Inventory is **strict & validated**
* AI is used only for **reasoning**, not guessing
* No duplicated code
* One image = one clothing item

---

## 🚀 Current Project Status

✅ Vision pipeline
✅ Inventory generation
✅ Validation rules
✅ Persistent wardrobe
✅ Ready for UI integration
⏳ AI API (planned)

---

## 📝 Notes for Future

* Add weather & occasion filters
* Add confidence scoring
* Add history (avoid repeating outfits)
* Add upload UI
* Add backend API (FastAPI)

---

## ✅ How to run everything (quick reference)

```bash
# Activate environment
source venv/bin/activate

# Remove background
python scripts/remove_bg.py

# Generate inventory
python scripts/batch_generate_inventory.py

# Merge into wardrobe
python scripts/merge_inventory.py
```

---

**This file is the single reference for understanding and running the project.**

---

If you want, next I can:

* review this plan with you
* help you wire Flutter to `wardrobe.json`
* design the first UI screen
* or convert this into a README for GitHub

Just tell me 👍
