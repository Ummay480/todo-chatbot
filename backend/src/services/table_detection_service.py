import cv2
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from ..services.structure_detection_service import StructureDetectionService, TableColumn, TableRow


@dataclass
class TableStructure:
    """
    Data class to represent detected table structure
    """
    columns: List[TableColumn]
    rows: List[TableRow]
    confidence: float
    cell_coordinates: List[Tuple[int, int, int, int]]  # x, y, width, height for each cell


class TableDetectionService:
    """
    Enhanced service for detecting table structures in ledger images
    """

    def __init__(self):
        self.structure_detector = StructureDetectionService()

    def detect_table_structure(self, image_path: str) -> TableStructure:
        """
        Detect table structure with enhanced accuracy for ledger formats
        """
        # Use the base structure detector to get initial results
        columns, rows = self.structure_detector.detect_table_structure(image_path)

        # Enhance the detection with ledger-specific logic
        enhanced_columns = self._enhance_column_detection(image_path, columns)
        enhanced_rows = self._enhance_row_detection(image_path, rows)

        # Calculate overall confidence based on consistency
        confidence = self._calculate_structure_confidence(enhanced_columns, enhanced_rows)

        # Get cell coordinates
        cell_coords = self._get_cell_coordinates(enhanced_columns, enhanced_rows)

        return TableStructure(
            columns=enhanced_columns,
            rows=enhanced_rows,
            confidence=confidence,
            cell_coordinates=cell_coords
        )

    def _enhance_column_detection(self, image_path: str, columns: List[TableColumn]) -> List[TableColumn]:
        """
        Enhance column detection with ledger-specific heuristics
        """
        # Load image to analyze content in each column
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        enhanced_columns = []
        for i, col in enumerate(columns):
            # Analyze the content of this column to refine the name
            refined_name = self._refine_column_name(image_path, col)

            # Calculate enhanced confidence based on content consistency
            content_confidence = self._analyze_column_content(image_path, col)

            enhanced_col = TableColumn(
                name=refined_name,
                position=col.position,
                left_x=col.left_x,
                right_x=col.right_x,
                confidence=min(col.confidence, content_confidence)
            )

            enhanced_columns.append(enhanced_col)

        return enhanced_columns

    def _refine_column_name(self, image_path: str, column: TableColumn) -> str:
        """
        Refine column name based on content analysis
        """
        # Extract a region from the top of the column to analyze header
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        # Define a region at the top of the column to look for header text
        roi_top = int(height * 0.02)  # Start 2% down from the top
        roi_bottom = int(height * 0.10)  # End 10% down from the top
        roi = img[roi_top:roi_bottom, column.left_x:column.right_x]

        if roi.size > 0:
            import pytesseract
            from PIL import Image

            # Convert to PIL Image for Tesseract
            pil_roi = Image.fromarray(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))

            # Extract text from header region
            header_text = pytesseract.image_to_string(pil_roi, config='--psm 7').strip()  # Single text line mode

            if header_text:
                # Look for common ledger column headers
                header_lower = header_text.lower()

                # More specific pattern matching for ledger headers
                if any(pattern in header_lower for pattern in ['date', 'dt', 'tarikh', 'din']):
                    return 'Date'
                elif any(pattern in header_lower for pattern in ['nozzle', 'pump', 'nuz', 'pmp', 'machine', 'mach']):
                    return 'Nozzle ID'
                elif any(pattern in header_lower for pattern in ['fuel', 'type', 'ftype', 'fueltype', 'category', 'cat']):
                    return 'Fuel Type'
                elif any(pattern in header_lower for pattern in ['open', 'start', 'opn', 'strt', 'initial', 'beg']):
                    return 'Opening Reading'
                elif any(pattern in header_lower for pattern in ['close', 'end', 'cls', 'fin', 'final']):
                    return 'Closing Reading'
                elif any(pattern in header_lower for pattern in ['liter', 'litre', 'ltr', 'qty', 'quantity', 'qnty']):
                    return 'Liters Sold'
                elif any(pattern in header_lower for pattern in ['rate', 'price', 'r/l', 'p/l', 'per', 'perltr']):
                    return 'Rate Per Liter'
                elif any(pattern in header_lower for pattern in ['amount', 'total', 'amt', 'ttl', 'sum', 'cash', 'rs']):
                    return 'Total Amount'
                elif any(pattern in header_lower for pattern in ['sn', 'no', 'num', 'sr', 'sno']):
                    return 'Serial Number'
                else:
                    # Return cleaned up version of detected text
                    cleaned = header_text.replace('\n', ' ').strip()
                    if len(cleaned) <= 20 and any(c.isalpha() for c in cleaned):
                        return cleaned.title()

        # If no specific header found, return the original name or a generic one
        return column.name if column.name != f"Column_{column.position}" else self._guess_column_type_by_position(len(columns), column.position)

    def _guess_column_type_by_position(self, total_cols: int, position: int) -> str:
        """
        Guess column type based on position in a typical ledger
        """
        # Typical ledger layouts often have: Date, Nozzle, Fuel Type, Opening, Closing, Liters, Rate, Amount
        typical_positions = {
            0: "Date",
            1: "Nozzle ID",
            2: "Fuel Type",
            3: "Opening Reading",
            4: "Closing Reading",
            5: "Liters Sold",
            6: "Rate Per Liter",
            7: "Total Amount"
        }

        return typical_positions.get(position, f"Column_{position}")

    def _analyze_column_content(self, image_path: str, column: TableColumn) -> float:
        """
        Analyze column content to determine confidence in column type
        """
        # This would involve looking at the content distribution in the column
        # For now, return a default confidence based on how well the name matches expected types
        expected_names = ["Date", "Nozzle ID", "Fuel Type", "Opening Reading", "Closing Reading", "Liters Sold", "Rate Per Liter", "Total Amount"]

        if column.name in expected_names:
            return 0.95
        elif any(expected.lower() in column.name.lower() for expected in expected_names):
            return 0.85
        else:
            return 0.70  # Lower confidence for unrecognized column names

    def _enhance_row_detection(self, image_path: str, rows: List[TableRow]) -> List[TableRow]:
        """
        Enhance row detection with ledger-specific logic
        """
        # For now, just pass through the rows with possible enhancements
        # In a more sophisticated implementation, we could validate row consistency
        # and detect missing data patterns typical in ledgers

        enhanced_rows = []
        for row in rows:
            # Validate that this looks like a legitimate data row (not just whitespace or artifacts)
            if self._is_valid_data_row(row):
                enhanced_rows.append(row)

        return enhanced_rows

    def _is_valid_data_row(self, row: TableRow) -> bool:
        """
        Check if a row contains valid data (not just empty or artifacts)
        """
        # Count non-empty data fields
        non_empty_fields = sum(1 for value in row.data.values() if value.strip())
        total_fields = len(row.data)

        # A valid row should have at least half its fields filled
        if total_fields > 0:
            return (non_empty_fields / total_fields) >= 0.5
        else:
            return False

    def _calculate_structure_confidence(self, columns: List[TableColumn], rows: List[TableRow]) -> float:
        """
        Calculate overall confidence in the detected table structure
        """
        if len(columns) < 3 or len(rows) < 2:
            # Too few columns/rows for a proper ledger table
            return 0.3

        # Calculate average column confidence
        avg_col_confidence = sum(col.confidence for col in columns) / len(columns) if columns else 0

        # Calculate average row confidence
        avg_row_confidence = sum(row.confidence for row in rows) / len(rows) if rows else 0

        # Combine confidences with weights
        structure_confidence = (avg_col_confidence * 0.6 + avg_row_confidence * 0.4)

        # Boost confidence if we have expected ledger columns
        expected_columns = {"date", "nozzle id", "fuel type", "liters sold", "total amount"}
        found_columns = {col.name.lower() for col in columns}
        matching_expected = expected_columns.intersection(found_columns)
        expected_match_ratio = len(matching_expected) / len(expected_columns)

        # Adjust overall confidence based on how many expected columns we found
        final_confidence = structure_confidence * 0.7 + expected_match_ratio * 0.3

        return min(final_confidence, 1.0)  # Cap at 1.0

    def _get_cell_coordinates(self, columns: List[TableColumn], rows: List[TableRow]) -> List[Tuple[int, int, int, int]]:
        """
        Calculate coordinates for each cell in the table
        """
        cell_coords = []

        for row in rows:
            for col in columns:
                # Calculate cell coordinates based on column and row boundaries
                x = col.left_x
                y = row.top_y
                w = col.right_x - col.left_x
                h = row.bottom_y - row.top_y

                cell_coords.append((x, y, w, h))

        return cell_coords

    def detect_ledger_specific_features(self, image_path: str) -> Dict[str, any]:
        """
        Detect ledger-specific features like total lines, headers, footers
        """
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Look for common ledger patterns
        features = {
            'has_header': self._detect_header_row(image_path),
            'has_total_line': self._detect_total_line(image_path),
            'has_signature_line': self._detect_signature_line(image_path),
            'estimated_columns': len(self.structure_detector.detect_table_structure(image_path)[0]),
            'estimated_rows': len(self.structure_detector.detect_table_structure(image_path)[1])
        }

        return features

    def _detect_header_row(self, image_path: str) -> bool:
        """
        Detect if the image contains a header row
        """
        # Look for text that appears to be a header in the upper portion of the image
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        # Analyze top 15% of image for header patterns
        header_region = img[int(0.02*height):int(0.15*height), 0:width]

        if header_region.size > 0:
            import pytesseract
            from PIL import Image

            pil_region = Image.fromarray(cv2.cvtColor(header_region, cv2.COLOR_BGR2RGB))
            text = pytesseract.image_to_string(pil_region).strip()

            # Look for common header keywords
            header_keywords = ['date', 'nozzle', 'fuel', 'liter', 'amount', 'total', 'sl', 'sr', 'no', 'qty']
            text_lower = text.lower()

            return any(keyword in text_lower for keyword in header_keywords)

        return False

    def _detect_total_line(self, image_path: str) -> bool:
        """
        Detect if the image contains a total line
        """
        # Look for "total", "total:", "sum", etc. in the lower portion of the image
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        # Analyze bottom 20% of image for total patterns
        footer_region = img[int(0.8*height):height, 0:width]

        if footer_region.size > 0:
            import pytesseract
            from PIL import Image

            pil_region = Image.fromarray(cv2.cvtColor(footer_region, cv2.COLOR_BGR2RGB))
            text = pytesseract.image_to_string(pil_region).strip()

            # Look for total-related keywords
            total_keywords = ['total', 'sum', 'grand', 'overall', 'final', 'ending', '合计', 'total:']
            text_lower = text.lower()

            return any(keyword in text_lower for keyword in total_keywords)

        return False

    def _detect_signature_line(self, image_path: str) -> bool:
        """
        Detect if the image contains a signature line
        """
        # Look for signature-related text in the bottom portion
        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        # Analyze bottom 15% of image for signature patterns
        signature_region = img[int(0.85*height):height, 0:width]

        if signature_region.size > 0:
            import pytesseract
            from PIL import Image

            pil_region = Image.fromarray(cv2.cvtColor(signature_region, cv2.COLOR_BGR2RGB))
            text = pytesseract.image_to_string(pil_region).strip()

            # Look for signature-related keywords
            sig_keywords = ['signature', 'sign', 'sgn', 'verified', 'approved', 'manager', 'auth', 'authorized']
            text_lower = text.lower()

            return any(keyword in text_lower for keyword in sig_keywords)

        return False

    def validate_detected_structure(self, image_path: str, structure: TableStructure) -> Dict[str, any]:
        """
        Validate the detected table structure for ledger-specific consistency
        """
        validation_results = {
            'is_valid_structure': True,
            'issues': [],
            'suggestions': []
        }

        # Check if structure has minimum required columns for a ledger
        if len(structure.columns) < 3:
            validation_results['is_valid_structure'] = False
            validation_results['issues'].append('Too few columns detected for a ledger table')
            validation_results['suggestions'].append('Verify the image has clear column separators')

        # Check if structure has reasonable number of rows
        if len(structure.rows) < 1:
            validation_results['is_valid_structure'] = False
            validation_results['issues'].append('No data rows detected')
            validation_results['suggestions'].append('Verify the image has clear row separators')

        # Check confidence level
        if structure.confidence < 0.7:
            validation_results['is_valid_structure'] = False
            validation_results['issues'].append(f'Low confidence in structure detection: {structure.confidence:.2f}')
            validation_results['suggestions'].append('Consider improving image quality or adjusting detection parameters')

        return validation_results