from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
import re
from ..services.structure_detection_service import TableColumn


@dataclass
class IdentifiedColumn:
    """
    Data class for a column that has been identified with its type
    """
    name: str
    position: int
    left_x: int
    right_x: int
    confidence: float
    column_type: str  # The identified type of this column
    patterns_found: List[str]  # Patterns that helped identify this column
    alternative_names: List[str]  # Possible alternative names for this column


class ColumnIdentificationService:
    """
    Service for identifying and classifying columns in ledger tables
    """

    def __init__(self):
        # Define patterns for different column types
        self.column_patterns = {
            'date': [
                r'\bdate\b', r'\bdt\b', r'\bdin\b', r'\btarikh\b',  # English/Urdu variants
                r'\bday\b', r'\bsanday\b', r'\bmon\b', r'\btue\b',  # Day abbreviations
                r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}'  # Date format
            ],
            'nozzle_id': [
                r'\bnozzle\b', r'\bnuz\b', r'\bpump\b', r'\bpmp\b', r'\bmachine\b', r'\bmach\b',
                r'\bid\b', r'\bno\b', r'\bsr\b', r'\bsn\b',  # Common abbreviations
                r'^[A-Z0-9]+$',  # Alphanumeric identifiers
                r'^\d+$'  # Numeric identifiers
            ],
            'fuel_type': [
                r'\bfuel\b', r'\btype\b', r'\bftype\b', r'\bfueltype\b',
                r'\bcategory\b', r'\bcat\b', r'\bkind\b',
                r'\bpetrol\b', r'\bdiesel\b', r'\bcng\b', r'\bgasoline\b',  # Fuel types
                r'\bbenzen\b', r'\bkerosene\b', r'\boctane\b'
            ],
            'opening_reading': [
                r'\bopen\b', r'\bstart\b', r'\bopn\b', r'\bstrt\b',
                r'\binitial\b', r'\bbegin\b', r'\breading\b', r'\breading_start\b',
                r'\binput\b', r'\bin\b'
            ],
            'closing_reading': [
                r'\bclose\b', r'\bend\b', r'\bcls\b', r'\bfin\b',
                r'\bfinal\b', r'\breading_end\b', r'\breading\b',
                r'\boutput\b', r'\bout\b'
            ],
            'liters_sold': [
                r'\bliter\b', r'\blitre\b', r'\bltr\b', r'\bqty\b', r'\bquantity\b', r'\bqnty\b',
                r'\bsold\b', r'\bdelivered\b', r'\bdispensed\b',
                r'^\d+\.?\d*$'  # Numeric values (would need context)
            ],
            'rate_per_liter': [
                r'\brate\b', r'\bprice\b', r'\br/l\b', r'\bp/l\b', r'\bper\b', r'\bperltr\b',
                r'\bcost\b', r'\bcharge\b', r'\bfare\b',
                r'^\d+\.?\d*$'  # Numeric values (would need context)
            ],
            'total_amount': [
                r'\bamount\b', r'\btotal\b', r'\bamt\b', r'\bttl\b', r'\bsum\b',
                r'\bcash\b', r'\brs\b', r'\brupees\b', r'\bpkr\b', r'\bcurrency\b',
                r'^\d+\.?\d*$'  # Numeric values (would need context)
            ]
        }

    def identify_columns(self, detected_columns: List[TableColumn], image_path: str = None) -> List[IdentifiedColumn]:
        """
        Identify the type of each column based on patterns and context
        :param detected_columns: List of detected columns from structure detection
        :param image_path: Optional image path to analyze column content
        :return: List of identified columns with their types
        """
        identified_columns = []

        for col in detected_columns:
            identified_col = self._identify_single_column(col, image_path)
            identified_columns.append(identified_col)

        return identified_columns

    def _identify_single_column(self, column: TableColumn, image_path: str = None) -> IdentifiedColumn:
        """
        Identify a single column's type
        """
        # If we have an image path, analyze the content of the column
        if image_path:
            content_analysis = self._analyze_column_content(image_path, column)
        else:
            content_analysis = {'patterns': [], 'values_sample': []}

        # Identify the column type based on name and content
        column_type, confidence, patterns = self._determine_column_type(
            column.name, content_analysis['patterns'], content_analysis['values_sample']
        )

        return IdentifiedColumn(
            name=column.name,
            position=column.position,
            left_x=column.left_x,
            right_x=column.right_x,
            confidence=confidence,
            column_type=column_type,
            patterns_found=patterns,
            alternative_names=self._get_alternative_names(column_type)
        )

    def _analyze_column_content(self, image_path: str, column: TableColumn) -> Dict[str, any]:
        """
        Analyze the content of a column to help identify its type
        """
        import cv2
        from PIL import Image
        import pytesseract

        img = cv2.imread(image_path)
        height, width = img.shape[:2]

        # Extract a sample of content from the column (middle portion to avoid headers)
        sample_top = int(height * 0.25)
        sample_bottom = int(height * 0.75)
        column_roi = img[sample_top:sample_bottom, column.left_x:column.right_x]

        if column_roi.size > 0:
            # Convert to PIL Image for OCR
            pil_roi = Image.fromarray(cv2.cvtColor(column_roi, cv2.COLOR_BGR2RGB))

            # Extract text
            text = pytesseract.image_to_string(pil_roi).strip()

            # Analyze the text for patterns
            patterns_found = []
            values_sample = []

            # Look for patterns in the text
            for col_type, patterns in self.column_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        patterns_found.append(pattern)

            # Extract potential values
            # Look for numbers, dates, etc.
            numbers = re.findall(r'\b\d+\.?\d*\b', text)
            dates = re.findall(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b', text)

            values_sample.extend(numbers[:5])  # Limit to first 5 samples
            values_sample.extend(dates[:2])   # Limit to first 2 date samples

            return {
                'patterns': patterns_found,
                'values_sample': values_sample
            }

        return {'patterns': [], 'values_sample': []}

    def _determine_column_type(self, column_name: str, content_patterns: List[str], content_values: List[str]) -> Tuple[str, float, List[str]]:
        """
        Determine the column type based on name, content patterns, and values
        """
        # Score each possible column type
        scores = {}
        matched_patterns = {}

        # Score based on column name
        for col_type, patterns in self.column_patterns.items():
            score = 0
            matched = []

            for pattern in patterns:
                if re.search(pattern, column_name, re.IGNORECASE):
                    score += 2  # Higher weight for name matching
                    matched.append(pattern)

            scores[col_type] = score
            matched_patterns[col_type] = matched

        # Score based on content patterns
        for col_type, patterns in self.column_patterns.items():
            for pattern in patterns:
                if pattern in content_patterns:
                    scores[col_type] = scores.get(col_type, 0) + 1

        # Score based on content values (special patterns like numbers for amount columns)
        for col_type in scores:
            if col_type in ['liters_sold', 'rate_per_liter', 'total_amount']:
                # These types are likely to contain numbers
                if any(re.match(r'^\d+\.?\d*$', val) for val in content_values):
                    scores[col_type] = scores.get(col_type, 0) + 1

        # Find the best match
        if scores:
            best_type = max(scores, key=scores.get)
            best_score = scores[best_type]

            # Calculate confidence (normalize score to 0-1 range)
            max_possible_score = len(self.column_patterns[best_type]) * 2  # If all name patterns matched
            if max_possible_score == 0:
                max_possible_score = 10  # Fallback

            confidence = min(best_score / max_possible_score * 2, 1.0)  # Multiply by 2 since max score is conservative

            return best_type, confidence, matched_patterns[best_type]
        else:
            # If no patterns match, make a guess based on position (common ledger layouts)
            return self._guess_by_position(column_name, 0), 0.3, []

    def _guess_by_position(self, column_name: str, position: int) -> str:
        """
        Guess column type based on its position in the table
        """
        # Typical ledger layouts often have: Date, Nozzle, Fuel Type, Opening, Closing, Liters, Rate, Amount
        typical_positions = {
            0: "date",
            1: "nozzle_id",
            2: "fuel_type",
            3: "opening_reading",
            4: "closing_reading",
            5: "liters_sold",
            6: "rate_per_liter",
            7: "total_amount"
        }

        return typical_positions.get(position, "unknown")

    def _get_alternative_names(self, column_type: str) -> List[str]:
        """
        Get alternative names for a column type
        """
        alternatives = {
            'date': ['dt', 'tarikh', 'din', 'day'],
            'nozzle_id': ['nuz', 'pmp', 'mach', 'id', 'no'],
            'fuel_type': ['ftype', 'fueltype', 'cat', 'category'],
            'opening_reading': ['opn', 'strt', 'begin', 'input'],
            'closing_reading': ['cls', 'fin', 'end', 'final', 'output'],
            'liters_sold': ['ltr', 'qty', 'qnty', 'sold'],
            'rate_per_liter': ['r/l', 'p/l', 'perltr', 'cost'],
            'total_amount': ['amt', 'ttl', 'cash', 'rs']
        }

        return alternatives.get(column_type, [])

    def validate_column_identification(self, identified_columns: List[IdentifiedColumn]) -> Dict[str, any]:
        """
        Validate the column identification results
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'missing_critical_columns': [],
            'confidence_issues': []
        }

        # Check for critical columns that should be in a ledger
        critical_columns = {'date', 'fuel_type', 'liters_sold', 'total_amount'}
        found_columns = {col.column_type.lower() for col in identified_columns}

        missing = critical_columns - found_columns
        validation['missing_critical_columns'] = list(missing)

        if missing:
            validation['is_valid'] = False
            validation['warnings'].append(f'Missing critical columns: {", ".join(missing)}')

        # Check for low confidence identifications
        low_confidence_cols = [col for col in identified_columns if col.confidence < 0.6]
        if low_confidence_cols:
            validation['confidence_issues'] = [
                f"{col.name} ({col.column_type}): {col.confidence:.2f}"
                for col in low_confidence_cols
            ]
            validation['warnings'].append(f"Low confidence in {len(low_confidence_cols)} column identifications")

        return validation

    def suggest_corrections(self, identified_columns: List[IdentifiedColumn], image_path: str = None) -> List[Dict[str, any]]:
        """
        Suggest corrections for potentially misidentified columns
        """
        suggestions = []

        for i, col in enumerate(identified_columns):
            # Check if the identification makes sense in context
            if col.confidence < 0.7:
                # Suggest alternative identifications
                alternatives = self._get_alternative_identifications(col, identified_columns, image_path)

                if alternatives:
                    suggestions.append({
                        'column_index': i,
                        'current_identification': col.column_type,
                        'confidence': col.confidence,
                        'alternatives': alternatives,
                        'reason': 'Low confidence identification'
                    })

        return suggestions

    def _get_alternative_identifications(self, column: IdentifiedColumn, all_columns: List[IdentifiedColumn], image_path: str = None) -> List[str]:
        """
        Get alternative identifications for a column
        """
        # This would involve re-analyzing the column with different assumptions
        # For now, return the alternative names for this column
        return self._get_alternative_names(column.column_type)

    def create_column_mapping(self, identified_columns: List[IdentifiedColumn]) -> Dict[str, str]:
        """
        Create a mapping from column names to standard ledger field names
        """
        mapping = {}
        for col in identified_columns:
            # Map to standard field names used in the system
            standard_name = self._to_standard_field_name(col.column_type)
            mapping[col.name] = standard_name

        return mapping

    def _to_standard_field_name(self, column_type: str) -> str:
        """
        Convert column type to standard field name used in the system
        """
        standard_mapping = {
            'date': 'date',
            'nozzle_id': 'nozzle_id',
            'fuel_type': 'fuel_type',
            'opening_reading': 'opening_reading',
            'closing_reading': 'closing_reading',
            'liters_sold': 'liters_sold',
            'rate_per_liter': 'rate_per_liter',
            'total_amount': 'total_amount'
        }

        return standard_mapping.get(column_type, column_type)