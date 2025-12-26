from PIL import Image
import numpy as np
import io
import logging

logger = logging.getLogger(__name__)


def extract_dominant_rgb(image_bytes: bytes) -> tuple:
    """
    Extract dominant RGB color from image bytes (ignoring transparent pixels).
    
    Args:
        image_bytes: PNG bytes with RGBA format
    
    Returns:
        Tuple of (r, g, b) integers
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        data = np.array(img)
        
        # Remove transparent pixels
        rgb_pixels = data[data[:, :, 3] > 0][:, :3]
        
        if len(rgb_pixels) == 0:
            # Fallback if all pixels are transparent
            return (128, 128, 128)
        
        # Compute average RGB
        avg_color = np.mean(rgb_pixels, axis=0)
        return tuple(int(x) for x in avg_color)
    
    except Exception as e:
        logger.error(f"Error extracting RGB: {str(e)}", exc_info=True)
        return (128, 128, 128)  # Default gray


def map_color_group(rgb: tuple) -> str:
    """Map RGB to color group (white, black, red, green, blue, neutral)."""
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


def map_color_name(rgb: tuple) -> str:
    """Map RGB to color name."""
    r, g, b = rgb
    
    if abs(r - g) < 20 and abs(g - b) < 20:
        if r > 200:
            return "off white"
        if r < 80:
            return "black"
        return "beige"
    
    if b > r + 25:
        return "blue"
    if r > g + 25:
        return "red"
    if g > r + 25:
        return "green"
    
    return "neutral"

