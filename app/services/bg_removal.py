from rembg import remove
from PIL import Image

def remove_background(image: Image.Image) -> Image.Image:
    """
    Removes background and returns RGBA image
    """
    output = remove(image)

    if output.mode != "RGBA":
        output = output.convert("RGBA")

    return output

