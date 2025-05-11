import os
from werkzeug.utils import secure_filename
from PIL import Image, ImageOps
from secrets import token_hex
from flask import current_app

_IMAGE_EXTS = [".jpg", ".jpeg", ".png", ".gif"]

def preprocess_image(uploaded_img, size=(200, 200)):
    """
    Processes an optional uploaded image before storage.

    Params:
        uploaded_img (FileStorage): The uploaded image file.
        size (tuple): The desired size (width, height) for the resized image.

    Returns:
        str | None: The relative file path of the processed and saved image, 
        or None if no image was uploaded.
    """
    if not uploaded_img:
        return None

    sanitized_name = secure_filename(uploaded_img.filename)
    _, ext = os.path.splitext(sanitized_name)
    
    if ext.lower() not in _IMAGE_EXTS:
        raise ValueError("Unsupported file format. Allowed formats: JPG, JPEG, PNG, GIF.")
    
    filename = f"{token_hex(16)}{ext.lower()}"

    output_folder = os.path.join(
        current_app.root_path,
        "static",
        "images",
        "profile-pictures"
    )
    os.makedirs(output_folder, exist_ok=True)

    output_path = os.path.join(output_folder, filename)

    img = Image.open(uploaded_img)
    img.thumbnail(size, Image.Resampling.LANCZOS) 
    img.save(output_path, quality=95, optimize=True)

    return filename
