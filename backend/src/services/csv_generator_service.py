import csv
import os
from typing import Dict, List, Any
from datetime import datetime
import io


class CSVGeneratorService:
    """
    Service for generating CSV reports from ledger data
    """

    def __init__(self):
        pass

    def generate_daily_report_csv(self, report_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a daily sales report in CSV format
        :param report_data: Dictionary containing report data
        :param output_path: Path to save the CSV file
        :return: Path to the generated CSV file
        """
        if not output_path:
            # Generate filename based on user and date
            user_id = report_data.get('user_id', 'unknown')
            report_date = report_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            output_path = f"daily_report_{user_id}_{report_date}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Daily Sales Report'])
            writer.writerow([])
            writer.writerow(['Field', 'Value'])
            writer.writerow(['Report Date', report_data.get('report_date', '')])
            writer.writerow(['User ID', report_data.get('user_id', '')])
            if 'user_name' in report_data:
                writer.writerow(['Manager', report_data['user_name']])
            if 'pump_name' in report_data:
                writer.writerow(['Petrol Pump', report_data['pump_name']])
            writer.writerow([])

            # Write summary data
            writer.writerow(['Fuel Type', 'Liters Sold', 'Revenue (₨)'])
            writer.writerow(['Petrol', f"{report_data.get('total_liters_petrol', 0):.2f}", f"{report_data.get('total_revenue_petrol', 0):.2f}"])
            writer.writerow(['Diesel', f"{report_data.get('total_liters_diesel', 0):.2f}", f"{report_data.get('total_revenue_diesel', 0):.2f}"])
            writer.writerow(['CNG', f"{report_data.get('total_liters_cng', 0):.2f}", f"{report_data.get('total_revenue_cng', 0):.2f}"])
            writer.writerow(['Total', f"{report_data.get('grand_total_liters', 0):.2f}", f"{report_data.get('grand_total_revenue', 0):.2f}"])
            writer.writerow([])

            # Write detailed sales entries if available
            if 'sales_entries' in report_data and report_data['sales_entries']:
                writer.writerow(['--- Detailed Sales Entries ---'])

                # Get all possible keys from sales entries to create header
                if report_data['sales_entries']:
                    first_entry = report_data['sales_entries'][0]
                    headers = [key.title() for key in first_entry.keys()]
                    writer.writerow(headers)

                    # Write each entry
                    for entry in report_data['sales_entries']:
                        row = []
                        for key in first_entry.keys():
                            value = entry.get(key, '')
                            if isinstance(value, (int, float)):
                                if 'liter' in key.lower() or 'amount' in key.lower() or 'rate' in key.lower():
                                    value = f"{value:.2f}"
                            row.append(str(value))
                        writer.writerow(row)

        return output_path

    def generate_monthly_report_csv(self, report_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a monthly sales report in CSV format
        :param report_data: Dictionary containing monthly report data
        :param output_path: Path to save the CSV file
        :return: Path to the generated CSV file
        """
        if not output_path:
            # Generate filename based on user and month
            user_id = report_data.get('user_id', 'unknown')
            month_year = report_data.get('month_year', datetime.now().strftime('%Y-%m'))
            output_path = f"monthly_report_{user_id}_{month_year}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Monthly Sales Report'])
            writer.writerow([])
            writer.writerow(['Field', 'Value'])
            writer.writerow(['Month-Year', report_data.get('month_year', '')])
            writer.writerow(['User ID', report_data.get('user_id', '')])
            if 'user_name' in report_data:
                writer.writerow(['Manager', report_data['user_name']])
            if 'pump_name' in report_data:
                writer.writerow(['Petrol Pump', report_data['pump_name']])
            writer.writerow([])

            # Write summary data
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Operational Days', report_data.get('total_operational_days', 0)])
            writer.writerow(['Total Daily Reports', report_data.get('total_daily_reports', 0)])
            writer.writerow(['Average Daily Liters', f"{report_data.get('avg_daily_liters', 0):.2f}"])
            writer.writerow(['Average Daily Revenue', f"{report_data.get('avg_daily_revenue', 0):.2f}"])
            writer.writerow(['Peak Sales Day', report_data.get('peak_sales_day', 'N/A')])
            writer.writerow(['Peak Sales Amount', f"{report_data.get('peak_sales_amount', 0):.2f}"])
            writer.writerow([])

            # Write fuel breakdown
            writer.writerow(['Fuel Type Breakdown'])
            writer.writerow(['Fuel Type', 'Total Liters', 'Total Revenue'])
            writer.writerow(['Petrol', f"{report_data.get('total_liters_petrol', 0):.2f}", f"{report_data.get('total_revenue_petrol', 0):.2f}"])
            writer.writerow(['Diesel', f"{report_data.get('total_liters_diesel', 0):.2f}", f"{report_data.get('total_revenue_diesel', 0):.2f}"])
            writer.writerow(['CNG', f"{report_data.get('total_liters_cng', 0):.2f}", f"{report_data.get('total_revenue_cng', 0):.2f}"])
            total_liters = report_data.get('total_liters_petrol', 0) + report_data.get('total_liters_diesel', 0) + report_data.get('total_liters_cng', 0)
            total_revenue = report_data.get('total_revenue_petrol', 0) + report_data.get('total_revenue_diesel', 0) + report_data.get('total_revenue_cng', 0)
            writer.writerow(['Total', f"{total_liters:.2f}", f"{total_revenue:.2f}"])

        return output_path

    def generate_sales_entries_csv(self, sales_entries: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Generate a CSV file with just the sales entries
        :param sales_entries: List of sales entry dictionaries
        :param output_path: Path to save the CSV file
        :return: Path to the generated CSV file
        """
        if not sales_entries:
            raise ValueError("No sales entries provided")

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"sales_entries_{timestamp}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Get all possible keys from sales entries to create header
            all_keys = set()
            for entry in sales_entries:
                all_keys.update(entry.keys())

            # Sort keys to ensure consistent column ordering
            headers = sorted([key.title() for key in all_keys])
            writer.writerow(headers)

            # Write each entry
            for entry in sales_entries:
                row = []
                for header in headers:
                    key = header.lower()
                    value = entry.get(key, '')
                    if isinstance(value, (int, float)):
                        # Format numeric values appropriately
                        if 'liter' in key or 'amount' in key or 'rate' in key or 'reading' in key:
                            value = f"{value:.2f}"
                    row.append(str(value))
                writer.writerow(row)

        return output_path

    def generate_ledger_verification_csv(self, verification_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a CSV for ledger verification showing extracted data vs manual input
        :param verification_data: Dictionary containing verification data
        :param output_path: Path to save the CSV file
        :return: Path to the generated CSV file
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"ledger_verification_{timestamp}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Ledger Verification Report'])
            writer.writerow([])
            writer.writerow(['Verification Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            if 'original_image_path' in verification_data:
                writer.writerow(['Original Image', verification_data['original_image_path']])
            writer.writerow([])

            # Write verification summary
            writer.writerow(['Verification Metrics'])
            writer.writerow(['Metric', 'Count'])
            writer.writerow(['Total Entries Extracted', verification_data.get('total_entries_extracted', 0)])
            writer.writerow(['High Confidence Entries', verification_data.get('high_confidence_entries', 0)])
            writer.writerow(['Low Confidence Entries', verification_data.get('low_confidence_entries', 0)])
            writer.writerow(['Manually Verified Entries', verification_data.get('manually_verified_entries', 0)])
            writer.writerow(['Auto-Verified Entries', verification_data.get('auto_verified_entries', 0)])
            writer.writerow([])

            # Write detailed verification data if available
            if 'detailed_verification' in verification_data:
                writer.writerow(['Detailed Verification Results'])
                writer.writerow(['Entry ID', 'Field', 'Extracted Value', 'Verified Value', 'Confidence', 'Status'])
                for detail in verification_data['detailed_verification']:
                    writer.writerow([
                        detail.get('entry_id', ''),
                        detail.get('field', ''),
                        detail.get('extracted_value', ''),
                        detail.get('verified_value', ''),
                        f"{detail.get('confidence', 0):.2f}" if detail.get('confidence') else '',
                        detail.get('status', '')
                    ])

        return output_path

    def create_urdu_csv(self, report_data: Dict[str, Any], output_path: str = None, is_urdu: bool = False) -> str:
        """
        Create a CSV with optional Urdu language support
        :param report_data: Dictionary containing report data
        :param output_path: Path to save the CSV file
        :param is_urdu: Whether to generate Urdu version
        :return: Path to the generated CSV file
        """
        if is_urdu:
            # For Urdu CSV, we simply translate the headers
            return self._generate_urdu_csv(report_data, output_path)
        else:
            # Generate standard English CSV
            return self.generate_daily_report_csv(report_data, output_path)

    def _generate_urdu_csv(self, report_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Internal method to generate Urdu CSV
        """
        if not output_path:
            user_id = report_data.get('user_id', 'unknown')
            report_date = report_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            output_path = f"daily_report_urdu_{user_id}_{report_date}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header in Urdu
            writer.writerow(['روزانہ فروخت کی رپورٹ'])
            writer.writerow([])
            writer.writerow(['میدان', 'قدر'])
            writer.writerow(['رپورٹ کی تاریخ', report_data.get('report_date', '')])
            writer.writerow(['صارف ID', report_data.get('user_id', '')])
            if 'user_name' in report_data:
                writer.writerow(['مینیجر', report_data['user_name']])
            if 'pump_name' in report_data:
                writer.writerow(['پیٹرول پمپ', report_data['pump_name']])
            writer.writerow([])

            # Write summary data in Urdu
            writer.writerow([' fuel type ', ' liters sold ', ' revenue (Rs)'])
            writer.writerow(['petrol', f"{report_data.get('total_liters_petrol', 0):.2f}", f"{report_data.get('total_revenue_petrol', 0):.2f}"])
            writer.writerow(['diesel', f"{report_data.get('total_liters_diesel', 0):.2f}", f"{report_data.get('total_revenue_diesel', 0):.2f}"])
            writer.writerow(['cng', f"{report_data.get('total_liters_cng', 0):.2f}", f"{report_data.get('total_revenue_cng', 0):.2f}"])
            writer.writerow(['کل', f"{report_data.get('grand_total_liters', 0):.2f}", f"{report_data.get('grand_total_revenue', 0):.2f}"])

        return output_path

    def export_multiple_reports_to_single_csv(self, reports_list: List[Dict[str, Any]], output_path: str = None) -> str:
        """
        Export multiple daily reports to a single CSV file
        :param reports_list: List of report dictionaries
        :param output_path: Path to save the CSV file
        :return: Path to the generated CSV file
        """
        if not reports_list:
            raise ValueError("No reports provided")

        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"combined_daily_reports_{timestamp}.csv"

        with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header
            writer.writerow(['Combined Daily Reports'])
            writer.writerow([])

            # Write combined data
            all_keys = set()
            for report in reports_list:
                all_keys.update(report.keys())

            # We'll create a flattened view focusing on key metrics
            headers = ['Report Date', 'Petrol Liters', 'Petrol Revenue', 'Diesel Liters', 'Diesel Revenue',
                      'CNG Liters', 'CNG Revenue', 'Grand Total Liters', 'Grand Total Revenue']
            writer.writerow(headers)

            for report in reports_list:
                row = [
                    report.get('report_date', ''),
                    f"{report.get('total_liters_petrol', 0):.2f}",
                    f"{report.get('total_revenue_petrol', 0):.2f}",
                    f"{report.get('total_liters_diesel', 0):.2f}",
                    f"{report.get('total_revenue_diesel', 0):.2f}",
                    f"{report.get('total_liters_cng', 0):.2f}",
                    f"{report.get('total_revenue_cng', 0):.2f}",
                    f"{report.get('grand_total_liters', 0):.2f}",
                    f"{report.get('grand_total_revenue', 0):.2f}"
                ]
                writer.writerow(row)

        return output_path