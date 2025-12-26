from rembg import remove
from PIL import Image
from .face_crop import crop_below_face
import io
import logging

logger = logging.getLogger(__name__)


def extract_cloth(image_bytes: bytes) -> bytes:
    """
    Extract cloth from image bytes using rembg for background removal.
    
    Processing steps:
    1. Load and convert image to RGB
    2. Optionally crop below face (if face detected)
    3. Remove background using rembg (U²-Net)
    4. Ensure RGBA format (transparent background)
    5. Return PNG bytes
    
    Args:
        image_bytes: Raw image bytes (jpg, png, webp, etc.)
    
    Returns:
        PNG bytes with RGBA format (transparent background)
    
    Raises:
        ValueError: If image cannot be processed
        IOError: If image bytes are invalid
    """
    try:
        # Load image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        # 1️⃣ Optional: Remove face (crop below face)
        # Gracefully handle face detection failures
        try:
            image = crop_below_face(image)
        except Exception as e:
            logger.warning(f"Face cropping failed, continuing without it: {str(e)}")
            # Continue with original image if face detection fails
        
        # 2️⃣ Remove background using rembg (U²-Net)
        output = remove(image)
        
        # 3️⃣ Ensure RGBA format (transparent background)
        if output.mode != "RGBA":
            output = output.convert("RGBA")
        
        # 4️⃣ Convert to PNG bytes
        buffer = io.BytesIO()
        output.save(buffer, format="PNG")
        buffer.seek(0)
        
        return buffer.read()
    
    except Exception as e:
        logger.error(f"Error in extract_cloth: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to process image: {str(e)}")

