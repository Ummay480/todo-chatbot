from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import os
from PIL import Image


class ImageValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate image uploads
    """

    def __init__(
        self,
        app,
        max_file_size: int = 16 * 1024 * 1024,  # 16MB
        allowed_extensions: set = None,
        allowed_mime_types: set = None
    ):
        super().__init__(app)
        self.max_file_size = max_file_size
        self.allowed_extensions = allowed_extensions or {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}
        self.allowed_mime_types = allowed_mime_types or {
            'image/png', 'image/jpeg', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp'
        }

    async def dispatch(self, request: Request, call_next):
        # Check if this is an image upload endpoint
        if request.url.path.startswith('/api/v1/ledger/upload') and request.method == 'POST':
            # For now, we'll just validate the content-type header
            content_type = request.headers.get('content-type', '')

            # Basic validation of content type
            if not any(mime_type in content_type for mime_type in self.allowed_mime_types):
                if not content_type.startswith('multipart/form-data'):
                    raise HTTPException(status_code=400, detail="Invalid content type for image upload")

        response = await call_next(request)
        return response


def validate_uploaded_image(file_path: str, max_size: int = 16 * 1024 * 1024) -> tuple[bool, str]:
    """
    Validate an uploaded image file
    :param file_path: Path to the uploaded file
    :param max_size: Maximum allowed file size in bytes
    :return: Tuple of (is_valid, error_message)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, "File does not exist"

    # Check file size
    file_size = os.path.getsize(file_path)
    if file_size > max_size:
        return False, f"File size {file_size} exceeds maximum allowed size {max_size}"

    # Check if it's a valid image
    try:
        with Image.open(file_path) as img:
            img.verify()  # Verify it's a valid image
    except Exception as e:
        return False, f"File is not a valid image: {str(e)}"

    # Get the actual file extension
    _, ext = os.path.splitext(file_path)
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'}

    if ext.lower() not in allowed_extensions:
        return False, f"File extension {ext} is not allowed"

    return True, "Valid image file"


def validate_image_content_type(content_type: str) -> tuple[bool, str]:
    """
    Validate image content type
    :param content_type: Content type string
    :return: Tuple of (is_valid, error_message)
    """
    allowed_types = {
        'image/png', 'image/jpeg', 'image/jpg', 'image/gif',
        'image/bmp', 'image/tiff', 'image/webp'
    }

    # Extract the main content type (before any parameters)
    main_type = content_type.split(';')[0].strip().lower()

    if main_type in allowed_types:
        return True, "Valid image content type"
    else:
        return False, f"Content type {main_type} is not allowed. Allowed types: {', '.join(allowed_types)}"