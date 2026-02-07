from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.SalesEntry import SalesEntry
from ..models.DailyReport import DailyReport
from ..services.calculation_engine_service import CalculationEngineService


class DailyCalculationsService:
    """
    Service for calculating daily totals and metrics from sales entries
    """

    def __init__(self):
        self.calculation_engine = CalculationEngineService()

    def calculate_daily_totals(self, sales_entries: List[SalesEntry], report_date: datetime = None) -> DailyReport:
        """
        Calculate daily totals and create a DailyReport object
        :param sales_entries: List of sales entries for the day
        :param report_date: Date for the report (defaults to current date)
        :return: DailyReport object with calculated totals
        """
        if not report_date:
            report_date = datetime.now()

        # Convert SalesEntry objects to dictionaries for the calculation engine
        entries_dicts = []
        for entry in sales_entries:
            entry_dict = {
                'date': entry.date,
                'nozzle_id': entry.nozzle_id,
                'fuel_type': entry.fuel_type,
                'opening_reading': entry.opening_reading,
                'closing_reading': entry.closing_reading,
                'liters_sold': entry.liters_sold,
                'rate_per_liter': entry.rate_per_liter,
                'total_amount': entry.total_amount
            }
            entries_dicts.append(entry_dict)

        # Calculate daily totals using the calculation engine
        daily_totals = self.calculation_engine.calculate_daily_totals(entries_dicts)

        # Create and populate a DailyReport object
        daily_report = DailyReport(
            report_date=report_date,
            total_liters_petrol=daily_totals['petrol']['liters'],
            total_liters_diesel=daily_totals['diesel']['liters'],
            total_liters_cng=daily_totals['cng']['liters'],
            total_revenue_petrol=daily_totals['petrol']['revenue'],
            total_revenue_diesel=daily_totals['diesel']['revenue'],
            total_revenue_cng=daily_totals['cng']['revenue'],
            grand_total_liters=daily_totals['grand_total_liters'],
            grand_total_revenue=daily_totals['grand_total_revenue'],
            total_sales_entries=daily_totals['total_entries']
        )

        return daily_report

    def calculate_nozzle_performance(self, sales_entries: List[SalesEntry]) -> Dict[str, Any]:
        """
        Calculate performance metrics per nozzle
        :param sales_entries: List of sales entries
        :return: Dictionary containing nozzle performance data
        """
        # Convert SalesEntry objects to dictionaries for the calculation engine
        entries_dicts = []
        for entry in sales_entries:
            entry_dict = {
                'nozzle_id': entry.nozzle_id,
                'fuel_type': entry.fuel_type,
                'liters_sold': entry.liters_sold,
                'total_amount': entry.total_amount
            }
            entries_dicts.append(entry_dict)

        # Calculate nozzle performance using the calculation engine
        performance_data = self.calculation_engine.calculate_nozzle_performance(entries_dicts)

        return performance_data

    def calculate_fuel_type_metrics(self, sales_entries: List[SalesEntry]) -> Dict[str, Dict[str, float]]:
        """
        Calculate metrics grouped by fuel type
        :param sales_entries: List of sales entries
        :return: Dictionary with metrics for each fuel type
        """
        # Group entries by fuel type and calculate totals
        fuel_metrics = {
            'petrol': {'liters': 0, 'revenue': 0, 'count': 0},
            'diesel': {'liters': 0, 'revenue': 0, 'count': 0},
            'cng': {'liters': 0, 'revenue': 0, 'count': 0},
            'other': {'liters': 0, 'revenue': 0, 'count': 0}
        }

        for entry in sales_entries:
            if entry.fuel_type:
                normalized_type = self._normalize_fuel_type(entry.fuel_type)

                if normalized_type in fuel_metrics:
                    fuel_metrics[normalized_type]['liters'] += entry.liters_sold or 0
                    fuel_metrics[normalized_type]['revenue'] += entry.total_amount or 0
                    fuel_metrics[normalized_type]['count'] += 1
                else:
                    fuel_metrics['other']['liters'] += entry.liters_sold or 0
                    fuel_metrics['other']['revenue'] += entry.total_amount or 0
                    fuel_metrics['other']['count'] += 1

        # Round values
        for fuel_type in fuel_metrics:
            fuel_metrics[fuel_type]['liters'] = round(fuel_metrics[fuel_type]['liters'], 2)
            fuel_metrics[fuel_type]['revenue'] = round(fuel_metrics[fuel_type]['revenue'], 2)

        return fuel_metrics

    def _normalize_fuel_type(self, fuel_type: str) -> str:
        """
        Normalize fuel type names to standard values
        """
        if not fuel_type:
            return 'other'

        fuel_lower = fuel_type.lower().strip()

        # Map various representations to standard types
        if any(word in fuel_lower for word in ['petrol', 'gasoline', 'benzin', 'benzene', 'premium']):
            return 'petrol'
        elif any(word in fuel_lower for word in ['diesel', 'dizel', 'petrodiesel', 'high speed diesel']):
            return 'diesel'
        elif any(word in fuel_lower for word in ['cng', 'compressed natural gas', 'natural gas']):
            return 'cng'
        else:
            return 'other'

    def calculate_daily_summary_stats(self, sales_entries: List[SalesEntry]) -> Dict[str, Any]:
        """
        Calculate various daily summary statistics
        :param sales_entries: List of sales entries
        :return: Dictionary containing summary statistics
        """
        if not sales_entries:
            return {
                'total_entries': 0,
                'average_transaction_value': 0,
                'highest_transaction': 0,
                'lowest_transaction': 0,
                'total_nozzles_used': 0,
                'busiest_nozzle': None
            }

        total_revenue = sum((entry.total_amount or 0) for entry in sales_entries)
        transaction_values = [entry.total_amount for entry in sales_entries if entry.total_amount is not None]

        if transaction_values:
            avg_value = total_revenue / len(sales_entries)
            highest_value = max(transaction_values)
            lowest_value = min(transaction_values)
        else:
            avg_value = highest_value = lowest_value = 0

        # Count unique nozzles used
        nozzles_used = set(entry.nozzle_id for entry in sales_entries if entry.nozzle_id)

        # Find busiest nozzle
        nozzle_counts = {}
        for entry in sales_entries:
            if entry.nozzle_id:
                nozzle_counts[entry.nozzle_id] = nozzle_counts.get(entry.nozzle_id, 0) + 1

        busiest_nozzle = max(nozzle_counts, key=nozzle_counts.get) if nozzle_counts else None

        return {
            'total_entries': len(sales_entries),
            'average_transaction_value': round(avg_value, 2),
            'highest_transaction': round(highest_value, 2),
            'lowest_transaction': round(lowest_value, 2),
            'total_nozzles_used': len(nozzles_used),
            'busiest_nozzle': busiest_nozzle
        }

    def validate_calculations(self, sales_entries: List[SalesEntry], expected_totals: Dict = None) -> Dict[str, Any]:
        """
        Validate calculations by comparing computed values with expected values
        :param sales_entries: List of sales entries
        :param expected_totals: Dictionary of expected totals for validation
        :return: Dictionary containing validation results
        """
        # Convert SalesEntry objects to dictionaries for the calculation engine
        entries_dicts = []
        for entry in sales_entries:
            entry_dict = {
                'fuel_type': entry.fuel_type,
                'liters_sold': entry.liters_sold,
                'total_amount': entry.total_amount
            }
            entries_dicts.append(entry_dict)

        # Validate calculations using the calculation engine
        validation_results = self.calculation_engine.validate_calculations(entries_dicts, expected_totals)

        return validation_results

    def calculate_profit_margins(self, sales_entries: List[SalesEntry], cost_prices: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Calculate profit margins if cost prices are provided
        :param sales_entries: List of sales entries
        :param cost_prices: Dictionary mapping fuel type to cost price per liter
        :return: Dictionary containing profit margin calculations
        """
        if not cost_prices:
            # Default cost prices (these would normally come from a configuration or database)
            cost_prices = {
                'petrol': 100.0,  # Cost per liter
                'diesel': 90.0,
                'cng': 30.0
            }

        profit_data = {
            'petrol': {'revenue': 0, 'cost': 0, 'profit': 0, 'margin': 0},
            'diesel': {'revenue': 0, 'cost': 0, 'profit': 0, 'margin': 0},
            'cng': {'revenue': 0, 'cost': 0, 'profit': 0, 'margin': 0},
            'total': {'revenue': 0, 'cost': 0, 'profit': 0, 'margin': 0}
        }

        # Calculate costs and profits by fuel type
        for entry in sales_entries:
            if entry.fuel_type and entry.liters_sold:
                normalized_type = self._normalize_fuel_type(entry.fuel_type)
                if normalized_type in profit_data and normalized_type != 'total':
                    cost_price_per_liter = cost_prices.get(normalized_type, 0)

                    revenue = entry.total_amount or 0
                    cost = entry.liters_sold * cost_price_per_liter
                    profit = revenue - cost

                    profit_data[normalized_type]['revenue'] += revenue
                    profit_data[normalized_type]['cost'] += cost
                    profit_data[normalized_type]['profit'] += profit

                    # Update totals
                    profit_data['total']['revenue'] += revenue
                    profit_data['total']['cost'] += cost
                    profit_data['total']['profit'] += profit

        # Calculate margins
        for fuel_type in ['petrol', 'diesel', 'cng', 'total']:
            if profit_data[fuel_type]['revenue'] > 0:
                profit_data[fuel_type]['margin'] = round(
                    (profit_data[fuel_type]['profit'] / profit_data[fuel_type]['revenue']) * 100, 2
                )
            else:
                profit_data[fuel_type]['margin'] = 0

            # Round values
            profit_data[fuel_type]['revenue'] = round(profit_data[fuel_type]['revenue'], 2)
            profit_data[fuel_type]['cost'] = round(profit_data[fuel_type]['cost'], 2)
            profit_data[fuel_type]['profit'] = round(profit_data[fuel_type]['profit'], 2)

        return profit_data

    def generate_daily_report_data(self, sales_entries: List[SalesEntry], user_id: int = None) -> Dict[str, Any]:
        """
        Generate complete daily report data
        :param sales_entries: List of sales entries for the day
        :param user_id: ID of the user requesting the report
        :return: Dictionary containing all daily report data
        """
        # Calculate basic totals
        daily_report = self.calculate_daily_totals(sales_entries)

        # Get additional metrics
        nozzle_performance = self.calculate_nozzle_performance(sales_entries)
        fuel_metrics = self.calculate_fuel_type_metrics(sales_entries)
        summary_stats = self.calculate_daily_summary_stats(sales_entries)

        # Create comprehensive report data
        report_data = {
            'user_id': user_id,
            'report_date': daily_report.report_date,
            'total_liters_petrol': daily_report.total_liters_petrol,
            'total_liters_diesel': daily_report.total_liters_diesel,
            'total_liters_cng': daily_report.total_liters_cng,
            'total_revenue_petrol': daily_report.total_revenue_petrol,
            'total_revenue_diesel': daily_report.total_revenue_diesel,
            'total_revenue_cng': daily_report.total_revenue_cng,
            'grand_total_liters': daily_report.grand_total_liters,
            'grand_total_revenue': daily_report.grand_total_revenue,
            'total_sales_entries': daily_report.total_sales_entries,
            'nozzle_performance': nozzle_performance,
            'fuel_type_metrics': fuel_metrics,
            'summary_statistics': summary_stats,
            'sales_entries': sales_entries  # Include the original entries for detailed view
        }

        return report_data