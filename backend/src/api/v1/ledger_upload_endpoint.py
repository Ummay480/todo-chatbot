from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
import os
from typing import Optional

from ...database.connection import get_db_session
from ...services.image_upload_service import ImageUploadService
from ...services.image_processing import ImageProcessingUtil
from ...services.ocr_service import OCRService
from ...services.structure_detection_service import StructureDetectionService
from ...services.calculation_engine_service import CalculationEngineService
from ...repositories.ledger_page_repository import LedgerPageRepository
from ...repositories.sales_entry_repository import SalesEntryRepository
from ...models.LedgerPage import LedgerPage
from ...models.SalesEntry import SalesEntry


router = APIRouter(prefix="/api/v1/ledger", tags=["ledger"])


@router.post("/upload")
async def upload_ledger(
    file: UploadFile = File(...),
    db: Session = Depends(get_db_session),
    background_tasks: BackgroundTasks = None
):
    """
    Upload a ledger image and initiate processing
    """
    # Validate file type
    allowed_extensions = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".webp"}
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}")

    # Initialize services
    upload_service = ImageUploadService(upload_folder="uploads/")

    # Upload and save the image
    file_path = await upload_service.upload_image(file)
    if not file_path:
        raise HTTPException(status_code=400, detail="Invalid file or upload failed")

    try:
        # Initialize the ledger page in the database
        ledger_page = LedgerPage(
            original_image_url=file_path,
            processing_status="processing"
        )

        # Add to database
        db.add(ledger_page)
        db.commit()
        db.refresh(ledger_page)

        # Schedule background processing
        if background_tasks:
            background_tasks.add_task(process_ledger_image, ledger_page.id, file_path, db)
        else:
            # If no background tasks, process synchronously
            process_ledger_image(ledger_page.id, file_path, db)

        return {
            "message": "Ledger uploaded successfully",
            "ledger_page_id": ledger_page.id,
            "processing_status": ledger_page.processing_status
        }
    except Exception as e:
        # Clean up the uploaded file if processing fails
        upload_service.cleanup_temp_file(file_path)
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing ledger: {str(e)}")


def process_ledger_image(ledger_page_id: int, image_path: str, db: Session):
    """
    Process the uploaded ledger image in the background
    """
    try:
        # Get the ledger page from the database
        ledger_repo = LedgerPageRepository(db)
        ledger_page = ledger_repo.get_by_id(ledger_page_id)

        if not ledger_page:
            raise ValueError(f"Ledger page with ID {ledger_page_id} not found")

        # Update status to processing
        ledger_page.processing_status = "processing"
        db.commit()

        # Preprocess the image
        processed_image_path = ImageProcessingUtil.preprocess_image_for_ocr(image_path)

        # Initialize services
        ocr_service = OCRService()
        structure_service = StructureDetectionService()
        calc_service = CalculationEngineService()

        # Perform OCR
        ocr_results = ocr_service.extract_structured_data(processed_image_path)

        # Detect table structure
        columns, rows = structure_service.detect_table_structure(processed_image_path)

        # Process the extracted data
        # For now, we'll just save the basic results
        ledger_page.detected_columns = str([col.__dict__ for col in columns])
        ledger_page.extracted_data = str([row.__dict__ for row in rows])
        ledger_page.ocr_confidence_score = ocr_results.get('confidence_avg', 0)
        ledger_page.processing_status = "completed"

        # Update the database
        db.commit()
        db.refresh(ledger_page)

        print(f"Ledger page {ledger_page_id} processed successfully")

    except Exception as e:
        # Update status to failed
        ledger_repo = LedgerPageRepository(db)
        ledger_page = ledger_repo.get_by_id(ledger_page_id)
        if ledger_page:
            ledger_page.processing_status = "failed"
            ledger_page.processing_errors = str(e)
            db.commit()

        print(f"Error processing ledger page {ledger_page_id}: {str(e)}")
        raise e