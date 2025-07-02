import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import io

# Configuration
UPLOAD_DIR = Path("uploads/profile_pictures")
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_IMAGE_DIMENSIONS = (800, 800)  # Max width and height

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def is_valid_image_file(filename: str) -> bool:
    """Check if the file has a valid image extension."""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


async def save_profile_picture(file: UploadFile, user_id: int) -> str:
    """
    Save a profile picture file and return the filename.
    
    Args:
        file: The uploaded file
        user_id: The user ID to associate with the file
        
    Returns:
        The filename of the saved image
        
    Raises:
        HTTPException: If the file is invalid or too large
    """
    # Validate file type
    if not file.filename or not is_valid_image_file(file.filename):
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB"
        )
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix.lower()
    filename = f"profile_{user_id}_{uuid.uuid4().hex}{file_extension}"
    file_path = UPLOAD_DIR / filename
    
    try:
        # Read file content
        content = await file.read()
        
        # Process image with PIL
        image = Image.open(io.BytesIO(content))
        
        # Convert to RGB if necessary (for JPEG compatibility)
        if image.mode in ('RGBA', 'LA', 'P'):
            image = image.convert('RGB')
        
        # Resize if too large
        if image.width > MAX_IMAGE_DIMENSIONS[0] or image.height > MAX_IMAGE_DIMENSIONS[1]:
            image.thumbnail(MAX_IMAGE_DIMENSIONS, Image.Resampling.LANCZOS)
        
        # Save processed image
        image.save(file_path, quality=85, optimize=True)
        
        return filename
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


def delete_profile_picture(filename: str) -> bool:
    """
    Delete a profile picture file.
    
    Args:
        filename: The filename to delete
        
    Returns:
        True if file was deleted, False if file didn't exist
    """
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        file_path.unlink()
        return True
    return False


def get_profile_picture_path(filename: str) -> Path:
    """
    Get the full path to a profile picture file.
    
    Args:
        filename: The filename
        
    Returns:
        Path object pointing to the file
    """
    return UPLOAD_DIR / filename 