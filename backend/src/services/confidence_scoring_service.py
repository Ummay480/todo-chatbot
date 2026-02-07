from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from ..services.ocr_service import OCRResult


@dataclass
class ConfidenceScore:
    """
    Data class to hold confidence scoring results
    """
    overall_score: float
    component_scores: Dict[str, float]
    confidence_ranges: Dict[str, List[any]]  # Ranges of data with different confidence levels
    recommendations: List[str]


class ConfidenceScoringService:
    """
    Service for calculating and managing confidence scores for OCR and data extraction results
    """

    def __init__(self):
        # Confidence thresholds
        self.high_confidence_threshold = 0.90
        self.medium_confidence_threshold = 0.75
        self.low_confidence_threshold = 0.60

    def calculate_overall_confidence(self, ocr_results: List[OCRResult], extracted_data: Dict[str, any] = None) -> ConfidenceScore:
        """
        Calculate overall confidence score based on OCR results and extracted data
        :param ocr_results: List of OCR results with confidence scores
        :param extracted_data: Additional extracted data to consider in confidence calculation
        :return: ConfidenceScore object with overall score and components
        """
        if not ocr_results:
            return ConfidenceScore(
                overall_score=0.0,
                component_scores={'ocr': 0.0, 'structure': 0.0, 'consistency': 0.0},
                confidence_ranges={'high': [], 'medium': [], 'low': []},
                recommendations=['No OCR results provided']
            )

        # Calculate OCR component score
        ocr_score = self._calculate_ocr_confidence(ocr_results)

        # Calculate structure component score if extracted data is provided
        structure_score = self._calculate_structure_confidence(extracted_data) if extracted_data else 0.5  # Default medium

        # Calculate consistency score based on OCR results
        consistency_score = self._calculate_consistency_confidence(ocr_results, extracted_data)

        # Weighted average of components
        overall_score = (ocr_score * 0.4) + (structure_score * 0.3) + (consistency_score * 0.3)

        # Categorize results by confidence level
        high_confidence_items, medium_confidence_items, low_confidence_items = self._categorize_by_confidence(ocr_results)

        # Generate recommendations
        recommendations = self._generate_recommendations(overall_score, ocr_results, extracted_data)

        return ConfidenceScore(
            overall_score=round(overall_score, 3),
            component_scores={
                'ocr': round(ocr_score, 3),
                'structure': round(structure_score, 3),
                'consistency': round(consistency_score, 3)
            },
            confidence_ranges={
                'high': high_confidence_items,
                'medium': medium_confidence_items,
                'low': low_confidence_items
            },
            recommendations=recommendations
        )

    def _calculate_ocr_confidence(self, ocr_results: List[OCRResult]) -> float:
        """
        Calculate confidence based on OCR results
        """
        if not ocr_results:
            return 0.0

        # Calculate average confidence
        avg_confidence = sum(result.confidence for result in ocr_results) / len(ocr_results)

        # Normalize to 0-1 scale (OCR confidence is typically 0-100)
        normalized_avg = avg_confidence / 100.0

        # Calculate confidence variance (lower variance = higher reliability)
        confidences = [result.confidence / 100.0 for result in ocr_results]
        variance = np.var(confidences)
        variance_penalty = min(variance * 2, 0.1)  # Max 10% penalty for high variance

        # Calculate score based on average and variance
        score = max(normalized_avg - variance_penalty, 0.0)

        return score

    def _calculate_structure_confidence(self, extracted_data: Dict[str, any]) -> float:
        """
        Calculate confidence based on the structure of extracted data
        """
        if not extracted_data:
            return 0.0

        score = 0.5  # Start with medium confidence

        # Check for expected fields in extracted data
        expected_fields = ['date', 'fuel_type', 'liters_sold', 'total_amount']
        found_fields = [field for field in expected_fields if field in extracted_data.get('summary', {})]

        field_coverage = len(found_fields) / len(expected_fields)
        score += (field_coverage * 0.3)  # Up to 30% boost for good field coverage

        # Check for reasonable data patterns
        if extracted_data.get('summary', {}).get('total_sales_entries', 0) > 0:
            score += 0.1  # Small boost for having sales entries

        # Penalize if there are processing errors
        if extracted_data.get('processing_errors'):
            score -= 0.2  # 20% penalty for processing errors

        return min(max(score, 0.0), 1.0)  # Clamp between 0 and 1

    def _calculate_consistency_confidence(self, ocr_results: List[OCRResult], extracted_data: Dict[str, any] = None) -> float:
        """
        Calculate confidence based on consistency of results
        """
        if not ocr_results:
            return 0.0

        # Check for consistency in numeric patterns
        numeric_results = [r for r in ocr_results if self._is_numeric_content(r.text)]

        if len(numeric_results) < 2:
            # If we don't have many numeric results, rely on overall OCR confidence
            avg_confidence = sum(r.confidence for r in ocr_results) / len(ocr_results) / 100.0
            return avg_confidence

        # Calculate consistency among numeric values
        numeric_values = []
        for result in numeric_results:
            try:
                val = float(self._clean_numeric_text(result.text))
                numeric_values.append(val)
            except ValueError:
                continue

        if len(numeric_values) < 2:
            return 0.5  # Default medium confidence

        # Calculate coefficient of variation (lower CV = more consistent)
        mean_val = np.mean(numeric_values)
        std_val = np.std(numeric_values)

        if mean_val == 0:
            cv = 1.0 if std_val > 0 else 0  # High inconsistency if mean is 0 but std > 0
        else:
            cv = std_val / abs(mean_val) if std_val > 0 else 0

        # Convert coefficient of variation to confidence (inverse relationship)
        consistency_score = max(0.0, 1.0 - min(cv, 1.0))

        return consistency_score

    def _is_numeric_content(self, text: str) -> bool:
        """
        Check if text content is likely numeric
        """
        import re
        # Check if text contains mostly numbers and common numeric symbols
        digits = sum(1 for c in text if c.isdigit())
        total_chars = len(text.replace(' ', ''))  # Ignore spaces

        if total_chars == 0:
            return False

        digit_ratio = digits / total_chars
        return digit_ratio > 0.5  # More than half characters are digits

    def _clean_numeric_text(self, text: str) -> str:
        """
        Clean text to extract numeric value
        """
        import re
        # Remove non-numeric characters except decimal point and minus sign
        cleaned = re.sub(r'[^\d.-]', '', text)
        return cleaned

    def _categorize_by_confidence(self, ocr_results: List[OCRResult]) -> Tuple[List[any], List[any], List[any]]:
        """
        Categorize OCR results by confidence level
        """
        high_confidence = []
        medium_confidence = []
        low_confidence = []

        for result in ocr_results:
            norm_conf = result.confidence / 100.0  # Normalize to 0-1 scale
            item_data = {
                'text': result.text,
                'confidence': norm_conf,
                'bbox': result.bounding_box
            }

            if norm_conf >= self.high_confidence_threshold:
                high_confidence.append(item_data)
            elif norm_conf >= self.medium_confidence_threshold:
                medium_confidence.append(item_data)
            else:
                low_confidence.append(item_data)

        return high_confidence, medium_confidence, low_confidence

    def _generate_recommendations(self, overall_score: float, ocr_results: List[OCRResult], extracted_data: Dict[str, any]) -> List[str]:
        """
        Generate recommendations based on confidence score
        """
        recommendations = []

        if overall_score >= self.high_confidence_threshold:
            recommendations.append("High confidence in results. Suitable for automated processing.")
        elif overall_score >= self.medium_confidence_threshold:
            recommendations.append("Medium confidence in results. Manual review recommended for critical values.")
        else:
            recommendations.append("Low confidence in results. Extensive manual review required.")

        # Add specific recommendations based on OCR results
        low_confidence_results = [r for r in ocr_results if (r.confidence / 100.0) < self.low_confidence_threshold]
        if len(low_confidence_results) > 5:
            recommendations.append(f"Many low-confidence OCR results ({len(low_confidence_results)} items). "
                                 "Consider improving image quality or using manual verification.")

        # Check for specific data issues
        if extracted_data:
            # Check if amounts seem inconsistent
            summary = extracted_data.get('summary', {})
            if summary.get('total_revenue_petrol', 0) > 1000000:  # Suspiciously high amount
                recommendations.append("Very high revenue detected. Verify for data entry errors.")

        return recommendations

    def get_confidence_level(self, score: float) -> str:
        """
        Get the confidence level string for a given score
        """
        if score >= self.high_confidence_threshold:
            return "high"
        elif score >= self.medium_confidence_threshold:
            return "medium"
        elif score >= self.low_confidence_threshold:
            return "low"
        else:
            return "very_low"

    def should_flag_for_review(self, score: float, threshold: Optional[float] = None) -> bool:
        """
        Determine if results should be flagged for manual review
        """
        if threshold is None:
            threshold = self.medium_confidence_threshold

        return score < threshold

    def calculate_field_confidence(self, field_name: str, field_value: any, ocr_result: OCRResult = None) -> float:
        """
        Calculate confidence for a specific field
        """
        base_confidence = 0.5  # Start with medium confidence

        # Adjust based on OCR confidence if available
        if ocr_result:
            base_confidence = ocr_result.confidence / 100.0

        # Field-specific validation
        if field_name == 'date':
            base_confidence = self._validate_date_confidence(field_value, base_confidence)
        elif field_name in ['liters_sold', 'rate_per_liter', 'total_amount']:
            base_confidence = self._validate_numeric_confidence(field_value, base_confidence, field_name)
        elif field_name == 'fuel_type':
            base_confidence = self._validate_fuel_type_confidence(field_value, base_confidence)

        return base_confidence

    def _validate_date_confidence(self, date_value: any, base_confidence: float) -> float:
        """
        Validate confidence for date fields
        """
        if date_value is None:
            return 0.1  # Very low confidence for missing dates

        try:
            from datetime import datetime
            if isinstance(date_value, str):
                # Try to parse common date formats
                formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y', '%m-%d-%Y']
                for fmt in formats:
                    try:
                        datetime.strptime(date_value, fmt)
                        return min(base_confidence + 0.1, 1.0)  # Small boost for valid format
                    except ValueError:
                        continue
                return base_confidence - 0.1  # Small penalty for unrecognized format
            elif isinstance(date_value, datetime):
                # If it's already a datetime object, boost confidence slightly
                return min(base_confidence + 0.05, 1.0)
        except Exception:
            pass

        return base_confidence

    def _validate_numeric_confidence(self, value: any, base_confidence: float, field_type: str) -> float:
        """
        Validate confidence for numeric fields
        """
        if value is None:
            return 0.1  # Very low confidence for missing values

        try:
            num_value = float(value)

            # Check for reasonable ranges based on field type
            if field_type == 'liters_sold':
                if num_value < 0 or num_value > 10000:  # Unreasonable for single transaction
                    return base_confidence - 0.2
            elif field_type == 'rate_per_liter':
                if num_value < 50 or num_value > 200:  # Unreasonable price per liter in Pakistan
                    return base_confidence - 0.2
            elif field_type == 'total_amount':
                if num_value < 0 or num_value > 100000:  # Unreasonable for single transaction
                    return base_confidence - 0.2

            return min(base_confidence + 0.05, 1.0)  # Small boost for valid numeric value
        except (ValueError, TypeError):
            return base_confidence - 0.3  # Penalty for non-numeric value

    def _validate_fuel_type_confidence(self, fuel_type: str, base_confidence: float) -> float:
        """
        Validate confidence for fuel type fields
        """
        if not fuel_type:
            return 0.1  # Very low confidence for missing fuel type

        # Common fuel types in Pakistan
        valid_fuel_types = ['petrol', 'diesel', 'cng', 'kerosene', 'gasoline', 'high speed diesel']

        if isinstance(fuel_type, str) and fuel_type.lower().strip() in [f.lower() for f in valid_fuel_types]:
            return min(base_confidence + 0.1, 1.0)  # Boost for recognized fuel type
        else:
            return base_confidence  # No change for unrecognized type

    def assess_image_quality_impact(self, image_path: str) -> Dict[str, any]:
        """
        Assess how image quality affects confidence (placeholder implementation)
        In a real implementation, this would analyze image characteristics
        """
        return {
            'resolution_sufficiency': 0.8,
            'contrast_quality': 0.7,
            'blur_estimation': 0.1,
            'noise_level': 0.2,
            'quality_impact_on_confidence': 0.15  # Estimated impact on confidence
        }