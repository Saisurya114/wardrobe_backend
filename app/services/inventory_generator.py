import os
import json
from .color_extractor import extract_dominant_rgb, map_color_group, map_color_name
from .type_classifier import classify_type, map_inventory_type
import logging

logger = logging.getLogger(__name__)

# Use absolute path based on project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WARDROBE_FILE = os.path.join(BASE_DIR, "inventory", "wardrobe.json")


def _load_wardrobe() -> list:
    """Load existing wardrobe items."""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(WARDROBE_FILE), exist_ok=True)
    
    if os.path.exists(WARDROBE_FILE):
        try:
            with open(WARDROBE_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load wardrobe: {str(e)}")
    return []


def generate_smart_id(category: str, item_type: str, existing_items: list = None) -> str:
    """
    Generate ID in format: {category}_{type}_{number}
    Examples: topwear_shirt_01, bottomwear_pants_02, footwear_shoes_01
    
    Args:
        category: Category (topwear, bottomwear, footwear, accessories)
        item_type: Type (shirt, tshirt, pants, shorts, shoes, etc.)
        existing_items: List of existing items (if None, loads from wardrobe.json)
    
    Returns:
        ID string like "topwear_shirt_01"
    """
    if existing_items is None:
        existing_items = _load_wardrobe()
    
    # Create prefix: category_type
    prefix = f"{category}_{item_type}"
    
    # Find all existing IDs with this prefix
    existing_ids = [
        item.get("id", "") for item in existing_items
        if item.get("id", "").startswith(prefix + "_")
    ]
    
    # Extract sequence numbers and find the next one
    max_seq = 0
    for item_id in existing_ids:
        try:
            # Extract number from ID like "topwear_shirt_01"
            parts = item_id.split("_")
            if len(parts) >= 3:
                seq_num = int(parts[-1])
                max_seq = max(max_seq, seq_num)
        except (ValueError, IndexError):
            continue
    
    # Generate next sequence number (zero-padded to 2 digits)
    next_seq = max_seq + 1
    return f"{prefix}_{str(next_seq).zfill(2)}"


def generate_inventory_item(processed_image_bytes: bytes) -> dict:
    """
    Generate inventory item from processed image bytes.
    
    Args:
        processed_image_bytes: PNG bytes with transparent background (from extract_cloth)
    
    Returns:
        Dictionary with inventory item data
    
    Raises:
        ValueError: If classification fails (e.g., multi-garment detected)
    """
    try:
        # Extract color information
        rgb = extract_dominant_rgb(processed_image_bytes)
        color_group = map_color_group(rgb)
        color_name = map_color_name(rgb)
        
        # Classify type
        label = classify_type(processed_image_bytes)
        category, item_type = map_inventory_type(label)
        
        # Generate smart ID
        smart_id = generate_smart_id(category, item_type)
        
        # Generate inventory item
        item = {
            "id": smart_id,
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
            "image": None  # Will be set by API if saving to disk
        }
        
        return item
    
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error generating inventory item: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to generate inventory: {str(e)}")

