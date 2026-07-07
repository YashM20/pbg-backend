import uuid
import logging
import asyncio
from pathlib import Path

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.pipeline import get_pipeline
from app.modules.extraction.schemas import OcrResponse, OcrErrorDetail, OcrResultData
from app.modules.extraction import service

logger = logging.getLogger(__name__)

router = APIRouter()

# Ensure temp upload directory exists at import time
TEMP_DIR = Path(settings.ocr_temp_dir)
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def _error_response(status_code: int, message: str, detail: str | None = None) -> JSONResponse:
    """Build a standardised error JSONResponse."""
    return JSONResponse(
        status_code=status_code,
        content=OcrResponse(
            ok=False,
            status="error",
            message=message,
            error=OcrErrorDetail(message=message, details=detail),
            code=status_code,
            data=None,
        ).model_dump(),
    )


@router.post("", response_model=OcrResponse)
async def predict_ocr(file: UploadFile = File(...)) -> OcrResponse | JSONResponse:
    """
    Accept an uploaded image or PDF, validate it, run PaddleOCR-VL,
    and return structured results.
    """
    filename = file.filename or "upload.jpg"
    logger.info(f"Received prediction request for file: '{filename}'")

    # --- Validate extension ---
    ext = service.validate_file_extension(filename)
    if ext is None:
        logger.warning(f"Rejected upload with unsupported extension for file: '{filename}'")
        return _error_response(
            400,
            f"Unsupported file format. Allowed: {sorted(service.ALLOWED_EXTENSIONS)}",
            "Unsupported file format.",
        )

    # --- Read & validate size ---
    contents = await file.read()
    if not service.validate_file_size(contents):
        logger.warning(f"Rejected upload exceeding size limit for file: '{filename}'")
        return _error_response(
            400,
            f"File exceeds maximum size limit of {service.MAX_FILE_SIZE_MB}MB.",
            "File size limit exceeded.",
        )

    # --- Validate magic bytes ---
    if not service.validate_file_content(contents, filename):
        logger.warning(f"Rejected upload due to invalid signature mismatch for file: '{filename}'")
        return _error_response(
            400,
            "File content does not match its extension signature.",
            "Invalid file signature.",
        )

    # --- Ensure pipeline is loaded ---
    pipeline = get_pipeline()
    if pipeline is None:
        logger.error("Prediction requested but model pipeline is not initialized.")
        return _error_response(
            503,
            "Model pipeline is currently unavailable or failed to initialize.",
            "Pipeline model is not loaded/initialized.",
        )

    # --- Save to temp file, predict, cleanup ---
    temp_filename = f"{uuid.uuid4().hex}{ext}"
    temp_path = TEMP_DIR / temp_filename

    try:
        temp_path.write_bytes(contents)
        logger.info(f"Saved temporary upload to: {temp_path}")

        start_time = asyncio.get_event_loop().time()
        prediction_results = await service.run_prediction(pipeline, str(temp_path))
        duration = asyncio.get_event_loop().time() - start_time

        logger.info(f"Prediction completed for '{filename}' in {duration:.4f}s")

        cleaned_results, extracted_content = service.clean_prediction_result(prediction_results)

        return OcrResponse(
            ok=True,
            status="success",
            message="OCR prediction completed successfully",
            error=None,
            code=200,
            data=OcrResultData(
                filename=filename,
                extractedContent=extracted_content,
                prediction_duration_seconds=round(duration, 4),
                results=cleaned_results,
            ),
        )

    except Exception as e:
        logger.error(f"Prediction failed for '{filename}': {e}", exc_info=True)
        return _error_response(
            500,
            "An internal error occurred during prediction.",
            e.__class__.__name__,
        )
    finally:
        try:
            if temp_path.exists():
                temp_path.unlink()
                logger.info(f"Cleaned up temporary file: {temp_path}")
        except Exception as cleanup_err:
            logger.warning(f"Failed to clean up '{temp_path}': {cleanup_err}")
