"""
Image Upload Service for Petrol Pump Ledger Automation

This module provides image upload functionality
"""
import os
import uuid
from typing import Optional
from fastapi import UploadFile


class ImageUploadService:
    """
    Service class for handling image uploads
    """

    def __init__(self, upload_folder: str = "uploads/", max_file_size: int = 16 * 1024 * 1024):
        """
        Initialize the image upload service

        Args:
            upload_folder: Folder to store uploaded images
            max_file_size: Maximum file size allowed in bytes (default 16MB)
        """
        self.upload_folder = upload_folder
        self.max_file_size = max_file_size

        # Create upload folder if it doesn't exist
        os.makedirs(upload_folder, exist_ok=True)

    async def upload_image(self, file: UploadFile) -> Optional[str]:
        """
        Upload an image file

        Args:
            file: Uploaded file object

        Returns:
            Path to the saved file or None if upload failed
        """
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(self.upload_folder, unique_filename)

        # Save the file
        with open(file_path, 'wb') as buffer:
            import shutil
            shutil.copyfileobj(file.file, buffer)

        return file_path

    def cleanup_temp_file(self, file_path: str) -> bool:
        """
        Remove a temporary file

        Args:
            file_path: Path to the file to remove

        Returns:
            True if file was removed, False otherwise
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
