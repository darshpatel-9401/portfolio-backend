import io

from PIL import Image

from app.config import Config
from app.utils.errors import ApiError

ALLOWED = {"JPEG": ".jpg", "PNG": ".png", "WEBP": ".webp", "GIF": ".gif"}


def check_image(data):
    """Checks size and that the bytes are really an image (not just a file name ending in .jpg).
    Returns (extension, mime type). SVG is not allowed because it can contain scripts."""
    if len(data) > Config.MAX_UPLOAD_MB * 1024 * 1024:
        raise ApiError(f"File is larger than {Config.MAX_UPLOAD_MB} MB", 413)
    if len(data) > 12 and data[4:8] == b"ftyp" and data[8:12] in (b"avif", b"avis"):
        return ".avif", "image/avif"  # Pillow 10 cannot open AVIF, so we check the file signature
    try:
        img = Image.open(io.BytesIO(data))
        img.verify()
        fmt = img.format
    except Exception:
        raise ApiError("File is not a valid image", 400)
    if fmt not in ALLOWED:
        raise ApiError("Only JPG, PNG, WEBP, GIF and AVIF images are allowed", 400)
    return ALLOWED[fmt], f"image/{fmt.lower()}"
