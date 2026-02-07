from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from typing import Dict, List, Any
import io
import os
from datetime import datetime


class PDFGeneratorService:
    """
    Service for generating PDF reports from ledger data
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.styles.add(ParagraphStyle(name='CustomHeading1', fontSize=18, spaceAfter=30, alignment=1))  # Center aligned
        self.styles.add(ParagraphStyle(name='CustomHeading2', fontSize=14, spaceAfter=20, spaceBefore=15))
        self.styles.add(ParagraphStyle(name='CustomNormal', fontSize=10, spaceAfter=6))

    def generate_daily_report_pdf(self, report_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a daily sales report in PDF format
        :param report_data: Dictionary containing report data
        :param output_path: Path to save the PDF file
        :return: Path to the generated PDF file
        """
        if not output_path:
            # Generate filename based on user and date
            user_id = report_data.get('user_id', 'unknown')
            report_date = report_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            output_path = f"daily_report_{user_id}_{report_date}.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Title
        title = Paragraph(f"Daily Sales Report - {report_date}", self.styles['CustomHeading1'])
        elements.append(title)

        # User Information
        if 'user_name' in report_data:
            user_para = Paragraph(f"Manager: {report_data['user_name']}", self.styles['CustomNormal'])
            elements.append(user_para)

        if 'pump_name' in report_data:
            pump_para = Paragraph(f"Petrol Pump: {report_data['pump_name']}", self.styles['CustomNormal'])
            elements.append(pump_para)

        # Add spacer
        elements.append(Spacer(1, 20))

        # Summary Table
        summary_data = [
            ['Fuel Type', 'Liters Sold', 'Revenue (₨)'],
            ['Petrol', f"{report_data.get('total_liters_petrol', 0):.2f}", f"₨{report_data.get('total_revenue_petrol', 0):,.2f}"],
            ['Diesel', f"{report_data.get('total_liters_diesel', 0):.2f}", f"₨{report_data.get('total_revenue_diesel', 0):,.2f}"],
            ['CNG', f"{report_data.get('total_liters_cng', 0):.2f}", f"₨{report_data.get('total_revenue_cng', 0):,.2f}"],
            ['<b>Total</b>', f"<b>{report_data.get('grand_total_liters', 0):.2f}</b>", f"<b>₨{report_data.get('grand_total_revenue', 0):,.2f}</b>"]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Right-align numbers
        ]))
        elements.append(summary_table)

        # Add spacer
        elements.append(Spacer(1, 20))

        # Detailed Sales Entries Table (if provided)
        if 'sales_entries' in report_data and report_data['sales_entries']:
            elements.append(Paragraph("Detailed Sales Entries", self.styles['CustomHeading2']))

            # Prepare table headers
            if report_data['sales_entries']:
                # Get column names from first entry (excluding id fields)
                first_entry = report_data['sales_entries'][0]
                headers = [key.title() for key in first_entry.keys() if key not in ['id', 'ledger_page_id']]

                # Create table data
                table_data = [headers]
                for entry in report_data['sales_entries']:
                    row = []
                    for key in first_entry.keys():
                        if key not in ['id', 'ledger_page_id']:
                            value = entry.get(key, '')
                            if isinstance(value, float):
                                if 'liter' in key.lower() or 'amount' in key.lower() or 'rate' in key.lower():
                                    value = f"{value:.2f}"
                            row.append(str(value))
                    table_data.append(row)

                detail_table = Table(table_data)
                detail_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.steelblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # Left-align text, numbers will be handled separately
                ]))
                elements.append(detail_table)

        # Build the PDF
        doc.build(elements)
        return output_path

    def generate_monthly_report_pdf(self, report_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a monthly sales report in PDF format
        :param report_data: Dictionary containing monthly report data
        :param output_path: Path to save the PDF file
        :return: Path to the generated PDF file
        """
        if not output_path:
            # Generate filename based on user and month
            user_id = report_data.get('user_id', 'unknown')
            month_year = report_data.get('month_year', datetime.now().strftime('%Y-%m'))
            output_path = f"monthly_report_{user_id}_{month_year}.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Title
        title = Paragraph(f"Monthly Sales Report - {month_year}", self.styles['CustomHeading1'])
        elements.append(title)

        # User Information
        if 'user_name' in report_data:
            user_para = Paragraph(f"Manager: {report_data['user_name']}", self.styles['CustomNormal'])
            elements.append(user_para)

        if 'pump_name' in report_data:
            pump_para = Paragraph(f"Petrol Pump: {report_data['pump_name']}", self.styles['CustomNormal'])
            elements.append(pump_para)

        # Add spacer
        elements.append(Spacer(1, 20))

        # Monthly Summary Table
        summary_data = [
            ['Metric', 'Value'],
            ['Total Operational Days', str(report_data.get('total_operational_days', 0))],
            ['Total Daily Reports', str(report_data.get('total_daily_reports', 0))],
            ['Avg. Daily Liters', f"{report_data.get('avg_daily_liters', 0):.2f}"],
            ['Avg. Daily Revenue', f"₨{report_data.get('avg_daily_revenue', 0):,.2f}"],
            ['Peak Sales Day', str(report_data.get('peak_sales_day', 'N/A'))],
            ['Peak Sales Amount', f"₨{report_data.get('peak_sales_amount', 0):,.2f}"]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Right-align numbers
        ]))
        elements.append(summary_table)

        # Add spacer
        elements.append(Spacer(1, 20))

        # Fuel Type Breakdown Table
        fuel_breakdown_data = [
            ['Fuel Type', 'Total Liters', 'Total Revenue'],
            ['Petrol', f"{report_data.get('total_liters_petrol', 0):.2f}", f"₨{report_data.get('total_revenue_petrol', 0):,.2f}"],
            ['Diesel', f"{report_data.get('total_liters_diesel', 0):.2f}", f"₨{report_data.get('total_revenue_diesel', 0):,.2f}"],
            ['CNG', f"{report_data.get('total_liters_cng', 0):.2f}", f"₨{report_data.get('total_revenue_cng', 0):,.2f}"],
            ['<b>Grand Total</b>', f"<b>{report_data.get('total_liters_petrol', 0) + report_data.get('total_liters_diesel', 0) + report_data.get('total_liters_cng', 0):.2f}</b>", f"<b>₨{report_data.get('total_revenue_petrol', 0) + report_data.get('total_revenue_diesel', 0) + report_data.get('total_revenue_cng', 0):,.2f}</b>"]
        ]

        fuel_table = Table(fuel_breakdown_data)
        fuel_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),  # Right-align numbers
        ]))
        elements.append(fuel_table)

        # Build the PDF
        doc.build(elements)
        return output_path

    def generate_ledger_verification_pdf(self, verification_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Generate a PDF for ledger verification showing extracted data vs manual input
        :param verification_data: Dictionary containing verification data
        :param output_path: Path to save the PDF file
        :return: Path to the generated PDF file
        """
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"ledger_verification_{timestamp}.pdf"

        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Title
        title = Paragraph("Ledger Verification Report", self.styles['CustomHeading1'])
        elements.append(title)

        # Verification Info
        elements.append(Paragraph(f"Verification Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['CustomNormal']))
        if 'original_image_path' in verification_data:
            elements.append(Paragraph(f"Original Image: {verification_data['original_image_path']}", self.styles['CustomNormal']))

        # Add spacer
        elements.append(Spacer(1, 20))

        # Verification Summary
        summary_data = [
            ['Verification Metric', 'Count'],
            ['Total Entries Extracted', str(verification_data.get('total_entries_extracted', 0))],
            ['High Confidence Entries', str(verification_data.get('high_confidence_entries', 0))],
            ['Low Confidence Entries', str(verification_data.get('low_confidence_entries', 0))],
            ['Manually Verified Entries', str(verification_data.get('manually_verified_entries', 0))],
            ['Auto-Verified Entries', str(verification_data.get('auto_verified_entries', 0))]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ]))
        elements.append(summary_table)

        # Build the PDF
        doc.build(elements)
        return output_path

    def create_urdu_support_pdf(self, report_data: Dict[str, Any], output_path: str = None, is_urdu: bool = False) -> str:
        """
        Create a PDF with optional Urdu language support
        :param report_data: Dictionary containing report data
        :param output_path: Path to save the PDF file
        :param is_urdu: Whether to generate Urdu version
        :return: Path to the generated PDF file
        """
        if is_urdu:
            # For Urdu support, we would typically use reportlab with custom fonts
            # This is a simplified version - in practice, you'd need to handle RTL text and Urdu fonts
            return self._generate_urdu_pdf(report_data, output_path)
        else:
            # Generate standard English PDF
            return self.generate_daily_report_pdf(report_data, output_path)

    def _generate_urdu_pdf(self, report_data: Dict[str, Any], output_path: str = None) -> str:
        """
        Internal method to generate Urdu PDF (simplified version)
        """
        if not output_path:
            user_id = report_data.get('user_id', 'unknown')
            report_date = report_data.get('report_date', datetime.now().strftime('%Y-%m-%d'))
            output_path = f"daily_report_urdu_{user_id}_{report_date}.pdf"

        # Create the PDF document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []

        # Title in English (Urdu would require special font handling)
        title = Paragraph(f"روزانہ فروخت کی رپورٹ - {report_data.get('report_date', '')}", self.styles['CustomHeading1'])
        elements.append(title)

        # For a real Urdu implementation, you'd need to use a library like xhtml2pdf with proper font support
        # or use reportlab with custom Urdu fonts
        # This is a placeholder implementation

        # Summary Table
        summary_data = [
            [' fuel type ', ' liters sold ', ' revenue (₨)'],
            ['petrol', f"{report_data.get('total_liters_petrol', 0):.2f}", f"₨{report_data.get('total_revenue_petrol', 0):,.2f}"],
            ['diesel', f"{report_data.get('total_liters_diesel', 0):.2f}", f"₨{report_data.get('total_revenue_diesel', 0):,.2f}"],
            ['cng', f"{report_data.get('total_liters_cng', 0):.2f}", f"₨{report_data.get('total_revenue_cng', 0):,.2f}"],
            ['<b>کل</b>', f"<b>{report_data.get('grand_total_liters', 0):.2f}</b>", f"<b>₨{report_data.get('grand_total_revenue', 0):,.2f}</b>"]
        ]

        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ]))
        elements.append(summary_table)

        # Build the PDF
        doc.build(elements)
        return output_path