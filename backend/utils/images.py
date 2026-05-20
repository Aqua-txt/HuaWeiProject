import os
import uuid
from flask import current_app
from werkzeug.utils import secure_filename
from PIL import Image


def save_image(file) -> str:
    """Save an uploaded image, return the filename."""
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'jpg'
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    img = Image.open(file)
    img.thumbnail((1200, 1200))
    img.save(filepath, quality=85, optimize=True)

    return filename


def allowed_image(filename: str) -> bool:
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    return ext in current_app.config['ALLOWED_EXTENSIONS']
