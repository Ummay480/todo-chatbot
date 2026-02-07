import pytesseract
from PIL import Image
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from ..services.ocr_service import OCRService, OCRResult


@dataclass
class ExtractionResult:
    """
    Data class to hold the results of text extraction
    """
    text: str
    confidence: float
    bounding_box: Optional[Tuple[int, int, int, int]]
    field_type: str  # e.g., 'date', 'nozzle_id', 'fuel_type', 'liters', 'amount', etc.
    extracted_value: any  # The parsed value (could be date, number, string, etc.)


class OCRIntegrationService:
    """
    Service for integrating OCR functionality with ledger processing
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        self.ocr_service = OCRService(tesseract_path)

    def extract_ledger_data(self, image_path: str) -> Dict[str, any]:
        """
        Extract structured ledger data from an image
        """
        # First, get the overall structure
        structure_data = self.ocr_service.extract_structured_data(image_path)

        # Then, detect table structure
        from ..services.structure_detection_service import StructureDetectionService
        structure_detector = StructureDetectionService()
        columns, rows = structure_detector.detect_table_structure(image_path)

        # Process each row to extract field-specific data
        processed_rows = []
        for row in rows:
            processed_row = self._process_row_data(row, columns)
            processed_rows.append(processed_row)

        return {
            'raw_ocr_results': structure_data['ocr_results'],
            'detected_columns': [col.__dict__ for col in columns],
            'extracted_rows': processed_rows,
            'overall_confidence': structure_data['confidence_avg'],
            'word_count': structure_data['word_count'],
            'text_regions': structure_data['text_regions']
        }

    def _process_row_data(self, row, columns) -> Dict[str, ExtractionResult]:
        """
        Process a single row to extract field-specific data
        """
        processed_data = {}

        # Map each column name to its extracted value
        for col_name, value in row.data.items():
            field_type = self._identify_field_type(col_name)
            confidence = row.confidence  # Use row confidence as base

            # Adjust confidence based on value characteristics
            if self._is_valid_field_value(value, field_type):
                adjusted_confidence = confidence * 0.95  # Slightly reduce for valid values
            else:
                adjusted_confidence = confidence * 0.7  # Reduce more for potentially invalid values

            processed_data[col_name.lower().replace(' ', '_')] = ExtractionResult(
                text=value,
                confidence=adjusted_confidence,
                bounding_box=None,  # Would need to calculate from original image coordinates
                field_type=field_type,
                extracted_value=self._parse_field_value(value, field_type)
            )

        return processed_data

    def _identify_field_type(self, column_name: str) -> str:
        """
        Identify the type of data in a column based on its name
        """
        column_name_lower = column_name.lower()

        if any(keyword in column_name_lower for keyword in ['date', 'day', 'time']):
            return 'date'
        elif any(keyword in column_name_lower for keyword in ['nozzle', 'pump', 'dispenser', 'machine']):
            return 'nozzle_id'
        elif any(keyword in column_name_lower for keyword in ['fuel', 'type', 'category']):
            return 'fuel_type'
        elif any(keyword in column_name_lower for keyword in ['open', 'start', 'initial', 'begin']):
            return 'opening_reading'
        elif any(keyword in column_name_lower for keyword in ['close', 'end', 'final', 'finish']):
            return 'closing_reading'
        elif any(keyword in column_name_lower for keyword in ['liter', 'litre', 'qty', 'quantity']):
            return 'liters_sold'
        elif any(keyword in column_name_lower for keyword in ['rate', 'price', 'per_liter']):
            return 'rate_per_liter'
        elif any(keyword in column_name_lower for keyword in ['amount', 'total', 'sum', 'value']):
            return 'total_amount'
        else:
            return 'unknown'

    def _is_valid_field_value(self, value: str, field_type: str) -> bool:
        """
        Check if a value is valid for its expected field type
        """
        if not value.strip():
            return False

        if field_type == 'date':
            return self._is_valid_date(value)
        elif field_type in ['opening_reading', 'closing_reading', 'liters_sold', 'rate_per_liter', 'total_amount']:
            return self._is_valid_number(value)
        elif field_type == 'fuel_type':
            return self._is_valid_fuel_type(value)
        elif field_type == 'nozzle_id':
            return len(value.strip()) > 0
        else:
            return True  # For unknown types, assume valid if not empty

    def _is_valid_date(self, date_str: str) -> bool:
        """
        Check if a string represents a valid date
        """
        import re
        # Simple regex for common date formats: DD/MM/YYYY, DD-MM-YYYY, MM/DD/YYYY, etc.
        date_pattern = r'\b(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[0-2])[\/\-](\d{4})\b|\b(0?[1-9]|1[0-2])[\/\-](0?[1-9]|[12][0-9]|3[01])[\/\-](\d{4})\b'
        return bool(re.search(date_pattern, date_str))

    def _is_valid_number(self, num_str: str) -> bool:
        """
        Check if a string represents a valid number
        """
        import re
        # Remove commas and other formatting
        clean_num = re.sub(r'[^\d.-]', '', num_str)
        try:
            float(clean_num)
            return True
        except ValueError:
            return False

    def _is_valid_fuel_type(self, fuel_str: str) -> bool:
        """
        Check if a string represents a valid fuel type
        """
        valid_fuels = ['petrol', 'diesel', 'cng', 'gasoline', 'benzene', 'kerosene', 'octane', 'premium']
        return any(fuel.lower() in fuel_str.lower() for fuel in valid_fuels)

    def _parse_field_value(self, value: str, field_type: str) -> any:
        """
        Parse a field value to its appropriate data type
        """
        if field_type == 'date':
            return self._parse_date(value)
        elif field_type in ['opening_reading', 'closing_reading', 'liters_sold', 'rate_per_liter', 'total_amount']:
            return self._parse_number(value)
        else:
            return value.strip()

    def _parse_date(self, date_str: str):
        """
        Parse a date string to a date object
        """
        import re
        from datetime import datetime

        # Try common formats
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d']

        # Clean the date string
        clean_date = re.sub(r'[^\d\/\-]', ' ', date_str).strip()

        for fmt in formats:
            try:
                return datetime.strptime(clean_date, fmt).date()
            except ValueError:
                continue

        # If no format works, return the original string
        return date_str

    def _parse_number(self, num_str: str) -> Optional[float]:
        """
        Parse a number string to a float
        """
        import re

        # Remove non-numeric characters except decimal point and minus sign
        clean_num = re.sub(r'[^\d.-]', '', num_str)

        try:
            return float(clean_num)
        except ValueError:
            return None

    def extract_specific_fields(self, image_path: str, field_types: List[str]) -> Dict[str, List[ExtractionResult]]:
        """
        Extract only specific field types from the image
        :param image_path: Path to the image file
        :param field_types: List of field types to extract
        :return: Dictionary mapping field types to lists of extraction results
        """
        all_data = self.extract_ledger_data(image_path)
        results = {field_type: [] for field_type in field_types}

        for row_data in all_data['extracted_rows']:
            for field_name, extraction_result in row_data.items():
                if extraction_result.field_type in field_types:
                    results[extraction_result.field_type].append(extraction_result)

        return results

    def get_confidence_score(self, image_path: str) -> float:
        """
        Get an overall confidence score for OCR on this image
        """
        ocr_results = self.ocr_service.extract_text_with_confidence(image_path)

        if not ocr_results:
            return 0.0

        # Calculate average confidence
        total_confidence = sum(result.confidence for result in ocr_results)
        return total_confidence / len(ocr_results)

    def extract_with_confidence_threshold(self, image_path: str, threshold: float = 85.0) -> Dict[str, any]:
        """
        Extract data but flag items with confidence below threshold
        """
        all_data = self.extract_ledger_data(image_path)

        # Add confidence flags to results
        for row_idx, row_data in enumerate(all_data['extracted_rows']):
            for field_name, extraction_result in row_data.items():
                all_data['extracted_rows'][row_idx][field_name] = {
                    'result': extraction_result,
                    'needs_review': extraction_result.confidence < threshold
                }

        return all_data