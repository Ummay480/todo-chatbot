"""
OCR Service for Petrol Pump Ledger Automation

This module provides OCR functionality for extracting text from images
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Any


class OCRService:
    """
    Service class for performing OCR on images
    """

    def __init__(self):
        """
        Initialize the OCR service
        """
        # You can set additional Tesseract configuration here if needed
        # For example: self.config = r'--oem 3 --psm 6'
        pass

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from an image using OCR

        Args:
            image_path: Path to the image file

        Returns:
            Extracted text as a string
        """
        # Load image using PIL
        img = Image.open(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(img)
        
        return text

    def extract_structured_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract structured data from an image

        Args:
            image_path: Path to the image file

        Returns:
            Dictionary containing extracted data and metadata
        """
        # Load image
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Perform OCR with data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Filter out empty text entries
        n_boxes = len(data['text'])
        extracted_elements = []
        confidence_scores = []
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0:  # Only include elements with confidence > 0
                element = {
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': int(data['conf'][i])
                }
                extracted_elements.append(element)
                
                if int(data['conf'][i]) > 0:  # Only include valid confidences
                    confidence_scores.append(int(data['conf'][i]))
        
        # Calculate average confidence
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
        
        return {
            'elements': extracted_elements,
            'confidence_avg': avg_confidence,
            'total_elements': len(extracted_elements),
            'image_path': image_path
        }

    def extract_text_with_confidence(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text elements with their confidence scores

        Args:
            image_path: Path to the image file

        Returns:
            List of dictionaries containing text, position, and confidence
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        elements = []
        n_boxes = len(data['text'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 0 and data['text'][i].strip():  # Only include non-empty text with confidence > 0
                element = {
                    'text': data['text'][i].strip(),
                    'bbox': (data['left'][i], data['top'][i], 
                            data['left'][i] + data['width'][i], 
                            data['top'][i] + data['height'][i]),
                    'confidence': int(data['conf'][i])
                }
                elements.append(element)
        
        return elements
