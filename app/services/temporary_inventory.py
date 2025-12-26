import os
import json
import uuid
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMP_INVENTORY_FILE = os.path.join(BASE_DIR, "inventory", "temporary_inventory.json")
WARDROBE_FILE = os.path.join(BASE_DIR, "inventory", "wardrobe.json")


def _load_temporary_inventory() -> Dict[str, dict]:
    """Load temporary inventory as dict with temp_id as key."""
    os.makedirs(os.path.dirname(TEMP_INVENTORY_FILE), exist_ok=True)
    
    if os.path.exists(TEMP_INVENTORY_FILE):
        try:
            with open(TEMP_INVENTORY_FILE, "r") as f:
                data = json.load(f)
                # Convert list to dict if needed, or keep as dict
                if isinstance(data, list):
                    return {item.get("temp_id"): item for item in data if item.get("temp_id")}
                return data
        except Exception as e:
            logger.warning(f"Could not load temporary inventory: {str(e)}")
    return {}


def _save_temporary_inventory(data: Dict[str, dict]):
    """Save temporary inventory."""
    os.makedirs(os.path.dirname(TEMP_INVENTORY_FILE), exist_ok=True)
    with open(TEMP_INVENTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def save_to_temporary_inventory(inventory_item: dict, image_base64: str) -> str:
    """
    Save inventory item to temporary inventory.
    
    Args:
        inventory_item: Inventory item dictionary
        image_base64: Base64-encoded PNG image string
    
    Returns:
        Temporary ID string
    """
    temp_id = f"temp_{uuid.uuid4().hex[:12]}"
    
    # Save image to disk
    from .image_service import save_temp_image
    import base64
    
    try:
        image_bytes = base64.b64decode(image_base64)
        image_path = save_temp_image(image_bytes, temp_id)
    except Exception as e:
        logger.warning(f"Failed to save temp image to disk: {str(e)}")
        image_path = None
    
    temp_item = {
        "temp_id": temp_id,
        "inventory": inventory_item,
        "image": {
            "data": image_base64,
            "format": "png",
            "media_type": "image/png",
            "path": image_path  # Add path for reference
        },
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending"
    }
    
    temp_inventory = _load_temporary_inventory()
    temp_inventory[temp_id] = temp_item
    _save_temporary_inventory(temp_inventory)
    
    logger.info(f"Saved temporary inventory item: {temp_id}")
    return temp_id


def get_temporary_item(temp_id: str) -> Optional[dict]:
    """
    Get temporary inventory item by ID.
    
    Args:
        temp_id: Temporary ID
    
    Returns:
        Temporary item dictionary or None if not found
    """
    temp_inventory = _load_temporary_inventory()
    return temp_inventory.get(temp_id)


def update_temporary_item(temp_id: str, updated_data: dict) -> bool:
    """
    Update temporary inventory item.
    
    Args:
        temp_id: Temporary ID
        updated_data: Dictionary with fields to update in inventory object
    
    Returns:
        True if updated, False if not found
    """
    temp_inventory = _load_temporary_inventory()
    
    if temp_id not in temp_inventory:
        return False
    
    # Update inventory fields
    if "inventory" in updated_data:
        temp_inventory[temp_id]["inventory"].update(updated_data["inventory"])
    else:
        temp_inventory[temp_id]["inventory"].update(updated_data)
    
    _save_temporary_inventory(temp_inventory)
    logger.info(f"Updated temporary inventory item: {temp_id}")
    return True


def confirm_and_move_to_wardrobe(temp_id: str) -> Optional[dict]:
    """
    Move temporary item to wardrobe.json and remove from temporary.
    
    NOTE: This is kept for backward compatibility. 
    New code should use POST /api/inventory/save which saves to SQLite.
    
    Args:
        temp_id: Temporary ID
    
    Returns:
        Confirmed inventory item or None if not found
    """
    temp_inventory = _load_temporary_inventory()
    
    if temp_id not in temp_inventory:
        return None
    
    item = temp_inventory[temp_id]
    inventory_item = item["inventory"]
    
    # Load wardrobe
    from .inventory_generator import _load_wardrobe
    wardrobe = _load_wardrobe()
    
    # Add to wardrobe
    wardrobe.append(inventory_item)
    
    # Save wardrobe
    os.makedirs(os.path.dirname(WARDROBE_FILE), exist_ok=True)
    with open(WARDROBE_FILE, "w") as f:
        json.dump(wardrobe, f, indent=2)
    
    # Remove from temporary
    del temp_inventory[temp_id]
    _save_temporary_inventory(temp_inventory)
    
    logger.info(f"Confirmed and moved to wardrobe.json: {temp_id} -> {inventory_item.get('id')}")
    logger.warning("Using legacy wardrobe.json. Consider using POST /api/inventory/save for SQLite storage.")
    return inventory_item


def delete_temporary_item(temp_id: str) -> bool:
    """
    Delete temporary inventory item (user cancelled).
    
    Args:
        temp_id: Temporary ID
    
    Returns:
        True if deleted, False if not found
    """
    temp_inventory = _load_temporary_inventory()
    
    if temp_id not in temp_inventory:
        return False
    
    del temp_inventory[temp_id]
    _save_temporary_inventory(temp_inventory)
    
    logger.info(f"Deleted temporary inventory item: {temp_id}")
    return True

