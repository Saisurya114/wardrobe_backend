# AI Stylist Backend - Complete Project Documentation

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [What We Achieved](#what-we-achieved)
3. [Technology Stack & Libraries](#technology-stack--libraries)
4. [Project Structure](#project-structure)
5. [File-by-File Explanation](#file-by-file-explanation)
6. [API Endpoint Details](#api-endpoint-details)
7. [JSON Response Format](#json-response-format)
8. [Processing Pipeline](#processing-pipeline)
9. [Temporary Inventory Workflow](#temporary-inventory-workflow)
10. [Permanent Inventory & Database](#permanent-inventory--database)
11. [How to Run the Application](#how-to-run-the-application)
12. [Testing the API](#testing-the-api)

---

## 🎯 Project Overview

**AI Stylist Backend** is a FastAPI-based REST API that processes clothing images to create a digital wardrobe inventory. The system:

- Accepts clothing images (user wearing outfit OR clothing item photo)
- Removes background using AI (rembg/U²-Net)
- Extracts clothing type using CLIP (OpenAI's vision model)
- Detects dominant color from the processed image
- Generates structured inventory data with smart IDs
- Returns both the processed image and inventory metadata

**Primary Goal (Phase 1 - MVP):** Create a backend API that accepts an image and returns a cloth-only PNG with transparent background, suitable for wardrobe digitization.

---

## ✅ What We Achieved

### Core Features Implemented:

1. **Image Processing Pipeline**
   - Background removal using rembg (U²-Net)
   - Face detection and cropping (optional, graceful fallback)
   - RGBA format conversion (transparent background)

2. **AI-Powered Classification**
   - Clothing type detection using CLIP (shirt, t-shirt, pants, shorts, shoes, accessories)
   - Multi-garment validation (rejects images with multiple items)
   - Category mapping (topwear, bottomwear, footwear, accessories)

3. **Color Analysis**
   - Dominant RGB color extraction (ignoring transparent pixels)
   - Color name mapping (blue, red, green, black, white, beige, neutral)
   - Color group classification (white, black, red, green, blue, neutral)

4. **Smart Inventory Generation**
   - Sequential ID generation (format: `{category}_{type}_{number}`)
   - Examples: `topwear_shirt_01`, `bottomwear_pants_02`, `footwear_shoes_01`
   - Reads existing wardrobe to avoid ID conflicts

5. **REST API**
   - FastAPI-based endpoint: `POST /api/extract-cloth`
   - JSON response with base64-encoded image and inventory data
   - Comprehensive error handling
   - Input validation

---

## 📚 Technology Stack & Libraries

### Core Framework
- **FastAPI** (v0.127.0+)
  - Modern, fast web framework for building APIs
  - Automatic API documentation (Swagger UI)
  - Type hints and validation
  - Why: Best performance, easy to use, great documentation

- **Uvicorn** (v0.39.0+)
  - ASGI server for running FastAPI
  - Hot reload for development
  - Why: Standard server for FastAPI, production-ready

### Image Processing
- **rembg** (v2.0.0+)
  - Background removal using U²-Net deep learning model
  - Why: Reliable, fast, no human parsing needed (unlike SCHP)

- **Pillow (PIL)** (v10.0.0+)
  - Image manipulation and format conversion
  - Why: Industry standard for Python image processing

- **numpy** (v1.24.0+)
  - Numerical operations on image arrays
  - Why: Required by image processing libraries

### AI/ML
- **torch (PyTorch)** (v2.0.0+)
  - Deep learning framework
  - Why: Required by CLIP for image classification

- **torchvision** (v0.15.0+)
  - Computer vision utilities for PyTorch
  - Why: Image preprocessing for CLIP

- **CLIP** (from OpenAI GitHub)
  - Vision-language model for image classification
  - Why: Accurate clothing type detection without training custom models

### Face Detection
- **mediapipe** (v0.10.0+)
  - Face detection for cropping below face
  - Why: Optional feature to remove person from clothing photos

### Utilities
- **python-multipart** (v0.0.6+)
  - File upload handling for FastAPI
  - Why: Required for multipart form-data (image uploads)

- **requests** (v2.31.0+)
  - HTTP library for testing
  - Why: Used in test scripts

- **SQLAlchemy** (v2.0.0+)
  - SQL toolkit and ORM for database operations
  - Why: Provides database abstraction and models for SQLite

---

## 📁 Project Structure

```
Backend/
├── app/                          # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI app entry point
│   ├── api/                     # API routes
│   │   ├── __init__.py
│   │   └── cloth.py             # Cloth extraction endpoint
│   └── services/                # Business logic layer
│       ├── __init__.py
│       ├── cloth_extractor.py   # Main image processing
│       ├── bg_removal.py        # Background removal service
│       ├── face_crop.py          # Face detection & cropping
│       ├── color_extractor.py   # Color analysis
│       ├── type_classifier.py   # CLIP-based classification
│       └── inventory_generator.py # Inventory creation
├── images/                       # Image storage
│   ├── raw/                     # Original uploaded images
│   ├── clean/                   # Processed images (transparent BG) - legacy
│   ├── temp/                    # Temporary images (pending confirmation)
│   └── permanent/               # Permanent images (confirmed items)
├── inventory/                   # Inventory data
│   ├── inventory.db            # SQLite database (permanent storage)
│   ├── wardrobe.json           # Legacy JSON storage (backward compatibility)
│   ├── temporary_inventory.json # Temporary items (pending confirmation)
│   └── batch_output.json       # Batch processing output
├── scripts/                     # Utility scripts (legacy)
│   ├── batch_generate_inventory.py
│   ├── classify_type.py
│   ├── extract_color.py
│   └── ...
├── test_api.py                  # API testing script
├── requirements.txt             # Python dependencies
├── API_TESTING_GUIDE.md        # Testing instructions
└── PROJECT_DOCUMENTATION.md     # This file
```

---

## 📄 File-by-File Explanation

### Application Files

#### `app/main.py`
**Purpose:** FastAPI application entry point
- Creates FastAPI app instance
- Includes API routers
- Defines health check endpoint (`GET /`)
- **Why it exists:** Central configuration point for the API

#### `app/api/cloth.py`
**Purpose:** API endpoint handler for cloth extraction
- Defines `POST /api/extract-cloth` endpoint
- Handles file upload validation
- Orchestrates image processing and inventory generation
- Returns JSON response with image and metadata
- **Why it exists:** Thin API layer that delegates to services

#### `app/services/cloth_extractor.py`
**Purpose:** Main image processing service
- Extracts cloth from image bytes
- Removes background using rembg
- Optionally crops below face
- Converts to RGBA format
- Returns PNG bytes
- **Why it exists:** Core image processing logic

#### `app/services/bg_removal.py`
**Purpose:** Background removal service
- Wrapper around rembg for background removal
- Ensures RGBA output
- **Why it exists:** Reusable background removal function

#### `app/services/face_crop.py`
**Purpose:** Face detection and cropping
- Uses MediaPipe to detect faces
- Crops image below detected face
- Returns original if no face detected
- **Why it exists:** Removes person from clothing photos

#### `app/services/color_extractor.py`
**Purpose:** Color analysis from processed image
- `extract_dominant_rgb()`: Extracts average RGB (ignoring transparent pixels)
- `map_color_group()`: Maps RGB to color groups (white, black, red, green, blue, neutral)
- `map_color_name()`: Maps RGB to color names (blue, red, green, black, off white, beige, neutral)
- **Why it exists:** Color detection for inventory metadata

#### `app/services/type_classifier.py`
**Purpose:** Clothing type classification using CLIP
- `classify_type()`: Uses CLIP to classify clothing type
- `map_inventory_type()`: Maps CLIP labels to inventory categories
- Model caching for performance
- Multi-garment validation
- **Why it exists:** AI-powered clothing type detection

#### `app/services/inventory_generator.py`
**Purpose:** Generates complete inventory items
- `generate_smart_id()`: Creates sequential IDs (e.g., `topwear_shirt_01`)
- `generate_inventory_item()`: Combines all processing into inventory format
- Reads existing wardrobe to generate unique IDs
- **Why it exists:** Orchestrates color extraction, classification, and ID generation

#### `app/services/temporary_inventory.py`
**Purpose:** Manages temporary inventory items before confirmation
- `save_to_temporary_inventory()`: Saves item to temporary storage after upload
- `get_temporary_item()`: Retrieves temporary item for review
- `update_temporary_item()`: Updates temporary item when user edits
- `confirm_and_move_to_wardrobe()`: Legacy method (moves to wardrobe.json)
- `delete_temporary_item()`: Removes temporary item if user cancels
- **Why it exists:** Allows user review and editing before final confirmation

#### `app/services/image_service.py`
**Purpose:** Manages image file storage
- `save_temp_image()`: Saves image to temporary storage (`images/temp/`)
- `save_permanent_image()`: Saves image to permanent storage (`images/permanent/`)
- `move_temp_to_permanent()`: Moves image from temp to permanent
- `delete_temp_image()`: Deletes temporary image
- `delete_permanent_image()`: Deletes permanent image
- `get_image_url()`: Generates image URL from path
- **Why it exists:** Centralized image file management

#### `app/services/inventory_service.py`
**Purpose:** Manages permanent inventory in SQLite database
- `create_inventory_item()`: Creates new inventory item in database
- `get_inventory_item()`: Retrieves item by ID
- `get_all_inventory_items()`: Lists all items with pagination
- `update_inventory_item()`: Updates item fields
- `delete_inventory_item()`: Deletes item and associated image
- `save_from_temporary()`: Saves temporary item to permanent database
- **Why it exists:** Database operations for permanent inventory storage

#### `app/models.py`
**Purpose:** SQLAlchemy database models
- `InventoryItem`: Canonical model for inventory items
- `init_db()`: Initialize database and create tables
- `get_db()`: Database session dependency
- **Why it exists:** Database schema and ORM definitions

### Configuration Files

#### `requirements.txt`
**Purpose:** Python package dependencies
- Lists all required libraries with versions
- **Why it exists:** Ensures consistent environment setup

### Utility Files

#### `test_api.py`
**Purpose:** Simple API testing script
- Uploads image to API
- Decodes base64 response
- Saves processed image
- Displays inventory data
- **Why it exists:** Quick way to test the API without Postman/curl

### Data Directories

#### `images/raw/`
**Purpose:** Stores original uploaded images
- Input images from users
- **Why it exists:** Archive of original photos

#### `images/clean/`
**Purpose:** Stores processed images (transparent background)
- Output from background removal
- **Why it exists:** Processed images for inventory

#### `inventory/inventory.db`
**Purpose:** SQLite database for permanent inventory storage
- Stores all confirmed clothing items with metadata
- Used for ID generation (prevents duplicates)
- **Why it exists:** Primary database for wardrobe data (replaces wardrobe.json)

#### `inventory/wardrobe.json`
**Purpose:** Legacy JSON storage (backward compatibility)
- Kept for migration purposes
- New items should use SQLite database
- **Why it exists:** Backward compatibility with existing data

#### `inventory/temporary_inventory.json`
**Purpose:** Temporary storage for pending inventory items
- Stores items waiting for user review and confirmation
- Includes processed image (base64) and inventory metadata
- Items are moved to SQLite database upon confirmation
- **Why it exists:** Allows user to review and edit before final save

#### `images/temp/`
**Purpose:** Temporary image storage
- Stores processed images for pending items
- Images are moved to permanent storage upon confirmation
- **Why it exists:** Temporary file storage before confirmation

#### `images/permanent/`
**Purpose:** Permanent image storage
- Stores confirmed inventory item images
- Filenames match inventory item IDs
- **Why it exists:** Permanent storage for confirmed items

---

## 🔌 API Endpoint Details

### `POST /api/extract-cloth`

**Description:** Extracts cloth from uploaded image, processes it, and saves to temporary inventory.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Field name: `file`
- Accepted formats: `jpg`, `jpeg`, `png`, `webp`

**Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body: JSON with `success`, `temp_id`, `image`, and `inventory` fields
- **Note:** Item is automatically saved to `temporary_inventory.json`

**Error Responses:**
- `400 Bad Request`: Invalid file type, empty file, or multi-garment detected
- `500 Internal Server Error`: Processing failure

---

### `GET /api/temporary-inventory/{temp_id}`

**Description:** Retrieve a temporary inventory item for review.

**Request:**
- Method: `GET`
- Path parameter: `temp_id` (temporary ID from upload response)

**Response:**
- Status: `200 OK`
- Body: Complete temporary item including image and inventory data

**Error Responses:**
- `404 Not Found`: Temporary item not found

---

### `PUT /api/temporary-inventory/{temp_id}`

**Description:** Update temporary inventory item (user edits before confirmation).

**Request:**
- Method: `PUT`
- Path parameter: `temp_id`
- Body: JSON with fields to update (all optional):
  ```json
  {
    "category": "topwear",
    "type": "shirt",
    "subtype": "casual",
    "color": {"name": "blue", "rgb": [45, 78, 120], "group": "blue"},
    "fit": "regular",
    "formality": "casual",
    "season": ["summer", "spring"]
  }
  ```

**Response:**
- Status: `200 OK`
- Body: Updated temporary item

**Error Responses:**
- `400 Bad Request`: No fields provided for update
- `404 Not Found`: Temporary item not found

---

### `POST /api/temporary-inventory/{temp_id}/confirm`

**Description:** Confirm and move temporary item to wardrobe.json.

**Request:**
- Method: `POST`
- Path parameter: `temp_id`

**Response:**
- Status: `200 OK`
- Body:
  ```json
  {
    "success": true,
    "message": "Item added to wardrobe",
    "item": { /* confirmed inventory item */ }
  }
  ```

**Error Responses:**
- `404 Not Found`: Temporary item not found

**Note:** Item is moved from `temporary_inventory.json` to `wardrobe.json` and removed from temporary storage.

---

### `DELETE /api/temporary-inventory/{temp_id}`

**Description:** Delete temporary inventory item (user cancelled).

**Request:**
- Method: `DELETE`
- Path parameter: `temp_id`

**Response:**
- Status: `200 OK`
- Body:
  ```json
  {
    "success": true,
    "message": "Temporary item deleted"
  }
  ```

**Error Responses:**
- `404 Not Found`: Temporary item not found

**Note:** Item is removed from `temporary_inventory.json` without saving to wardrobe.

---

## 📦 JSON Response Format

### Success Response Structure (POST /api/extract-cloth)

```json
{
  "success": true,
  "temp_id": "temp_abc123def456",
  "image": {
    "data": "iVBORw0KGgoAAAANSUhEUgAA...",  // base64-encoded PNG string
    "format": "png",
    "media_type": "image/png"
  },
  "inventory": {
    "id": "topwear_shirt_01",
    "category": "topwear",
    "type": "shirt",
    "subtype": "unknown",
    "color": {
      "name": "blue",
      "rgb": [45, 78, 120],
      "group": "blue"
    },
    "fit": "unknown",
    "formality": "unknown",
    "season": [],
    "image": null
  }
}
```

**Note:** The `temp_id` is used for subsequent operations (review, edit, confirm, delete).

### Field Explanations

#### Top Level
- **`success`**: Boolean indicating successful processing
- **`image`**: Processed image data
  - **`data`**: Base64-encoded PNG string (transparent background)
  - **`format`**: Always `"png"`
  - **`media_type`**: Always `"image/png"`
- **`inventory`**: Inventory metadata object

#### Inventory Object
- **`id`**: Smart ID in format `{category}_{type}_{number}` (e.g., `topwear_shirt_01`)
- **`category`**: Clothing category (`topwear`, `bottomwear`, `footwear`, `accessories`, `unknown`)
- **`type`**: Specific type (`shirt`, `tshirt`, `pants`, `shorts`, `shoes`, etc.)
- **`subtype`**: Currently always `"unknown"` (reserved for future use)
- **`color`**: Color information object
  - **`name`**: Human-readable color name (`blue`, `red`, `green`, `black`, `off white`, `beige`, `neutral`)
  - **`rgb`**: Array of 3 integers `[r, g, b]` (0-255 range)
  - **`group`**: Color group (`white`, `black`, `red`, `green`, `blue`, `neutral`)
- **`fit`**: Currently `"unknown"` (reserved for future use)
- **`formality`**: Currently `"unknown"` (reserved for future use)
- **`season`**: Empty array `[]` (reserved for future use)
- **`image`**: Always `null` in API response (used in saved inventory files)

### Example Responses

#### Shirt Example
```json
{
  "success": true,
  "temp_id": "temp_abc123def456",
  "image": {
    "data": "iVBORw0KGgoAAAANSUhEUgAA...",
    "format": "png",
    "media_type": "image/png"
  },
  "inventory": {
    "id": "topwear_shirt_01",
    "category": "topwear",
    "type": "shirt",
    "subtype": "unknown",
    "color": {
      "name": "blue",
      "rgb": [45, 78, 120],
      "group": "blue"
    },
    "fit": "unknown",
    "formality": "unknown",
    "season": [],
    "image": null
  }
}
```

#### T-Shirt Example
```json
{
  "success": true,
  "temp_id": "temp_xyz789ghi012",
  "image": {
    "data": "iVBORw0KGgoAAAANSUhEUgAA...",
    "format": "png",
    "media_type": "image/png"
  },
  "inventory": {
    "id": "topwear_tshirt_01",
    "category": "topwear",
    "type": "tshirt",
    "subtype": "unknown",
    "color": {
      "name": "off white",
      "rgb": [245, 240, 235],
      "group": "white"
    },
    "fit": "unknown",
    "formality": "unknown",
    "season": [],
    "image": null
  }
}
```

#### Pants Example
```json
{
  "success": true,
  "temp_id": "temp_mno345pqr678",
  "image": {
    "data": "iVBORw0KGgoAAAANSUhEUgAA...",
    "format": "png",
    "media_type": "image/png"
  },
  "inventory": {
    "id": "bottomwear_pants_01",
    "category": "bottomwear",
    "type": "pants",
    "subtype": "unknown",
    "color": {
      "name": "black",
      "rgb": [25, 25, 30],
      "group": "black"
    },
    "fit": "unknown",
    "formality": "unknown",
    "season": [],
    "image": null
  }
}
```

### Error Response Format

#### Multi-garment Detected (400)
```json
{
  "detail": "Multi-garment image detected. Top: a photo of a shirt (0.65), Second: a photo of a pants (0.52)"
}
```

#### Invalid File Type (400)
```json
{
  "detail": "Invalid file type. Allowed types: image/jpeg, image/jpg, image/png, image/webp"
}
```

---

## 🔄 Processing Pipeline

### Step-by-Step Flow

When a user uploads an image to `POST /api/extract-cloth`, here's what happens:

#### Step 1: Request Validation
- ✅ Check file content type (must be image/jpeg, image/jpg, image/png, or image/webp)
- ✅ Verify file is not empty
- ❌ Return 400 error if validation fails

#### Step 2: Image Processing (`extract_cloth`)
- Load image from bytes using Pillow
- **Optional:** Detect face using MediaPipe and crop below face
  - If face detected: Crop image to show only clothing
  - If no face: Continue with original image
- Remove background using rembg (U²-Net model)
- Convert to RGBA format (ensures transparent background)
- Convert to PNG bytes

#### Step 3: Color Extraction (`extract_dominant_rgb`)
- Load processed PNG (with transparent background)
- Filter out transparent pixels (alpha channel = 0)
- Calculate average RGB from visible pixels
- Map RGB to color name and group

#### Step 4: Type Classification (`classify_type`)
- Load CLIP model (cached after first use)
- Preprocess image for CLIP
- Run CLIP inference with labels:
  - "a photo of a shirt"
  - "a photo of a t-shirt"
  - "a photo of a pants"
  - "a photo of a shorts"
  - "a photo of a shoes"
  - "a photo of a accessories"
- Get probability scores for each label
- **Multi-garment validation:**
  - If top 2 scores are close (within 0.20) and both above thresholds
  - Reject image (likely contains multiple items)
- Return top label

#### Step 5: Inventory Generation (`generate_inventory_item`)
- Map CLIP label to category and type:
  - "a photo of a shirt" → `topwear`, `shirt`
  - "a photo of a t-shirt" → `topwear`, `tshirt`
  - "a photo of a pants" → `bottomwear`, `pants`
  - "a photo of a shorts" → `bottomwear`, `shorts`
  - "a photo of a shoes" → `footwear`, `shoes`
  - "a photo of a accessories" → `accessories`, `accessories`
- Generate smart ID:
  - Load existing wardrobe from `inventory/wardrobe.json`
  - Find all IDs matching `{category}_{type}_*`
  - Get highest sequence number
  - Generate next ID: `{category}_{type}_{next_number}`
  - Example: If `topwear_shirt_01` and `topwear_shirt_02` exist, generate `topwear_shirt_03`
- Create inventory object with all metadata

#### Step 6: Response Preparation
- Encode processed PNG bytes to base64 string
- Combine image data and inventory into JSON response
- Return JSONResponse with status 200

### Error Handling

- **Image processing errors:** Logged and return 500 error
- **Multi-garment detection:** Return 400 error with explanation
- **Classification errors:** Logged and return 500 error
- **File validation errors:** Return 400 error immediately

---

## 📝 Temporary Inventory Workflow

### Overview

The temporary inventory system allows users to review, edit, and confirm items before they are permanently added to the wardrobe. This prevents accidental saves and enables corrections.

### Complete User Flow

#### Step 1: Upload Image
```
POST /api/extract-cloth
→ Image processed (background removed, classified, color extracted)
→ Item saved to temporary_inventory.json
→ Returns: { temp_id, image, inventory }
```

**Response includes:**
- `temp_id`: Temporary ID for subsequent operations
- `image`: Base64-encoded processed PNG
- `inventory`: Generated inventory metadata

#### Step 2: Review Item (Optional)
```
GET /api/temporary-inventory/{temp_id}
→ Returns: Complete temporary item with image and inventory
```

**Use case:** Display item in UI for user review before confirmation.

#### Step 3: Edit Item (Optional)
```
PUT /api/temporary-inventory/{temp_id}
Body: {
  "category": "topwear",
  "fit": "slim",
  "formality": "casual",
  "season": ["summer", "spring"]
}
→ Returns: Updated temporary item
```

**Editable fields:**
- `category`: Clothing category
- `type`: Specific type
- `subtype`: Subtype classification
- `color`: Color object (name, rgb, group)
- `fit`: Fit style
- `formality`: Formality level
- `season`: Array of seasons

**Note:** Only provided fields are updated. Omitted fields remain unchanged.

#### Step 4: Confirm Item (Two Options)

#### Option A: Save to SQLite Database (Recommended)
```
POST /api/inventory/save
Body: { "temp_id": "temp_abc123" }
→ Moves image to images/permanent/{item_id}.png
→ Creates record in SQLite database
→ Removes from temporary storage
→ Returns: Confirmed item with image_url
```

**What happens:**
1. Image moved from `images/temp/` to `images/permanent/`
2. Record created in `inventory/inventory.db` (SQLite)
3. Item removed from `temporary_inventory.json`
4. Item is now part of permanent wardrobe

#### Option B: Save to JSON (Legacy)
```
POST /api/temporary-inventory/{temp_id}/confirm
→ Moves item from temporary_inventory.json to wardrobe.json
→ Removes from temporary storage
→ Returns: Confirmed item
```

**Note:** This method is kept for backward compatibility. New code should use Option A.

#### Step 5: Cancel Item (Alternative)
```
DELETE /api/temporary-inventory/{temp_id}
→ Removes item from temporary_inventory.json
→ Item is discarded (not saved to wardrobe)
```

**Use case:** User decides not to add the item to wardrobe.

### Temporary Inventory File Structure

**File:** `inventory/temporary_inventory.json`

**Format:**
```json
{
  "temp_abc123def456": {
    "temp_id": "temp_abc123def456",
    "inventory": {
      "id": "topwear_shirt_01",
      "category": "topwear",
      "type": "shirt",
      "subtype": "unknown",
      "color": {
        "name": "blue",
        "rgb": [45, 78, 120],
        "group": "blue"
      },
      "fit": "unknown",
      "formality": "unknown",
      "season": []
    },
    "image": {
      "data": "iVBORw0KGgoAAAANSUhEUgAA...",
      "format": "png",
      "media_type": "image/png"
    },
    "created_at": "2025-12-25T12:00:00.000000",
    "status": "pending"
  }
}
```

### Benefits of Temporary Inventory

1. **User Control:** Users can review AI-generated data before saving
2. **Error Correction:** Allows editing of incorrect classifications
3. **Data Quality:** Prevents accidental saves of incorrect items
4. **Flexibility:** Users can cancel items they don't want to add
5. **Audit Trail:** `created_at` timestamp tracks when items were processed

### Flutter Integration Example

```dart
// 1. Upload image
var uploadResponse = await uploadImage(imageFile);
String tempId = uploadResponse['temp_id'];

// 2. Display for review (optional)
var reviewItem = await getTemporaryItem(tempId);

// 3. Edit if needed (optional)
await updateTemporaryItem(tempId, {
  'fit': 'slim',
  'formality': 'casual'
});

// 4. Save to permanent database (recommended)
var savedItem = await saveToInventory(tempId);
// Returns: { success: true, item: {...} }

// OR use legacy confirm (saves to JSON)
await confirmTemporaryItem(tempId);

// OR cancel
await deleteTemporaryItem(tempId);

// 5. Manage permanent inventory
var allItems = await getAllInventoryItems();
var singleItem = await getInventoryItem('topwear_shirt_01');
await updateInventoryItem('topwear_shirt_01', { 'fit': 'regular' });
await deleteInventoryItem('topwear_shirt_01');
```

---

## 💾 Permanent Inventory & Database

### SQLite Database

The permanent inventory is stored in SQLite database (`inventory/inventory.db`) for reliable, queryable storage.

### Database Schema

**Table: `inventory_items`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | String (PK) | Inventory item ID (e.g., `topwear_shirt_01`) |
| `image_path` | String | Relative path to image file |
| `image_url` | String | Full image URL (optional) |
| `category` | String | Clothing category |
| `type` | String | Clothing type |
| `subtype` | String | Subtype classification |
| `color_name` | String | Color name |
| `color_rgb` | JSON | RGB array `[r, g, b]` |
| `color_group` | String | Color group |
| `fit` | String | Fit style |
| `formality` | String | Formality level |
| `season` | JSON | Array of seasons |
| `type_confidence` | Float | Type classification confidence (optional) |
| `color_confidence` | Float | Color detection confidence (optional) |
| `created_at` | DateTime | Creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

### Permanent Inventory API Endpoints

#### `POST /api/inventory/save`

**Description:** Save temporary inventory item to permanent database.

**Request:**
```json
{
  "temp_id": "temp_abc123def456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Item saved to inventory",
  "item": {
    "id": "topwear_shirt_01",
    "image_path": "images/permanent/topwear_shirt_01.png",
    "image_url": "images/permanent/topwear_shirt_01.png",
    "category": "topwear",
    "type": "shirt",
    "subtype": "unknown",
    "color": {
      "name": "blue",
      "rgb": [45, 78, 120],
      "group": "blue"
    },
    "fit": "unknown",
    "formality": "unknown",
    "season": [],
    "created_at": "2025-12-25T12:00:00",
    "updated_at": "2025-12-25T12:00:00"
  }
}
```

**What happens:**
1. Retrieves temporary item
2. Moves image from `images/temp/` to `images/permanent/`
3. Creates record in SQLite database
4. Removes from temporary storage

---

#### `GET /api/inventory`

**Description:** List all inventory items with pagination.

**Query Parameters:**
- `skip` (int, default: 0): Number of items to skip
- `limit` (int, default: 100, max: 1000): Maximum items to return

**Response:**
```json
{
  "success": true,
  "count": 10,
  "items": [
    {
      "id": "topwear_shirt_01",
      "image_path": "images/permanent/topwear_shirt_01.png",
      "image_url": "images/permanent/topwear_shirt_01.png",
      "category": "topwear",
      "type": "shirt",
      ...
    },
    ...
  ]
}
```

---

#### `GET /api/inventory/{item_id}`

**Description:** Get single inventory item by ID.

**Response:**
```json
{
  "success": true,
  "item": {
    "id": "topwear_shirt_01",
    "image_path": "images/permanent/topwear_shirt_01.png",
    "image_url": "images/permanent/topwear_shirt_01.png",
    "category": "topwear",
    "type": "shirt",
    ...
  }
}
```

**Error Responses:**
- `404 Not Found`: Item not found

---

#### `PUT /api/inventory/{item_id}`

**Description:** Update inventory item fields.

**Request:**
```json
{
  "fit": "slim",
  "formality": "casual",
  "season": ["summer", "spring"]
}
```

**Response:**
```json
{
  "success": true,
  "item": {
    "id": "topwear_shirt_01",
    "fit": "slim",
    "formality": "casual",
    "season": ["summer", "spring"],
    ...
  }
}
```

**Note:** Only provided fields are updated. Omitted fields remain unchanged.

---

#### `DELETE /api/inventory/{item_id}`

**Description:** Delete inventory item and associated image.

**Response:**
```json
{
  "success": true,
  "message": "Inventory item deleted"
}
```

**What happens:**
1. Deletes image file from `images/permanent/`
2. Removes record from SQLite database

---

### Complete Inventory Lifecycle

#### Step 1: Upload Image
```
POST /api/extract-cloth
→ Image processed
→ Saved to temporary_inventory.json
→ Image saved to images/temp/{temp_id}.png
→ Returns: { temp_id, image, inventory }
```

#### Step 2: Review & Edit (Optional)
```
GET /api/temporary-inventory/{temp_id}
PUT /api/temporary-inventory/{temp_id}
```

#### Step 3: Save to Permanent Database
```
POST /api/inventory/save
Body: { "temp_id": "temp_abc123" }
→ Image moved to images/permanent/{item_id}.png
→ Record created in SQLite database
→ Removed from temporary storage
→ Returns: Confirmed item with image_url
```

#### Step 4: Manage Inventory
```
GET /api/inventory              # List all items
GET /api/inventory/{item_id}    # Get single item
PUT /api/inventory/{item_id}     # Update item
DELETE /api/inventory/{item_id} # Delete item
```

---

## 🚀 How to Run the Application

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd "/Users/saisurya114gmail.com/Documents/Ai Stylist/Backend"

# Install all required packages
pip install -r requirements.txt
```

**Note:** First-time installation will:
- Download PyTorch (~2GB)
- Download CLIP model on first use (~150MB)
- This may take 10-20 minutes depending on internet speed

### Step 2: Start the Server

```bash
# From the project root directory
uvicorn app.main:app --reload
```

**What this does:**
- Starts FastAPI server on `http://localhost:8000`
- `--reload` enables auto-reload on code changes (development mode)

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using StatReload
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 3: Verify Server is Running

Open in browser: `http://localhost:8000/`

Expected response:
```json
{
  "status": "ok",
  "message": "AI Stylist Backend is running"
}
```

### Step 4: Access API Documentation

Open in browser: `http://localhost:8000/docs`

This provides:
- Interactive API documentation (Swagger UI)
- Try it out feature
- Request/response schemas

---

## 🧪 Testing the API

### Method 1: Using the Test Script (Easiest)

```bash
# Make sure server is running first
python test_api.py images/raw/your_image.jpg
```

**What it does:**
- Uploads image to API
- Decodes base64 response
- Saves processed image as `test_output_*.png`
- Displays inventory data in console

### Method 2: Using curl

```bash
curl -X POST "http://localhost:8000/api/extract-cloth" \
  -F "file=@images/raw/test.jpg" \
  --output response.json
```

Then decode the base64 image:
```python
import json
import base64

with open('response.json', 'r') as f:
    data = json.load(f)

image_bytes = base64.b64decode(data['image']['data'])
with open('output.png', 'wb') as f:
    f.write(image_bytes)
```

### Method 3: Using Swagger UI

1. Open `http://localhost:8000/docs`
2. Find `POST /api/extract-cloth`
3. Click "Try it out"
4. Click "Choose File" and select an image
5. Click "Execute"
6. View response JSON
7. Copy base64 string and decode (see Method 2)

### Method 4: Using Python requests

```python
import requests
import base64
import json

url = "http://localhost:8000/api/extract-cloth"
with open("test_image.jpg", "rb") as f:
    files = {"file": ("test.jpg", f, "image/jpeg")}
    response = requests.post(url, files=files)

if response.status_code == 200:
    data = response.json()
    
    # Decode and save image
    image_bytes = base64.b64decode(data['image']['data'])
    with open('output.png', 'wb') as f:
        f.write(image_bytes)
    
    # Print inventory
    print(json.dumps(data['inventory'], indent=2))
```

### Method 5: View Base64 Image in Browser

1. Get the base64 string from `response['image']['data']`
2. Open browser and paste in address bar:
   ```
   data:image/png;base64,<paste_base64_string_here>
   ```
3. Image will display directly

---

## 📝 Key Design Decisions

### Why rembg instead of SCHP?
- **SCHP (Self-Correction for Human Parsing)** requires human detection
- rembg (U²-Net) works on any object, not just humans
- More reliable for clothing items without people
- Faster processing

### Why CLIP for classification?
- Pre-trained model (no training needed)
- Accurate clothing type detection
- Multi-garment validation built-in
- No need for custom dataset

### Why base64 encoding?
- JSON can only contain text, not binary
- Base64 converts binary (image) to text
- Standard approach for embedding images in JSON
- Easy to decode on client side

### Why smart IDs?
- Human-readable format (`topwear_shirt_01`)
- Sequential numbering prevents conflicts
- Easy to query and filter
- Better than random UUIDs for inventory management

### Why layered architecture?
- **API layer** (`app/api/`): Thin, handles HTTP
- **Service layer** (`app/services/`): Business logic
- **Separation of concerns**: Easy to test and maintain
- **Reusability**: Services can be used by multiple endpoints

---

## 🔧 Troubleshooting

### Server won't start
- **Check:** All dependencies installed? Run `pip install -r requirements.txt`
- **Check:** Port 8000 available? Change port: `uvicorn app.main:app --port 8001`

### CLIP import error
- **Solution:** Install CLIP: `pip install git+https://github.com/openai/CLIP.git`
- **Note:** Requires torch to be installed first

### Model download slow
- **First run:** CLIP downloads ViT-B/32 model (~150MB)
- **Location:** `~/.cache/clip/` (cached after first download)
- **Solution:** Wait for download, or download manually

### Multi-garment error
- **Cause:** Image contains multiple clothing items
- **Solution:** Upload image with single clothing item only
- **Validation:** Top 2 classifications are too close in confidence

### Permission errors
- **Cause:** Sandbox restrictions in some environments
- **Solution:** Run server outside sandbox, or check file permissions

---

## 📚 Additional Resources

- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **CLIP Paper:** https://arxiv.org/abs/2103.00020
- **rembg GitHub:** https://github.com/danielgatis/rembg
- **Swagger UI:** Available at `http://localhost:8000/docs` when server is running

---

## 🎯 Next Steps (Future Enhancements)

1. **Database Integration:** Replace JSON files with PostgreSQL/MongoDB
2. **Image Storage:** Use cloud storage (S3, Cloudinary) instead of local files
3. **User Authentication:** Add user accounts and session management
4. **Batch Processing:** Endpoint for multiple images at once
5. **Outfit Recommendations:** AI-powered outfit suggestions based on inventory
6. **Additional Metadata:** Fit, formality, season detection
7. **Image Enhancement:** Better background removal, image quality improvement

---

## 📞 Support

For issues or questions:
1. Check this documentation first
2. Review error logs in server output
3. Check `API_TESTING_GUIDE.md` for testing help
4. Verify all dependencies are installed correctly

---

**Last Updated:** December 2025  
**Version:** 1.0.0  
**Status:** MVP Complete ✅

