import cv2
import numpy as np
from PIL import Image
import os
from typing import Optional, Tuple
from ..utils.image_processing import ImageProcessingUtil


class ImagePreprocessingPipeline:
    """
    Complete pipeline for preprocessing images before OCR
    """

    def __init__(self,
                 target_width: int = 1920,
                 target_height: int = 1080,
                 enhance_contrast: bool = True,
                 remove_noise: bool = True,
                 sharpen: bool = True):
        self.target_width = target_width
        self.target_height = target_height
        self.enhance_contrast = enhance_contrast
        self.remove_noise = remove_noise
        self.sharpen = sharpen

    def preprocess_image(self, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Complete preprocessing pipeline
        :param image_path: Path to the input image
        :param output_path: Path where the processed image will be saved
        :return: Path to the processed image
        """
        # Step 1: Load image
        image = cv2.imread(image_path)

        # Step 2: Rotate if needed
        image = ImageProcessingUtil.rotate_image_if_needed(image_path)

        # Step 3: Resize image
        image = self.resize_image(image)

        # Step 4: Deskew image
        image = ImageProcessingUtil.deskew_image(image)

        # Step 5: Remove noise
        if self.remove_noise:
            image = ImageProcessingUtil.remove_noise(image)

        # Step 6: Enhance contrast
        if self.enhance_contrast:
            image = ImageProcessingUtil.enhance_contrast(image)

        # Step 7: Sharpen image
        if self.sharpen:
            image = ImageProcessingUtil.sharpen_image(image)

        # Step 8: Convert to binary (for better OCR)
        image = ImageProcessingUtil.convert_to_binary(image)

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

    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image to target dimensions while maintaining aspect ratio
        """
        return ImageProcessingUtil.resize_image(image, self.target_width, self.target_height)

    def preprocess_for_ocr(self, image_path: str, output_path: Optional[str] = None) -> str:
        """
        Specialized preprocessing pipeline optimized for OCR
        """
        # Load image
        image = cv2.imread(image_path)

        # Apply transformations in sequence optimized for OCR
        processed_image = self._apply_ocr_optimized_transformations(image)

        # Save the processed image
        if output_path:
            cv2.imwrite(output_path, processed_image)
            return output_path
        else:
            base_path, ext = os.path.splitext(image_path)
            output_path = f"{base_path}_ocr_processed{ext}"
            cv2.imwrite(output_path, processed_image)
            return output_path

    def _apply_ocr_optimized_transformations(self, image: np.ndarray) -> np.ndarray:
        """
        Apply transformations specifically optimized for OCR
        """
        # Step 1: Rotate if needed
        image = ImageProcessingUtil.rotate_image_if_needed_from_array(image)

        # Step 2: Resize to optimal OCR size
        image = self.resize_image_for_ocr(image)

        # Step 3: Deskew
        image = ImageProcessingUtil.deskew_image(image)

        # Step 4: Enhance contrast
        image = ImageProcessingUtil.enhance_contrast(image)

        # Step 5: Remove noise
        image = ImageProcessingUtil.remove_noise(image)

        # Step 6: Convert to binary
        image = ImageProcessingUtil.convert_to_binary(image)

        # Step 7: Additional sharpening for OCR
        image = ImageProcessingUtil.sharpen_image(image)

        return image

    def resize_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image to an optimal size for OCR (typically higher resolution)
        """
        # For OCR, we often want higher resolution than for display
        return ImageProcessingUtil.resize_image(image, 2480, 3508)  # A4 at 300 DPI

    def validate_preprocessing_result(self, original_path: str, processed_path: str) -> dict:
        """
        Validate that preprocessing improved the image quality for OCR
        """
        original_image = cv2.imread(original_path)
        processed_image = cv2.imread(processed_path)

        # Calculate some metrics to compare quality
        original_variance = np.var(cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY))
        processed_variance = np.var(cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY))

        return {
            "original_variance": float(original_variance),
            "processed_variance": float(processed_variance),
            "variance_improved": processed_variance > original_variance,
            "original_shape": original_image.shape,
            "processed_shape": processed_image.shape
        }


