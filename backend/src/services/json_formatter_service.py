import json
from typing import Dict, List, Any, Union
from datetime import datetime, date
from decimal import Decimal
import os


class DateTimeEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle datetime and other non-serializable objects
    """
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super().default(obj)


class JSONFormatterService:
    """
    Service for formatting data as JSON for API responses and data export
    """

    def __init__(self):
        pass

    def format_daily_report_json(self, report_data: Dict[str, Any]) -> str:
        """
        Format daily report data as JSON string
        :param report_data: Dictionary containing daily report data
        :return: JSON string representation of the report
        """
        formatted_data = {
            "report_type": "daily_sales",
            "report_date": report_data.get('report_date'),
            "user_id": report_data.get('user_id'),
            "user_name": report_data.get('user_name'),
            "pump_name": report_data.get('pump_name'),
            "summary": {
                "total_liters_petrol": report_data.get('total_liters_petrol', 0),
                "total_liters_diesel": report_data.get('total_liters_diesel', 0),
                "total_liters_cng": report_data.get('total_liters_cng', 0),
                "total_revenue_petrol": report_data.get('total_revenue_petrol', 0),
                "total_revenue_diesel": report_data.get('total_revenue_diesel', 0),
                "total_revenue_cng": report_data.get('total_revenue_cng', 0),
                "grand_total_liters": report_data.get('grand_total_liters', 0),
                "grand_total_revenue": report_data.get('grand_total_revenue', 0),
                "total_sales_entries": report_data.get('total_sales_entries', 0)
            },
            "detailed_entries": report_data.get('sales_entries', []),
            "generated_at": datetime.now().isoformat(),
            "export_format": "json"
        }

        return json.dumps(formatted_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def format_monthly_report_json(self, report_data: Dict[str, Any]) -> str:
        """
        Format monthly report data as JSON string
        :param report_data: Dictionary containing monthly report data
        :return: JSON string representation of the report
        """
        formatted_data = {
            "report_type": "monthly_sales",
            "month_year": report_data.get('month_year'),
            "user_id": report_data.get('user_id'),
            "user_name": report_data.get('user_name'),
            "pump_name": report_data.get('pump_name'),
            "summary": {
                "total_liters_petrol": report_data.get('total_liters_petrol', 0),
                "total_liters_diesel": report_data.get('total_liters_diesel', 0),
                "total_liters_cng": report_data.get('total_liters_cng', 0),
                "total_revenue_petrol": report_data.get('total_revenue_petrol', 0),
                "total_revenue_diesel": report_data.get('total_revenue_diesel', 0),
                "total_revenue_cng": report_data.get('total_revenue_cng', 0),
                "total_operational_days": report_data.get('total_operational_days', 0),
                "total_daily_reports": report_data.get('total_daily_reports', 0),
                "avg_daily_liters": report_data.get('avg_daily_liters', 0),
                "avg_daily_revenue": report_data.get('avg_daily_revenue', 0),
                "peak_sales_day": report_data.get('peak_sales_day'),
                "peak_sales_amount": report_data.get('peak_sales_amount', 0)
            },
            "generated_at": datetime.now().isoformat(),
            "export_format": "json"
        }

        return json.dumps(formatted_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def format_ledger_verification_json(self, verification_data: Dict[str, Any]) -> str:
        """
        Format ledger verification data as JSON string
        :param verification_data: Dictionary containing verification data
        :return: JSON string representation of the verification data
        """
        formatted_data = {
            "verification_type": "ledger_verification",
            "original_image_path": verification_data.get('original_image_path'),
            "verification_date": datetime.now().isoformat(),
            "summary": {
                "total_entries_extracted": verification_data.get('total_entries_extracted', 0),
                "high_confidence_entries": verification_data.get('high_confidence_entries', 0),
                "low_confidence_entries": verification_data.get('low_confidence_entries', 0),
                "manually_verified_entries": verification_data.get('manually_verified_entries', 0),
                "auto_verified_entries": verification_data.get('auto_verified_entries', 0),
                "overall_accuracy": verification_data.get('overall_accuracy', 0)
            },
            "detailed_verification": verification_data.get('detailed_verification', []),
            "confidence_threshold": verification_data.get('confidence_threshold', 85.0),
            "verification_status": verification_data.get('verification_status', 'pending')
        }

        return json.dumps(formatted_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def format_sales_entries_json(self, sales_entries: List[Dict[str, Any]]) -> str:
        """
        Format sales entries as JSON string
        :param sales_entries: List of sales entry dictionaries
        :return: JSON string representation of the sales entries
        """
        formatted_data = {
            "data_type": "sales_entries",
            "entry_count": len(sales_entries),
            "entries": sales_entries,
            "generated_at": datetime.now().isoformat()
        }

        return json.dumps(formatted_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def format_ledger_extraction_json(self, extraction_data: Dict[str, Any]) -> str:
        """
        Format ledger extraction results as JSON string
        :param extraction_data: Dictionary containing extraction results
        :return: JSON string representation of the extraction data
        """
        formatted_data = {
            "extraction_type": "ledger_extraction",
            "original_image": extraction_data.get('original_image'),
            "processing_status": extraction_data.get('processing_status', 'completed'),
            "processing_time": extraction_data.get('processing_time'),
            "detected_columns": extraction_data.get('detected_columns', []),
            "extracted_data": extraction_data.get('extracted_data', []),
            "ocr_confidence_avg": extraction_data.get('ocr_confidence_avg', 0),
            "confidence_distribution": extraction_data.get('confidence_distribution', {}),
            "validation_results": extraction_data.get('validation_results', {}),
            "post_processing_required": extraction_data.get('post_processing_required', False),
            "low_confidence_items": extraction_data.get('low_confidence_items', []),
            "manual_review_required": extraction_data.get('manual_review_required', False)
        }

        return json.dumps(formatted_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def format_api_response(self, data: Any, success: bool = True, message: str = "", error_code: str = None) -> str:
        """
        Format standardized API response as JSON
        :param data: Data to include in the response
        :param success: Whether the operation was successful
        :param message: Message to include in the response
        :param error_code: Error code if operation failed
        :return: JSON string representation of the API response
        """
        response = {
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "message": message
        }

        if not success and error_code:
            response["error_code"] = error_code

        return json.dumps(response, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def format_user_preferences_json(self, preferences_data: Dict[str, Any]) -> str:
        """
        Format user preferences as JSON string
        :param preferences_data: Dictionary containing user preferences
        :return: JSON string representation of user preferences
        """
        formatted_data = {
            "preferences_type": "user_preferences",
            "user_id": preferences_data.get('user_id'),
            "settings": {
                "language_preference": preferences_data.get('language_preference', 'en'),
                "report_layout": preferences_data.get('report_layout', 'standard'),
                "date_format": preferences_data.get('date_format', 'DD-MM-YYYY'),
                "unit_preference": preferences_data.get('unit_preference', 'liters'),
                "currency_symbol": preferences_data.get('currency_symbol', '₨'),
                "custom_column_order": preferences_data.get('custom_column_order', []),
                "enable_urdu_translation": preferences_data.get('enable_urdu_translation', True),
                "enable_email_notifications": preferences_data.get('enable_email_notifications', False),
                "enable_sms_notifications": preferences_data.get('enable_sms_notifications', False),
                "custom_report_templates": preferences_data.get('custom_report_templates', {})
            },
            "last_updated": preferences_data.get('updated_at'),
            "generated_at": datetime.now().isoformat()
        }

        return json.dumps(formatted_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def save_json_to_file(self, data: str, output_path: str) -> str:
        """
        Save JSON string to a file
        :param data: JSON string to save
        :param output_path: Path where the file should be saved
        :return: Path to the saved file
        """
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True) if os.path.dirname(output_path) else None

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(data)

        return output_path

    def format_for_urdu_localization(self, data: Dict[str, Any], is_urdu: bool = False) -> str:
        """
        Format data with optional Urdu localization
        :param data: Dictionary containing data to format
        :param is_urdu: Whether to format for Urdu localization
        :return: JSON string with appropriate localization
        """
        if is_urdu:
            # Add Urdu translations to the data
            localized_data = self._add_urdu_translations(data)
            return json.dumps(localized_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)
        else:
            # Return standard English formatting
            return json.dumps(data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)

    def _add_urdu_translations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add Urdu translations to data
        :param data: Original data dictionary
        :return: Data dictionary with Urdu translations
        """
        # This is a simplified approach - in practice, you'd have a more comprehensive translation system
        translated_data = data.copy()

        # Add a translations section if not present
        if 'translations' not in translated_data:
            translated_data['translations'] = {}

        # Add common translations
        translated_data['translations'].update({
            "daily_sales_report": "روزانہ فروخت کی رپورٹ",
            "monthly_sales_report": "ماہانہ فروخت کی رپورٹ",
            "petrol": "پیٹرول",
            "diesel": "ڈیزل",
            "cng": "CNG",
            "liters_sold": "لیٹر فروخت",
            "revenue": "آمدنی",
            "total": "کل",
            "fuel_type": " fuel type ",
            "date": "تاریخ",
            "nozzle_id": "نوزل ID",
            "opening_reading": "Opening Reading",
            "closing_reading": "Closing Reading",
            "liters_sold": "لیٹر فروخت",
            "rate_per_liter": "Rate Per Liter",
            "total_amount": "Total Amount"
        })

        return translated_data

    def validate_json_format(self, json_str: str) -> bool:
        """
        Validate if a string is valid JSON
        :param json_str: String to validate
        :return: True if valid JSON, False otherwise
        """
        try:
            json.loads(json_str)
            return True
        except json.JSONDecodeError:
            return False

    def merge_json_reports(self, reports: List[str]) -> str:
        """
        Merge multiple JSON reports into a single JSON structure
        :param reports: List of JSON strings representing reports
        :return: Single merged JSON string
        """
        merged_data = {
            "merged_report_type": "aggregated_reports",
            "report_count": len(reports),
            "reports": [],
            "generated_at": datetime.now().isoformat()
        }

        for report_str in reports:
            try:
                report_data = json.loads(report_str)
                merged_data["reports"].append(report_data)
            except json.JSONDecodeError:
                # Skip invalid JSON strings
                continue

        return json.dumps(merged_data, cls=DateTimeEncoder, indent=2, ensure_ascii=False)