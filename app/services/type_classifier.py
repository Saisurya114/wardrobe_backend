import torch
import clip
from PIL import Image
import io
import logging

logger = logging.getLogger(__name__)

# Cache the model to avoid reloading
_model_cache = None
_preprocess_cache = None
_device_cache = None

LABELS = [
    "a photo of a shirt",
    "a photo of a t-shirt",
    "a photo of a pants",
    "a photo of a shorts",
    "a photo of a shoes",
    "a photo of a accessories"
]

# Validation thresholds
PRIMARY_CONFIDENCE_THRESHOLD = 0.50
SECONDARY_CONFIDENCE_THRESHOLD = 0.30
MAX_CONFIDENCE_DIFF = 0.20


def _load_model():
    """Load CLIP model (cached for performance)."""
    global _model_cache, _preprocess_cache, _device_cache
    
    if _model_cache is None:
        _device_cache = "cuda" if torch.cuda.is_available() else "cpu"
        _model_cache, _preprocess_cache = clip.load("ViT-B/32", device=_device_cache)
        logger.info(f"CLIP model loaded on {_device_cache}")
    
    return _model_cache, _preprocess_cache, _device_cache


def classify_type(image_bytes: bytes) -> str:
    """
    Classify clothing type using CLIP.
    
    Args:
        image_bytes: Image bytes (PNG with transparent background)
    
    Returns:
        Label string (e.g., "a photo of a shirt")
    
    Raises:
        ValueError: If multi-garment image is detected
    """
    try:
        model, preprocess, device = _load_model()
        
        # Load and preprocess image
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = preprocess(image).unsqueeze(0).to(device)
        
        # Tokenize labels
        text = clip.tokenize(LABELS).to(device)
        
        # Run CLIP
        with torch.no_grad():
            logits, _ = model(image_tensor, text)
            probs = logits.softmax(dim=-1).cpu().numpy()[0]
        
        # Get top results
        scored = list(zip(LABELS, probs))
        scored.sort(key=lambda x: x[1], reverse=True)
        
        top_label, top_score = scored[0]
        second_label, second_score = scored[1]
        
        # Multi-garment validation
        if (
            top_score >= PRIMARY_CONFIDENCE_THRESHOLD
            and second_score >= SECONDARY_CONFIDENCE_THRESHOLD
            and abs(top_score - second_score) <= MAX_CONFIDENCE_DIFF
        ):
            raise ValueError(
                f"Multi-garment image detected. "
                f"Top: {top_label} ({top_score:.2f}), "
                f"Second: {second_label} ({second_score:.2f})"
            )
        
        return top_label
    
    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Error in classify_type: {str(e)}", exc_info=True)
        raise ValueError(f"Failed to classify image type: {str(e)}")


def map_inventory_type(label: str) -> tuple:
    """
    Map CLIP label to inventory category and type.
    
    Returns:
        Tuple of (category, type)
    """
    if "shirt" in label and "t-shirt" not in label:
        return "topwear", "shirt"
    if "t-shirt" in label:
        return "topwear", "tshirt"
    if "pants" in label:
        return "bottomwear", "pants"
    if "shorts" in label:
        return "bottomwear", "shorts"
    if "shoes" in label:
        return "footwear", "shoes"
    if "accessories" in label:
        return "accessories", "accessories"
    
    return "unknown", "unknown"

