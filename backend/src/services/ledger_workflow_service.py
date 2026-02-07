from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio
import logging
from ..models.LedgerPage import LedgerPage
from ..models.SalesEntry import SalesEntry
from ..models.DailyReport import DailyReport
from ..services.image_preprocessing_service import ImagePreprocessingPipeline
from ..services.ocr_integration_service import OCRIntegrationService
from ..services.table_detection_service import TableDetectionService
from ..services.column_identification_service import ColumnIdentificationService
from ..services.sales_entry_extraction_service import SalesEntryExtractionService
from ..services.daily_calculations_service import DailyCalculationsService
from ..repositories.ledger_page_repository import LedgerPageRepository
from ..repositories.sales_entry_repository import SalesEntryRepository
from ..repositories.daily_report_repository import DailyReportRepository
from sqlalchemy.orm import Session


class LedgerWorkflowService:
    """
    Service to orchestrate the complete ledger processing workflow
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.preprocessing_pipeline = ImagePreprocessingPipeline()
        self.ocr_service = OCRIntegrationService()
        self.table_detection_service = TableDetectionService()
        self.column_identification_service = ColumnIdentificationService()
        self.extraction_service = SalesEntryExtractionService()
        self.calculation_service = DailyCalculationsService()

        # Repositories
        self.ledger_repo = LedgerPageRepository(db_session)
        self.sales_entry_repo = SalesEntryRepository(db_session)
        self.daily_report_repo = DailyReportRepository(db_session)

        # Set up logging
        self.logger = logging.getLogger(__name__)

    async def process_ledger_page(self, ledger_page_id: int) -> Dict[str, Any]:
        """
        Process a ledger page through the complete workflow
        :param ledger_page_id: ID of the ledger page to process
        :return: Dictionary containing processing results
        """
        try:
            # Get the ledger page from the database
            ledger_page = self.ledger_repo.get_by_id(ledger_page_id)
            if not ledger_page:
                raise ValueError(f"Ledger page with ID {ledger_page_id} not found")

            # Update processing status
            ledger_page.processing_status = "processing"
            self.db_session.commit()

            # Step 1: Preprocess the image
            self.logger.info(f"Starting preprocessing for ledger page {ledger_page_id}")
            processed_image_path = self.preprocessing_pipeline.preprocess_image(ledger_page.original_image_url)

            # Step 2: Perform OCR
            self.logger.info(f"Starting OCR for ledger page {ledger_page_id}")
            ocr_results = self.ocr_service.extract_ledger_data(processed_image_path)

            # Step 3: Detect table structure
            self.logger.info(f"Detecting table structure for ledger page {ledger_page_id}")
            table_structure = self.table_detection_service.detect_table_structure(processed_image_path)

            # Validate the detected structure
            validation_results = self.table_detection_service.validate_detected_structure(
                processed_image_path, table_structure
            )

            if not validation_results['is_valid_structure']:
                self.logger.warning(f"Table structure validation failed for ledger page {ledger_page_id}")
                ledger_page.processing_status = "failed"
                ledger_page.processing_errors = f"Table structure validation failed: {validation_results['issues']}"
                self.db_session.commit()
                return {
                    'success': False,
                    'message': 'Table structure validation failed',
                    'errors': validation_results['issues'],
                    'suggestions': validation_results['suggestions']
                }

            # Step 4: Identify columns
            self.logger.info(f"Identifying columns for ledger page {ledger_page_id}")
            identified_columns = self.column_identification_service.identify_columns(
                table_structure.columns, processed_image_path
            )

            # Validate column identification
            column_validation = self.column_identification_service.validate_column_identification(identified_columns)
            if not column_validation['is_valid']:
                self.logger.warning(f"Column identification validation failed for ledger page {ledger_page_id}")
                suggestions = self.column_identification_service.suggest_corrections(identified_columns, processed_image_path)

            # Step 5: Create column mapping
            column_mapping = self.column_identification_service.create_column_mapping(identified_columns)

            # Step 6: Extract sales entries
            self.logger.info(f"Extracting sales entries for ledger page {ledger_page_id}")
            extraction_results = self.extraction_service.extract_entries_with_validation(
                ocr_results, column_mapping
            )
            sales_entries = extraction_results['sales_entries']

            # Step 7: Calculate daily totals
            self.logger.info(f"Calculating daily totals for ledger page {ledger_page_id}")
            daily_report_data = self.calculation_service.generate_daily_report_data(sales_entries, ledger_page.user_id)

            # Step 8: Save results to database
            await self._save_processing_results(
                ledger_page,
                table_structure,
                identified_columns,
                sales_entries,
                daily_report_data
            )

            # Update status to completed
            ledger_page.processing_status = "completed"
            ledger_page.processed_date = datetime.utcnow()
            self.db_session.commit()

            self.logger.info(f"Successfully processed ledger page {ledger_page_id}")

            return {
                'success': True,
                'message': 'Ledger page processed successfully',
                'ledger_page_id': ledger_page_id,
                'sales_entries_count': len(sales_entries),
                'daily_report_generated': True,
                'needs_review_count': extraction_results['needs_review_count'],
                'column_validation': column_validation,
                'processing_time': (datetime.utcnow() - ledger_page.created_at).total_seconds()
            }

        except Exception as e:
            self.logger.error(f"Error processing ledger page {ledger_page_id}: {str(e)}")
            # Update status to failed
            ledger_page = self.ledger_repo.get_by_id(ledger_page_id)
            if ledger_page:
                ledger_page.processing_status = "failed"
                ledger_page.processing_errors = str(e)
                self.db_session.commit()

            return {
                'success': False,
                'message': f'Error processing ledger page: {str(e)}',
                'ledger_page_id': ledger_page_id
            }

    async def _save_processing_results(
        self,
        ledger_page: LedgerPage,
        table_structure,
        identified_columns,
        sales_entries: List[SalesEntry],
        daily_report_data: Dict[str, Any]
    ):
        """
        Save processing results to the database
        """
        # Update ledger page with detected columns and extracted data
        ledger_page.detected_columns = str([col.__dict__ for col in identified_columns])
        ledger_page.extracted_data = str([entry.__dict__ for entry in sales_entries])
        ledger_page.ocr_confidence_score = table_structure.confidence

        # Save sales entries
        for entry in sales_entries:
            entry.ledger_page_id = ledger_page.id
            self.db_session.add(entry)

        # Create and save daily report
        daily_report = DailyReport(
            user_id=ledger_page.user_id,
            report_date=daily_report_data['report_date'],
            total_liters_petrol=daily_report_data['total_liters_petrol'],
            total_liters_diesel=daily_report_data['total_liters_diesel'],
            total_liters_cng=daily_report_data['total_liters_cng'],
            total_revenue_petrol=daily_report_data['total_revenue_petrol'],
            total_revenue_diesel=daily_report_data['total_revenue_diesel'],
            total_revenue_cng=daily_report_data['total_revenue_cng'],
            grand_total_liters=daily_report_data['grand_total_liters'],
            grand_total_revenue=daily_report_data['grand_total_revenue'],
            total_sales_entries=daily_report_data['total_sales_entries']
        )

        self.db_session.add(daily_report)

        # Commit all changes
        self.db_session.commit()

    def process_ledger_batch(self, ledger_page_ids: List[int]) -> Dict[str, Any]:
        """
        Process multiple ledger pages in batch
        :param ledger_page_ids: List of ledger page IDs to process
        :return: Dictionary containing batch processing results
        """
        results = {
            'processed_count': 0,
            'successful_count': 0,
            'failed_count': 0,
            'results': [],
            'start_time': datetime.utcnow()
        }

        for page_id in ledger_page_ids:
            result = asyncio.run(self.process_ledger_page(page_id))
            results['results'].append(result)
            results['processed_count'] += 1

            if result['success']:
                results['successful_count'] += 1
            else:
                results['failed_count'] += 1

        results['end_time'] = datetime.utcnow()
        results['total_processing_time'] = (results['end_time'] - results['start_time']).total_seconds()

        return results

    async def process_with_manual_review_fallback(self, ledger_page_id: int) -> Dict[str, Any]:
        """
        Process ledger with automatic fallback to manual review when needed
        """
        result = await self.process_ledger_page(ledger_page_id)

        # If processing succeeded but has items needing review, flag for manual review
        if result['success'] and result.get('needs_review_count', 0) > 0:
            # Update ledger page to indicate manual review is needed
            ledger_page = self.ledger_repo.get_by_id(ledger_page_id)
            if ledger_page:
                # Add flag or note about manual review needed
                if ledger_page.processing_errors:
                    ledger_page.processing_errors += f"; {result['needs_review_count']} entries need manual review"
                else:
                    ledger_page.processing_errors = f"{result['needs_review_count']} entries need manual review"

                self.db_session.commit()

        return result

    def get_processing_status(self, ledger_page_id: int) -> Dict[str, Any]:
        """
        Get the processing status of a ledger page
        """
        ledger_page = self.ledger_repo.get_by_id(ledger_page_id)
        if not ledger_page:
            return {
                'error': f'Ledger page {ledger_page_id} not found'
            }

        return {
            'ledger_page_id': ledger_page_id,
            'status': ledger_page.processing_status,
            'created_at': ledger_page.created_at,
            'processed_at': ledger_page.processed_date,
            'ocr_confidence': ledger_page.ocr_confidence_score,
            'errors': ledger_page.processing_errors
        }

    def retry_failed_processing(self, ledger_page_id: int) -> Dict[str, Any]:
        """
        Retry processing for a failed ledger page
        """
        ledger_page = self.ledger_repo.get_by_id(ledger_page_id)
        if not ledger_page:
            return {
                'success': False,
                'message': f'Ledger page {ledger_page_id} not found'
            }

        if ledger_page.processing_status != 'failed':
            return {
                'success': False,
                'message': f'Ledger page {ledger_page_id} is not in failed state'
            }

        # Reset status to allow reprocessing
        ledger_page.processing_status = 'pending'
        ledger_page.processing_errors = None
        self.db_session.commit()

        # Process again
        return asyncio.run(self.process_ledger_page(ledger_page_id))

    async def process_ledger_with_custom_params(
        self,
        ledger_page_id: int,
        confidence_threshold: float = 0.85,
        enable_manual_review: bool = True
    ) -> Dict[str, Any]:
        """
        Process ledger with custom parameters
        :param ledger_page_id: ID of the ledger page to process
        :param confidence_threshold: Threshold for determining when manual review is needed
        :param enable_manual_review: Whether to enable manual review functionality
        :return: Dictionary containing processing results
        """
        # This would involve adjusting the workflow based on the parameters
        # For now, we'll just pass the parameters to the standard processing
        result = await self.process_ledger_page(ledger_page_id)

        # Apply confidence threshold logic
        if result['success'] and enable_manual_review:
            # Check if any entries have confidence below the threshold
            low_confidence_entries = self.sales_entry_repo.get_low_confidence_entries(confidence_threshold)
            low_confidence_count = len([e for e in low_confidence_entries if e.ledger_page_id == ledger_page_id])

            result['low_confidence_entries_count'] = low_confidence_count

        return result