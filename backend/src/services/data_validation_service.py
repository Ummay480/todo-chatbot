from typing import Dict, List, Any, Optional
from datetime import datetime, date
from ..models.SalesEntry import SalesEntry
from ..models.LedgerPage import LedgerPage


class DataValidationService:
    """
    Service for validating extracted ledger data for accuracy and completeness
    """

    def __init__(self):
        pass

    def validate_sales_entry(self, entry: SalesEntry) -> Dict[str, Any]:
        """
        Validate a single sales entry
        :param entry: SalesEntry object to validate
        :return: Dictionary containing validation results
        """
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'field_validations': {}
        }

        # Validate required fields
        if not entry.fuel_type or entry.fuel_type.strip() == '':
            validation_results['is_valid'] = False
            validation_results['errors'].append('Fuel type is required')

        if entry.liters_sold is None:
            validation_results['is_valid'] = False
            validation_results['errors'].append('Liters sold is required')
        elif entry.liters_sold < 0:
            validation_results['is_valid'] = False
            validation_results['errors'].append('Liters sold cannot be negative')

        if entry.total_amount is None:
            validation_results['is_valid'] = False
            validation_results['errors'].append('Total amount is required')
        elif entry.total_amount < 0:
            validation_results['is_valid'] = False
            validation_results['errors'].append('Total amount cannot be negative')

        # Validate date if provided
        if entry.date:
            date_validation = self._validate_date(entry.date)
            if not date_validation['is_valid']:
                validation_results['errors'].extend(date_validation['errors'])
                validation_results['is_valid'] = False

        # Validate numeric relationships
        if entry.liters_sold is not None and entry.rate_per_liter is not None and entry.total_amount is not None:
            calculated_amount = round(entry.liters_sold * entry.rate_per_liter, 2)
            if abs(calculated_amount - entry.total_amount) > 0.01:  # Allow small rounding differences
                validation_results['warnings'].append(
                    f'Amount calculation mismatch: calculated {calculated_amount}, recorded {entry.total_amount}'
                )

        # Validate fuel type
        fuel_validation = self._validate_fuel_type(entry.fuel_type)
        if not fuel_validation['is_valid']:
            validation_results['warnings'].extend(fuel_validation['warnings'])

        # Validate nozzle ID
        if entry.nozzle_id:
            nozzle_validation = self._validate_nozzle_id(entry.nozzle_id)
            if not nozzle_validation['is_valid']:
                validation_results['warnings'].extend(nozzle_validation['warnings'])

        # Store field-level validations
        validation_results['field_validations'] = {
            'date': self._validate_date(entry.date),
            'fuel_type': self._validate_fuel_type(entry.fuel_type),
            'liters_sold': self._validate_liters_sold(entry.liters_sold),
            'rate_per_liter': self._validate_rate_per_liter(entry.rate_per_liter),
            'total_amount': self._validate_total_amount(entry.total_amount),
            'nozzle_id': self._validate_nozzle_id(entry.nozzle_id),
            'opening_reading': self._validate_meter_reading(entry.opening_reading),
            'closing_reading': self._validate_meter_reading(entry.closing_reading)
        }

        return validation_results

    def validate_sales_entries_batch(self, entries: List[SalesEntry]) -> Dict[str, Any]:
        """
        Validate a batch of sales entries
        :param entries: List of SalesEntry objects to validate
        :return: Dictionary containing validation results for the batch
        """
        batch_results = {
            'total_entries': len(entries),
            'valid_entries': 0,
            'invalid_entries': 0,
            'entries_with_warnings': 0,
            'global_errors': [],
            'global_warnings': [],
            'entry_validations': []
        }

        for entry in entries:
            validation_result = self.validate_sales_entry(entry)
            batch_results['entry_validations'].append({
                'entry_id': entry.id,
                'validation_result': validation_result
            })

            if validation_result['is_valid']:
                batch_results['valid_entries'] += 1
            else:
                batch_results['invalid_entries'] += 1

            if validation_result['warnings']:
                batch_results['entries_with_warnings'] += 1

            # Collect global issues
            batch_results['global_errors'].extend(validation_result['errors'])
            batch_results['global_warnings'].extend(validation_result['warnings'])

        return batch_results

    def validate_ledger_page_data(self, ledger_page: LedgerPage, sales_entries: List[SalesEntry]) -> Dict[str, Any]:
        """
        Validate all data associated with a ledger page
        :param ledger_page: LedgerPage object to validate
        :param sales_entries: List of SalesEntry objects for this ledger page
        :return: Dictionary containing validation results for the ledger page
        """
        page_validation = {
            'ledger_page_valid': True,
            'sales_entries_valid': True,
            'overall_valid': True,
            'ledger_page_errors': [],
            'sales_entries_errors': [],
            'consistency_issues': [],
            'recommendations': []
        }

        # Validate the ledger page itself
        if not ledger_page.original_image_url:
            page_validation['ledger_page_valid'] = False
            page_validation['overall_valid'] = False
            page_validation['ledger_page_errors'].append('Original image URL is required')

        if ledger_page.processing_status not in ['pending', 'processing', 'completed', 'failed']:
            page_validation['ledger_page_valid'] = False
            page_validation['overall_valid'] = False
            page_validation['ledger_page_errors'].append('Invalid processing status')

        # Validate all sales entries
        entries_validation = self.validate_sales_entries_batch(sales_entries)
        page_validation['sales_entries_valid'] = entries_validation['invalid_entries'] == 0
        if not page_validation['sales_entries_valid']:
            page_validation['overall_valid'] = False

        # Check for consistency between ledger page and sales entries
        for entry in sales_entries:
            if entry.ledger_page_id != ledger_page.id:
                page_validation['consistency_issues'].append(
                    f'Sales entry {entry.id} does not belong to ledger page {ledger_page.id}'
                )

        # Check for temporal consistency (if dates are available)
        if sales_entries:
            dates = [entry.date for entry in sales_entries if entry.date]
            if dates:
                # Check if all entries have the same date as the ledger upload date
                upload_date = ledger_page.upload_date.date() if ledger_page.upload_date else None
                if upload_date:
                    for entry_date in dates:
                        if isinstance(entry_date, datetime):
                            entry_date = entry_date.date()
                        if entry_date != upload_date:
                            page_validation['consistency_issues'].append(
                                f'Entry date {entry_date} differs from upload date {upload_date}'
                            )

        # Generate recommendations
        if not page_validation['ledger_page_valid']:
            page_validation['recommendations'].append('Fix ledger page data issues before processing')
        if not page_validation['sales_entries_valid']:
            page_validation['recommendations'].append(
                f'Review and correct {entries_validation["invalid_entries"]} invalid entries'
            )
        if page_validation['consistency_issues']:
            page_validation['recommendations'].append(
                f'Address {len(page_validation["consistency_issues"])} consistency issues'
            )

        return page_validation

    def _validate_date(self, date_value: Any) -> Dict[str, Any]:
        """
        Validate date field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if date_value is None:
            result['warnings'].append('Date is missing')
            return result

        try:
            if isinstance(date_value, str):
                # Try to parse common date formats
                from datetime import datetime
                formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y']

                parsed = False
                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(date_value, fmt).date()
                        parsed = True
                        break
                    except ValueError:
                        continue

                if not parsed:
                    result['is_valid'] = False
                    result['errors'].append(f'Invalid date format: {date_value}')
                    return result

            elif isinstance(date_value, datetime):
                parsed_date = date_value.date()
            elif isinstance(date_value, date):
                parsed_date = date_value
            else:
                result['is_valid'] = False
                result['errors'].append(f'Invalid date type: {type(date_value)}')
                return result

            # Check if date is reasonable (not too far in the past/future)
            today = datetime.today().date()
            if parsed_date > today:
                result['warnings'].append(f'Date {parsed_date} is in the future')

            # Check if date is not too far in the past (more than 2 years)
            from datetime import timedelta
            if parsed_date < (today - timedelta(days=730)):  # ~2 years
                result['warnings'].append(f'Date {parsed_date} is more than 2 years ago')

        except Exception as e:
            result['is_valid'] = False
            result['errors'].append(f'Error validating date: {str(e)}')

        return result

    def _validate_fuel_type(self, fuel_type: str) -> Dict[str, Any]:
        """
        Validate fuel type field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if not fuel_type:
            result['warnings'].append('Fuel type is missing')
            return result

        # Common fuel types in Pakistan
        valid_fuel_types = [
            'petrol', 'diesel', 'cng', 'kerosene', 'gasoline',
            'high speed diesel', 'automotive diesel', 'premium gasoline'
        ]

        if fuel_type.lower().strip() not in [f.lower() for f in valid_fuel_types]:
            result['warnings'].append(f'Unusual fuel type: {fuel_type}. Expected one of: {", ".join(valid_fuel_types)}')

        return result

    def _validate_liters_sold(self, liters_sold: Optional[float]) -> Dict[str, Any]:
        """
        Validate liters sold field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if liters_sold is None:
            result['errors'].append('Liters sold is required')
            result['is_valid'] = False
            return result

        if liters_sold < 0:
            result['errors'].append('Liters sold cannot be negative')
            result['is_valid'] = False
        elif liters_sold == 0:
            result['warnings'].append('Liters sold is zero')
        elif liters_sold > 10000:  # Unusually high for a single transaction
            result['warnings'].append(f'Unusually high liters sold: {liters_sold}')

        return result

    def _validate_rate_per_liter(self, rate_per_liter: Optional[float]) -> Dict[str, Any]:
        """
        Validate rate per liter field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if rate_per_liter is None:
            return result  # Rate is optional

        if rate_per_liter < 0:
            result['errors'].append('Rate per liter cannot be negative')
            result['is_valid'] = False
        elif rate_per_liter == 0:
            result['warnings'].append('Rate per liter is zero')
        elif rate_per_liter < 50 or rate_per_liter > 250:  # Unusual rates in Pakistan
            result['warnings'].append(f'Unusual rate per liter: {rate_per_liter}. Expected 50-250 PKR')

        return result

    def _validate_total_amount(self, total_amount: Optional[float]) -> Dict[str, Any]:
        """
        Validate total amount field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if total_amount is None:
            result['errors'].append('Total amount is required')
            result['is_valid'] = False
            return result

        if total_amount < 0:
            result['errors'].append('Total amount cannot be negative')
            result['is_valid'] = False
        elif total_amount == 0:
            result['warnings'].append('Total amount is zero')
        elif total_amount > 100000:  # Unusually high for a single transaction
            result['warnings'].append(f'Unusually high total amount: {total_amount}')

        return result

    def _validate_nozzle_id(self, nozzle_id: Optional[str]) -> Dict[str, Any]:
        """
        Validate nozzle ID field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if not nozzle_id:
            result['warnings'].append('Nozzle ID is missing')
            return result

        # Basic validation: should not be just numbers or just letters
        if nozzle_id.isdigit():
            result['warnings'].append(f'Nozzle ID "{nozzle_id}" appears to be only numbers')
        elif nozzle_id.isalpha():
            result['warnings'].append(f'Nozzle ID "{nozzle_id}" appears to be only letters')

        # Length check
        if len(nozzle_id) > 20:
            result['warnings'].append(f'Nozzle ID "{nozzle_id}" is unusually long')

        return result

    def _validate_meter_reading(self, reading: Optional[float]) -> Dict[str, Any]:
        """
        Validate meter reading field
        """
        result = {'is_valid': True, 'errors': [], 'warnings': []}

        if reading is None:
            return result  # Meter readings are optional

        if reading < 0:
            result['errors'].append('Meter reading cannot be negative')
            result['is_valid'] = False
        elif reading > 999999:  # Standard meters usually have 6 digits
            result['warnings'].append(f'Unusually high meter reading: {reading}')

        return result

    def validate_business_rules(self, sales_entries: List[SalesEntry]) -> Dict[str, Any]:
        """
        Validate business rules for the sales entries
        """
        rules_validation = {
            'passed': True,
            'violations': [],
            'rule_results': {}
        }

        # Rule: Total liters should be positive
        total_liters = sum(entry.liters_sold or 0 for entry in sales_entries)
        if total_liters <= 0:
            rules_validation['violations'].append('Total liters sold should be positive')
            rules_validation['passed'] = False

        # Rule: Total revenue should be positive
        total_revenue = sum(entry.total_amount or 0 for entry in sales_entries)
        if total_revenue <= 0:
            rules_validation['violations'].append('Total revenue should be positive')
            rules_validation['passed'] = False

        # Rule: Nozzle IDs should be consistent within a day
        nozzle_ids = [entry.nozzle_id for entry in sales_entries if entry.nozzle_id]
        if len(set(nozzle_ids)) > 20:  # Unusually high number of nozzles
            rules_validation['violations'].append(f'Unusually high number of nozzles: {len(set(nozzle_ids))}')

        # Rule: Check for duplicate entries (same nozzle, fuel type, and similar amounts)
        entries_map = {}
        for i, entry in enumerate(sales_entries):
            key = (entry.nozzle_id, entry.fuel_type, entry.liters_sold)
            if key in entries_map:
                rules_validation['violations'].append(f'Potential duplicate entry detected at positions {entries_map[key]} and {i}')
            else:
                entries_map[key] = i

        return rules_validation

    def generate_validation_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Generate a human-readable validation report
        """
        report_lines = ["LEDGER DATA VALIDATION REPORT", "=" * 30]

        if 'overall_valid' in validation_results:
            report_lines.append(f"Overall Valid: {'YES' if validation_results['overall_valid'] else 'NO'}")

        if 'total_entries' in validation_results:
            report_lines.append(f"Total Entries: {validation_results['total_entries']}")
            report_lines.append(f"Valid Entries: {validation_results['valid_entries']}")
            report_lines.append(f"Invalid Entries: {validation_results['invalid_entries']}")
            report_lines.append(f"Entries with Warnings: {validation_results['entries_with_warnings']}")

        if validation_results.get('global_errors'):
            report_lines.append("\nERRORS:")
            for error in validation_results['global_errors']:
                report_lines.append(f"  - {error}")

        if validation_results.get('global_warnings'):
            report_lines.append("\nWARNINGS:")
            for warning in validation_results['global_warnings']:
                report_lines.append(f"  - {warning}")

        if validation_results.get('consistency_issues'):
            report_lines.append("\nCONSISTENCY ISSUES:")
            for issue in validation_results['consistency_issues']:
                report_lines.append(f"  - {issue}")

        if validation_results.get('violations'):
            report_lines.append("\nBUSINESS RULE VIOLATIONS:")
            for violation in validation_results['violations']:
                report_lines.append(f"  - {violation}")

        return "\n".join(report_lines)