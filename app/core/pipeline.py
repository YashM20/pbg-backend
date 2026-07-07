import logging
import os
from typing import Any

logger = logging.getLogger(__name__)

pipeline: Any | None = None


async def init_pipeline(device: str) -> None:
    """Initialize the PaddleOCR-VL pipeline at startup."""
    global pipeline
    
    paddlex_device = device
    if device.startswith("gpu:"):
        gpu_idx = device.split(":")[1]
        os.environ["CUDA_VISIBLE_DEVICES"] = gpu_idx
        paddlex_device = "gpu:0"
        logger.info(f"Setting CUDA_VISIBLE_DEVICES={gpu_idx} and initializing pipeline on gpu:0")
    else:
        logger.info(f"Initializing PaddleOCR-VL pipeline on {device}...")
        
    try:
        from paddlex import create_pipeline

        pipeline = create_pipeline(pipeline="PaddleOCR-VL", device=paddlex_device)
        logger.info("PaddleOCR-VL pipeline loaded successfully.")
    except ImportError:
        logger.warning(
            "paddlex is not installed — OCR pipeline will be unavailable. "
            "Install paddlex to enable the /extraction endpoint."
        )
    except Exception as e:
        logger.error(f"Failed to load PaddleOCR-VL pipeline: {e}", exc_info=True)


async def close_pipeline() -> None:
    """Release pipeline resources on shutdown."""
    global pipeline
    logger.info("Shutting down PaddleOCR-VL pipeline resources...")
    pipeline = None


def get_pipeline() -> Any | None:
    """Return the current pipeline instance (or None if not loaded)."""
    return pipeline
