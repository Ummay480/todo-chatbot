import cv2
import numpy as np
import os
from PIL import Image, ImageEnhance
import io
from typing import Tuple, Optional


class ImageProcessingUtil:
    """
    Utility class for preprocessing images before OCR
    """

    @staticmethod
    def rotate_image_if_needed(image_path: str) -> np.ndarray:
        """
        Rotate image if it's not in the correct orientation
        """
        # Load image
        image = cv2.imread(image_path)

        # Try to detect orientation and correct it
        # For now, we'll implement a basic method - in practice, you'd use a more sophisticated approach
        # This is a simplified version that tries to detect if the image is rotated

        height, width = image.shape[:2]

        # If height > width, the image might be rotated
        if height > width:
            # Rotate 90 degrees clockwise
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        return image

    @staticmethod
    def deskew_image(image: np.ndarray) -> np.ndarray:
        """
        Deskew an image that might be tilted
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply threshold to get binary image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Find all white pixels
        coords = np.column_stack(np.where(binary == 0))

        # Find the angle of rotation
        angle = cv2.minAreaRect(coords)[-1]

        # Adjust angle based on OpenCV convention
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Rotate the image
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

        return rotated

    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast of the image
        """
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

        # Split LAB channels
        l, a, b = cv2.split(lab)

        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        cl = clahe.apply(l)

        # Merge enhanced L channel with original A and B channels
        limg = cv2.merge((cl,a,b))

        # Convert back to BGR
        enhanced = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

        return enhanced

    @staticmethod
    def remove_noise(image: np.ndarray) -> np.ndarray:
        """
        Remove noise from the image
        """
        # Apply bilateral filter to remove noise while keeping edges sharp
        denoised = cv2.bilateralFilter(image, 9, 75, 75)

        return denoised

    @staticmethod
    def sharpen_image(image: np.ndarray) -> np.ndarray:
        """
        Sharpen the image to make text clearer
        """
        # Create sharpening kernel
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])

        # Apply the kernel
        sharpened = cv2.filter2D(image, -1, kernel)

        # Blend original and sharpened
        sharpened = cv2.addWeighted(image, 0.7, sharpened, 0.3, 0)

        return sharpened

    @staticmethod
    def preprocess_image_for_ocr(image_path: str, output_path: Optional[str] = None) -> str:
        """
        Complete preprocessing pipeline for OCR
        """
        # Step 1: Rotate if needed
        image = ImageProcessingUtil.rotate_image_if_needed(image_path)

        # Step 2: Deskew image
        image = ImageProcessingUtil.deskew_image(image)

        # Step 3: Remove noise
        image = ImageProcessingUtil.remove_noise(image)

        # Step 4: Enhance contrast
        image = ImageProcessingUtil.enhance_contrast(image)

        # Step 5: Sharpen image
        image = ImageProcessingUtil.sharpen_image(image)

        # Save the processed image
        if output_path:
            cv2.imwrite(output_path, image)
            return output_path
        else:
            # If no output path provided, save with '_processed' suffix
            base_path, ext = os.path.splitext(image_path)
            output_path = f"{base_path}_processed{ext}"
            cv2.imwrite(output_path, image)
            return output_path

    @staticmethod
    def resize_image(image: np.ndarray, max_width: int = 1920, max_height: int = 1080) -> np.ndarray:
        """
        Resize image to fit within specified dimensions while maintaining aspect ratio
        """
        height, width = image.shape[:2]

        # Calculate scaling factor
        scale_w = max_width / width
        scale_h = max_height / height
        scale = min(scale_w, scale_h)

        if scale < 1:  # Only resize if image is larger than limits
            new_width = int(width * scale)
            new_height = int(height * scale)

            # Resize image
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)

            return resized
        else:
            return image

    @staticmethod
    def convert_to_binary(image: np.ndarray) -> np.ndarray:
        """
        Convert image to binary (black and white) for better OCR
        """
        # Convert to grayscale first
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply adaptive threshold
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)

        return binary

    @staticmethod
    def rotate_image_if_needed_from_array(image: np.ndarray) -> np.ndarray:
        """
        Rotate image if it's not in the correct orientation (works with numpy array)
        """
        height, width = image.shape[:2]

        # If height > width, the image might be rotated
        if height > width:
            # Rotate 90 degrees clockwise
            image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

        return image