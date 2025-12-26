from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.services.cloth_extractor import extract_cloth
from app.services.inventory_generator import generate_inventory_item
from app.services.temporary_inventory import (
    save_to_temporary_inventory,
    get_temporary_item,
    update_temporary_item,
    confirm_and_move_to_wardrobe,
    delete_temporary_item
)
from pydantic import BaseModel
from typing import Optional, List
import logging
import base64
from concurrent.futures import ThreadPoolExecutor
import asyncio

logger = logging.getLogger(__name__)
router = APIRouter()

# Thread pool for CPU-intensive tasks
executor = ThreadPoolExecutor(max_workers=2)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit


# Request models
class InventoryUpdate(BaseModel):
    """Model for updating inventory item fields."""
    category: Optional[str] = None
    type: Optional[str] = None
    subtype: Optional[str] = None
    color: Optional[dict] = None
    fit: Optional[str] = None
    formality: Optional[str] = None
    season: Optional[List[str]] = None


@router.post("/extract-cloth")
async def extract_cloth_api(file: UploadFile = File(...)):
    """
    Extract cloth from uploaded image and return PNG with transparent background
    along with inventory metadata (type, color, etc.).
    
    Accepts: jpg, jpeg, png, webp
    Returns: JSON with processed image (base64) and inventory data
    """
    # Validate content type
    if not file.content_type or file.content_type.lower() not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Validate file size
        if len(image_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        
        # Step 1: Process image (extract cloth with transparent background) - run in thread pool
        processed_image_bytes = await asyncio.get_event_loop().run_in_executor(
            executor, extract_cloth, image_bytes
        )
        
        if not processed_image_bytes:
            raise HTTPException(
                status_code=500,
                detail="Failed to process image. Please try again."
            )
        
        # Step 2: Generate inventory metadata - run in thread pool
        try:
            inventory_item = await asyncio.get_event_loop().run_in_executor(
                executor, generate_inventory_item, processed_image_bytes
            )
        except ValueError as e:
            # Multi-garment or classification error
            raise HTTPException(
                status_code=400,
                detail=str(e)
            )
        
        # Step 3: Encode image as base64 for JSON response
        image_base64 = base64.b64encode(processed_image_bytes).decode('utf-8')
        
        # Step 4: Save to temporary inventory
        temp_id = save_to_temporary_inventory(inventory_item, image_base64)
        
        # Step 5: Return combined response with temp_id
        return JSONResponse(
            content={
                "success": True,
                "temp_id": temp_id,
                "image": {
                    "data": image_base64,
                    "format": "png",
                    "media_type": "image/png"
                },
                "inventory": inventory_item
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error while processing image"
        )


@router.get("/temporary-inventory/{temp_id}")
async def get_temporary_inventory(temp_id: str):
    """
    Get temporary inventory item for review.
    
    Returns the full temporary item including image and inventory data.
    """
    item = get_temporary_item(temp_id)
    
    if not item:
        raise HTTPException(status_code=404, detail="Temporary item not found")
    
    return JSONResponse(content=item)


@router.put("/temporary-inventory/{temp_id}")
async def update_temporary_inventory(temp_id: str, update: InventoryUpdate):
    """
    Update temporary inventory item (user edits).
    
    Allows user to edit any inventory fields before confirming.
    Only provided fields will be updated.
    """
    # Convert Pydantic model to dict, excluding None values
    update_dict = update.dict(exclude_none=True)
    
    if not update_dict:
        raise HTTPException(status_code=400, detail="No fields provided for update")
    
    success = update_temporary_item(temp_id, update_dict)
    
    if not success:
        raise HTTPException(status_code=404, detail="Temporary item not found")
    
    # Return updated item
    item = get_temporary_item(temp_id)
    return JSONResponse(content=item)


@router.post("/temporary-inventory/{temp_id}/confirm")
async def confirm_temporary_inventory(temp_id: str):
    """
    Confirm and move temporary item to wardrobe.json.
    
    This moves the item from temporary_inventory.json to wardrobe.json
    and removes it from temporary storage.
    """
    confirmed_item = confirm_and_move_to_wardrobe(temp_id)
    
    if not confirmed_item:
        raise HTTPException(status_code=404, detail="Temporary item not found")
    
    return JSONResponse(content={
        "success": True,
        "message": "Item added to wardrobe",
        "item": confirmed_item
    })


@router.delete("/temporary-inventory/{temp_id}")
async def delete_temporary_inventory(temp_id: str):
    """
    Delete temporary inventory item (user cancelled).
    
    Removes the item from temporary_inventory.json without saving to wardrobe.
    """
    success = delete_temporary_item(temp_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Temporary item not found")
    
    return JSONResponse(content={
        "success": True,
        "message": "Temporary item deleted"
    })
