from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.SalesEntry import SalesEntry
from ..services.ocr_integration_service import OCRIntegrationService
from ..services.column_identification_service import IdentifiedColumn
import re


class SalesEntryExtractionService:
    """
    Service for extracting sales entries from processed ledger data
    """

    def __init__(self):
        self.ocr_service = OCRIntegrationService()

    def extract_sales_entries(self, processed_data: Dict[str, any], column_mappings: Dict[str, str]) -> List[SalesEntry]:
        """
        Extract sales entries from processed ledger data
        :param processed_data: Dictionary containing processed ledger data
        :param column_mappings: Mapping from detected column names to standard field names
        :return: List of SalesEntry objects
        """
        sales_entries = []

        # Process each row of extracted data
        for row_data in processed_data.get('extracted_rows', []):
            entry = self._extract_single_sales_entry(row_data, column_mappings)
            if entry:
                sales_entries.append(entry)

        return sales_entries

    def _extract_single_sales_entry(self, row_data: Dict[str, any], column_mappings: Dict[str, str]) -> Optional[SalesEntry]:
        """
        Extract a single sales entry from row data
        """
        # Create a mapping from standard field names to values
        field_values = {}
        for col_name, result_obj in row_data.items():
            # Get the standard field name for this column
            if isinstance(result_obj, dict) and 'result' in result_obj:
                # Handle the case where result is wrapped with review flag
                result = result_obj['result']
            else:
                # Handle the case where result is directly in the dict
                result = result_obj

            standard_field = column_mappings.get(col_name.lower().replace(' ', '_'))

            if standard_field:
                field_values[standard_field] = result.extracted_value

        # Create a SalesEntry object with the extracted values
        try:
            # Convert field values to appropriate types
            entry_data = {
                'date': self._parse_date(field_values.get('date')),
                'nozzle_id': str(field_values.get('nozzle_id', '')),
                'fuel_type': self._normalize_fuel_type(str(field_values.get('fuel_type', ''))),
                'opening_reading': self._parse_float(field_values.get('opening_reading')),
                'closing_reading': self._parse_float(field_values.get('closing_reading')),
                'liters_sold': self._parse_float(field_values.get('liters_sold')),
                'rate_per_liter': self._parse_float(field_values.get('rate_per_liter')),
                'total_amount': self._parse_float(field_values.get('total_amount')),
                'ocr_confidence': self._calculate_row_confidence(row_data)
            }

            # Calculate liters sold if not provided (using opening and closing readings)
            if entry_data['liters_sold'] is None and entry_data['opening_reading'] and entry_data['closing_reading']:
                entry_data['liters_sold'] = self._calculate_liters_from_readings(
                    entry_data['opening_reading'], entry_data['closing_reading']
                )

            # Calculate total amount if not provided (using liters sold and rate per liter)
            if entry_data['total_amount'] is None and entry_data['liters_sold'] and entry_data['rate_per_liter']:
                entry_data['total_amount'] = self._calculate_amount_from_rate(
                    entry_data['liters_sold'], entry_data['rate_per_liter']
                )

            # Create the SalesEntry object
            # Note: We can't create the full object here because we don't have all required fields like ledger_page_id
            # This would be handled by the calling function which has access to the ledger page
            return SalesEntry(**{k: v for k, v in entry_data.items() if v is not None})

        except Exception as e:
            # Log the error and return None if the entry can't be created
            print(f"Error creating sales entry: {e}")
            return None

    def _parse_date(self, date_value: any) -> Optional[datetime]:
        """
        Parse date value to datetime object
        """
        if date_value is None:
            return None

        if isinstance(date_value, datetime):
            return date_value

        if isinstance(date_value, str):
            # Try common date formats
            formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y']

            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue

            # If none of the formats work, try parsing common patterns
            # This handles cases like "01-Jan-2023", "Jan 1, 2023", etc.
            date_patterns = [
                r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})',  # DD/MM/YYYY or DD-MM-YYYY
                r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2})'   # DD/MM/YY or DD-MM-YY
            ]

            for pattern in date_patterns:
                match = re.search(pattern, date_value)
                if match:
                    try:
                        day, month, year = match.groups()
                        if len(year) == 2:
                            year = f"20{year}"  # Assume 21st century
                        return datetime(int(year), int(month), int(day))
                    except ValueError:
                        continue

        return None

    def _parse_float(self, value: any) -> Optional[float]:
        """
        Parse value to float
        """
        if value is None:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove non-numeric characters except decimal point and minus sign
            clean_value = re.sub(r'[^\d.-]', '', value)
            try:
                return float(clean_value)
            except ValueError:
                return None

        return None

    def _normalize_fuel_type(self, fuel_type: str) -> str:
        """
        Normalize fuel type to standard values
        """
        if not fuel_type:
            return ''

        fuel_lower = fuel_type.lower().strip()

        # Map various representations to standard types
        if any(word in fuel_lower for word in ['petrol', 'gasoline', 'benzin', 'benzene', 'premium']):
            return 'Petrol'
        elif any(word in fuel_lower for word in ['diesel', 'dizel', 'petrodiesel', 'high speed diesel']):
            return 'Diesel'
        elif any(word in fuel_lower for word in ['cng', 'compressed natural gas', 'natural gas']):
            return 'CNG'
        elif any(word in fuel_lower for word in ['kerosene', 'paraffin', 'coal oil']):
            return 'Kerosene'
        else:
            # Return the original value if it doesn't match known types
            return fuel_type.title()

    def _calculate_liters_from_readings(self, opening: Optional[float], closing: Optional[float]) -> Optional[float]:
        """
        Calculate liters sold from opening and closing readings
        """
        if opening is None or closing is None:
            return None

        if closing >= opening:
            return round(closing - opening, 2)
        else:
            # Handle meter rollover (simplified - assumes 6-digit meter that rolls over at 999999)
            return round(closing + (1000000 - opening), 2)

    def _calculate_amount_from_rate(self, liters: Optional[float], rate: Optional[float]) -> Optional[float]:
        """
        Calculate total amount from liters sold and rate per liter
        """
        if liters is None or rate is None:
            return None

        return round(liters * rate, 2)

    def _calculate_row_confidence(self, row_data: Dict[str, any]) -> float:
        """
        Calculate overall confidence for a row based on individual field confidences
        """
        if not row_data:
            return 0.0

        confidences = []
        for result_obj in row_data.values():
            if isinstance(result_obj, dict) and 'result' in result_obj:
                confidence = result_obj['result'].confidence
            else:
                confidence = result_obj.confidence
            confidences.append(confidence)

        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            return min(avg_confidence, 1.0)  # Cap at 1.0
        else:
            return 0.0

    def validate_extracted_entries(self, entries: List[SalesEntry]) -> Dict[str, any]:
        """
        Validate extracted sales entries for consistency and completeness
        """
        validation_results = {
            'valid_entries': 0,
            'invalid_entries': 0,
            'total_entries': len(entries),
            'errors': [],
            'warnings': []
        }

        for i, entry in enumerate(entries):
            entry_errors = []
            entry_warnings = []

            # Validate required fields
            if not entry.fuel_type or entry.fuel_type.strip() == '':
                entry_errors.append(f"Missing fuel type at entry {i}")

            if entry.liters_sold is None or entry.liters_sold <= 0:
                entry_warnings.append(f"Invalid liters sold value at entry {i}")

            if entry.rate_per_liter is None or entry.rate_per_liter <= 0:
                entry_warnings.append(f"Invalid rate per liter value at entry {i}")

            if entry.total_amount is None or entry.total_amount <= 0:
                entry_warnings.append(f"Invalid total amount value at entry {i}")

            # Validate numeric relationships
            if entry.liters_sold and entry.rate_per_liter and entry.total_amount:
                calculated_amount = round(entry.liters_sold * entry.rate_per_liter, 2)
                if abs(calculated_amount - entry.total_amount) > 0.01:  # Allow small rounding differences
                    entry_warnings.append(f"Amount calculation mismatch at entry {i}")

            if entry_errors:
                validation_results['invalid_entries'] += 1
                validation_results['errors'].extend(entry_errors)
            else:
                validation_results['valid_entries'] += 1

            if entry_warnings:
                validation_results['warnings'].extend(entry_warnings)

        return validation_results

    def extract_entries_with_validation(self, processed_data: Dict[str, any], column_mappings: Dict[str, str]) -> Dict[str, any]:
        """
        Extract sales entries with validation
        :return: Dictionary containing entries and validation results
        """
        entries = self.extract_sales_entries(processed_data, column_mappings)
        validation_results = self.validate_extracted_entries(entries)

        return {
            'sales_entries': entries,
            'validation_results': validation_results,
            'needs_review_count': len([e for e in entries if e.ocr_confidence < 0.85])  # Threshold configurable
        }

    def get_entries_requiring_review(self, entries: List[SalesEntry], confidence_threshold: float = 0.85) -> List[SalesEntry]:
        """
        Get entries that require manual review based on confidence threshold
        """
        return [entry for entry in entries if entry.ocr_confidence is not None and entry.ocr_confidence < confidence_threshold]

    def create_sales_entry_from_dict(self, entry_dict: Dict[str, any]) -> SalesEntry:
        """
        Create a SalesEntry object from a dictionary
        """
        # Map dictionary keys to SalesEntry attributes
        mapped_dict = {}

        field_mapping = {
            'date': 'date',
            'nozzle_id': 'nozzle_id',
            'fuel_type': 'fuel_type',
            'opening_reading': 'opening_reading',
            'closing_reading': 'closing_reading',
            'liters_sold': 'liters_sold',
            'rate_per_liter': 'rate_per_liter',
            'total_amount': 'total_amount',
            'ocr_confidence': 'ocr_confidence',
            'is_manual_correction': 'is_manual_correction',
            'manual_correction_notes': 'manual_correction_notes'
        }

        for key, value in entry_dict.items():
            if key in field_mapping:
                mapped_dict[field_mapping[key]] = value

        return SalesEntry(**mapped_dict)