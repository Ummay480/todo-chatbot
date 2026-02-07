"""
Calculation Engine Service for Petrol Pump Ledger Automation

This module provides calculation functionality for ledger data
"""
from typing import Dict, List, Any, Optional
import re


class CalculationEngineService:
    """
    Service class for performing calculations on ledger data
    """

    def __init__(self):
        """
        Initialize the calculation engine service
        """
        pass

    def calculate_daily_totals(self, entries: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate daily totals from sales entries

        Args:
            entries: List of sales entries

        Returns:
            Dictionary containing calculated totals
        """
        totals = {
            'total_liters_petrol': 0.0,
            'total_liters_diesel': 0.0,
            'total_liters_cng': 0.0,
            'total_revenue_petrol': 0.0,
            'total_revenue_diesel': 0.0,
            'total_revenue_cng': 0.0,
            'grand_total_liters': 0.0,
            'grand_total_revenue': 0.0,
            'total_nozzles_count': 0,
            'total_sales_entries': len(entries)
        }

        # Set to track unique nozzles
        nozzles = set()

        for entry in entries:
            # Get fuel type and liters
            fuel_type = self.normalize_fuel_type(entry.get('fuel_type', ''))
            liters = self.parse_number(entry.get('liters_sold', 0))
            rate = self.parse_number(entry.get('rate_per_liter', 0))
            nozzle_id = entry.get('nozzle_id', '')

            # Add nozzle to set
            if nozzle_id:
                nozzles.add(nozzle_id)

            # Add to appropriate totals
            if fuel_type == 'petrol':
                totals['total_liters_petrol'] += liters
                totals['total_revenue_petrol'] += liters * rate
            elif fuel_type == 'diesel':
                totals['total_liters_diesel'] += liters
                totals['total_revenue_diesel'] += liters * rate
            elif fuel_type == 'cng':
                totals['total_liters_cng'] += liters
                totals['total_revenue_cng'] += liters * rate

            # Add to grand totals
            totals['grand_total_liters'] += liters
            totals['grand_total_revenue'] += liters * rate

        # Set nozzle count
        totals['total_nozzles_count'] = len(nozzles)

        return totals

    def calculate_monthly_totals(self, daily_totals: List[Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate monthly totals from daily totals

        Args:
            daily_totals: List of daily total dictionaries

        Returns:
            Dictionary containing calculated monthly totals
        """
        monthly_totals = {
            'total_liters_petrol': 0.0,
            'total_liters_diesel': 0.0,
            'total_liters_cng': 0.0,
            'total_revenue_petrol': 0.0,
            'total_revenue_diesel': 0.0,
            'total_revenue_cng': 0.0,
            'avg_daily_liters': 0.0,
            'avg_daily_revenue': 0.0,
            'peak_sales_day': None,
            'peak_sales_amount': 0.0,
            'total_operational_days': 0,
            'total_daily_reports': len(daily_totals),
            'trend_indicator': 'neutral'
        }

        if not daily_totals:
            return monthly_totals

        # Sum up all daily totals
        peak_sales = 0.0
        peak_day = None

        for daily in daily_totals:
            monthly_totals['total_liters_petrol'] += daily.get('total_liters_petrol', 0.0)
            monthly_totals['total_liters_diesel'] += daily.get('total_liters_diesel', 0.0)
            monthly_totals['total_liters_cng'] += daily.get('total_liters_cng', 0.0)
            monthly_totals['total_revenue_petrol'] += daily.get('total_revenue_petrol', 0.0)
            monthly_totals['total_revenue_diesel'] += daily.get('total_revenue_diesel', 0.0)
            monthly_totals['total_revenue_cng'] += daily.get('total_revenue_cng', 0.0)

            # Track peak sales day
            daily_revenue = daily.get('grand_total_revenue', 0.0)
            if daily_revenue > peak_sales:
                peak_sales = daily_revenue
                peak_day = daily.get('date', 'unknown')

        # Calculate averages
        if len(daily_totals) > 0:
            monthly_totals['avg_daily_liters'] = (
                monthly_totals['total_liters_petrol'] +
                monthly_totals['total_liters_diesel'] +
                monthly_totals['total_liters_cng']
            ) / len(daily_totals)

            monthly_totals['avg_daily_revenue'] = (
                monthly_totals['total_revenue_petrol'] +
                monthly_totals['total_revenue_diesel'] +
                monthly_totals['total_revenue_cng']
            ) / len(daily_totals)

        # Set peak sales information
        monthly_totals['peak_sales_day'] = peak_day
        monthly_totals['peak_sales_amount'] = peak_sales

        # Set operational days
        monthly_totals['total_operational_days'] = len(daily_totals)

        # Determine trend indicator (simplified)
        if len(daily_totals) >= 2:
            recent_avg = sum(dt.get('grand_total_revenue', 0) for dt in daily_totals[-7:]) / min(7, len(daily_totals))
            earlier_avg = sum(dt.get('grand_total_revenue', 0) for dt in daily_totals[:7]) / min(7, len(daily_totals))

            if recent_avg > earlier_avg * 1.05:
                monthly_totals['trend_indicator'] = 'up'
            elif recent_avg < earlier_avg * 0.95:
                monthly_totals['trend_indicator'] = 'down'
            else:
                monthly_totals['trend_indicator'] = 'neutral'

        return monthly_totals

    def calculate_discrepancies(self, handwritten_values: Dict[str, float], calculated_values: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate discrepancies between handwritten values and calculated values

        Args:
            handwritten_values: Values from the handwritten ledger
            calculated_values: Values calculated by the system

        Returns:
            Dictionary containing discrepancy information
        """
        discrepancies = {}

        for key in handwritten_values:
            if key in calculated_values:
                handwritten_val = handwritten_values[key]
                calculated_val = calculated_values[key]
                difference = abs(handwritten_val - calculated_val)
                percentage_diff = (difference / max(abs(handwritten_val), 0.001)) * 100

                discrepancies[f"{key}_discrepancy"] = {
                    'handwritten': handwritten_val,
                    'calculated': calculated_val,
                    'difference': difference,
                    'percentage_difference': percentage_diff
                }

        return discrepancies

    def validate_calculations(self, entries: List[Dict[str, Any]], expected_totals: Dict[str, float]) -> Dict[str, Any]:
        """
        Validate calculations against expected totals

        Args:
            entries: List of sales entries
            expected_totals: Expected total values from the ledger

        Returns:
            Dictionary containing validation results
        """
        calculated_totals = self.calculate_daily_totals(entries)
        validation_results = {
            'is_valid': True,
            'discrepancies': {},
            'confidence': 100.0  # Default confidence
        }

        # Compare calculated totals with expected totals
        for key, expected_val in expected_totals.items():
            if key in calculated_totals:
                calculated_val = calculated_totals[key]
                difference = abs(expected_val - calculated_val)

                # If difference is significant, mark as invalid
                if difference > expected_val * 0.05:  # 5% tolerance
                    validation_results['is_valid'] = False
                    validation_results['discrepancies'][key] = {
                        'expected': expected_val,
                        'calculated': calculated_val,
                        'difference': difference
                    }

        # Calculate overall confidence based on discrepancies
        if validation_results['discrepancies']:
            avg_diff_percentage = sum(
                abs(v['difference'] / max(abs(v['expected']), 0.001)) * 100
                for v in validation_results['discrepancies'].values()
            ) / len(validation_results['discrepancies'])
            validation_results['confidence'] = max(0, 100 - avg_diff_percentage)

        return validation_results

    def parse_number(self, value: Any) -> float:
        """
        Parse a value as a number, handling various formats

        Args:
            value: Value to parse

        Returns:
            Parsed number as float
        """
        if value is None:
            return 0.0

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove common non-numeric characters
            cleaned = re.sub(r'[^\d.-]', '', value)
            try:
                return float(cleaned)
            except ValueError:
                return 0.0

        return float(value) if value else 0.0

    def normalize_fuel_type(self, fuel_type: str) -> str:
        """
        Normalize fuel type string to standard values

        Args:
            fuel_type: Raw fuel type string

        Returns:
            Normalized fuel type
        """
        if not fuel_type:
            return 'unknown'

        fuel_type_lower = fuel_type.lower().strip()

        # Map various representations to standard values
        if any(keyword in fuel_type_lower for keyword in ['petrol', 'gasoline', 'benzin']):
            return 'petrol'
        elif any(keyword in fuel_type_lower for keyword in ['diesel', 'dizel']):
            return 'diesel'
        elif any(keyword in fuel_type_lower for keyword in ['cng', 'compressed', 'natural']):
            return 'cng'
        else:
            return 'other'