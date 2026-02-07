"""
Image Processing Utilities for Petrol Pump Ledger Automation

This module provides image preprocessing utilities for OCR processing
"""
import cv2
import numpy as np
from PIL import Image
import os
from typing import Optional


class ImageProcessingUtil:
    """
    Utility class for image preprocessing before OCR
    """

    @staticmethod
    def preprocess_image_for_ocr(image_path: str) -> str:
        """
        Preprocess an image to improve OCR accuracy

        Args:
            image_path: Path to the input image

        Returns:
            Path to the processed image
        """
        # Load image using OpenCV
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Could not load image from {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply adaptive thresholding to enhance text
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)

        # Find contours to potentially crop the relevant area
        # This is a basic approach - more sophisticated methods can be used
        processed_img = denoised

        # Create output path
        dir_path, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_processed{ext}")

        # Save the processed image
        cv2.imwrite(output_path, processed_img)

        return output_path

    @staticmethod
    def rotate_image_if_needed(image_path: str) -> str:
        """
        Rotate image if needed based on orientation detection

        Args:
            image_path: Path to the input image

        Returns:
            Path to the potentially rotated image
        """
        # Placeholder implementation - in a real implementation,
        # you would detect the image orientation and rotate accordingly
        return image_path

    @staticmethod
    def resize_image(image_path: str, max_width: int = 1920, max_height: int = 1080) -> str:
        """
        Resize image to a maximum dimension while maintaining aspect ratio

        Args:
            image_path: Path to the input image
            max_width: Maximum width
            max_height: Maximum height

        Returns:
            Path to the resized image
        """
        with Image.open(image_path) as img:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

            dir_path, file_name = os.path.split(image_path)
            name, ext = os.path.splitext(file_name)
            output_path = os.path.join(dir_path, f"{name}_resized{ext}")

            img.save(output_path, optimize=True, quality=95)

        return output_path

    @staticmethod
    def correct_skew(image_path: str) -> str:
        """
        Correct image skew to improve OCR accuracy

        Args:
            image_path: Path to the input image

        Returns:
            Path to the corrected image
        """
        # Load image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find coordinates of all non-zero pixels (text)
        coords = np.column_stack(np.where(binary > 0))

        # Find angle of rotation
        angle = cv2.minAreaRect(coords)[-1]

        # Adjust angle based on OpenCV convention
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Rotate the image
        (h, w) = img.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)

        # Save the corrected image
        dir_path, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_corrected{ext}")

        cv2.imwrite(output_path, rotated)

        return output_path