import os
import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS: set[str] = {".png", ".jpg", ".jpeg", ".pdf"}
MAX_FILE_SIZE_MB: float = 100.0


def validate_file_extension(filename: str) -> str | None:
    """Return the lowercased extension if allowed, else None."""
    ext = os.path.splitext(filename.lower())[1]
    return ext if ext in ALLOWED_EXTENSIONS else None


def validate_file_content(file_bytes: bytes, filename: str) -> bool:
    """Validate file content using magic bytes against the declared extension."""
    ext = os.path.splitext(filename.lower())[1]
    if ext == ".png":
        return file_bytes.startswith(b"\x89PNG")
    elif ext in (".jpg", ".jpeg"):
        return file_bytes.startswith(b"\xff\xd8")
    elif ext == ".pdf":
        return file_bytes.startswith(b"%PDF")
    return False


def validate_file_size(file_bytes: bytes) -> bool:
    """Return True if the file is within the allowed size limit."""
    file_size_mb = len(file_bytes) / (1024 * 1024)
    return file_size_mb <= MAX_FILE_SIZE_MB


def clean_prediction_result(res_data: list) -> tuple[list, str]:
    """
    Filter and simplify PaddleOCR prediction results.
    Returns (cleaned_results, extracted_text_content).
    """
    cleaned_results: list[dict] = []
    extracted_blocks: list[str] = []
    text_labels = {"number", "paragraph_title", "vision_footnote", "doc_title", "text"}

    for item in res_data:
        if not isinstance(item, dict):
            cleaned_results.append(item)
            continue

        page_res = item.get("res") if "res" in item else item
        if not isinstance(page_res, dict):
            cleaned_results.append(item)
            continue

        raw_parsing_list = page_res.get("parsing_res_list", [])
        cleaned_parsing_list: list[dict] = []
        if isinstance(raw_parsing_list, list):
            for block in raw_parsing_list:
                if not isinstance(block, dict):
                    continue
                block_label = block.get("block_label")
                block_content = block.get("block_content")

                cleaned_parsing_list.append({
                    "block_label": block_label,
                    "block_content": block_content,
                    "block_bbox": block.get("block_bbox"),
                    "block_order": block.get("block_order"),
                })

                if block_label in text_labels and block_content:
                    extracted_blocks.append(str(block_content))

        page_index = page_res.get("page_index")
        page_count = page_res.get("page_count")

        cleaned_results.append({
            "page_index": page_index if page_index is not None else 0,
            "page_count": page_count if (page_count is not None and page_count != 0) else 1,
            "width": page_res.get("width"),
            "height": page_res.get("height"),
            "parsing_res_list": cleaned_parsing_list,
        })

    extracted_content = "\n".join(extracted_blocks)
    return cleaned_results, extracted_content


async def run_prediction(pipeline: Any, file_path: str) -> list:
    """Run the PaddleOCR pipeline in a thread executor to avoid blocking the event loop."""
    loop = asyncio.get_running_loop()

    def _predict() -> list:
        result = pipeline.predict(input=file_path)
        results_data = []
        for res in result:
            try:
                results_data.append(res.json)
            except AttributeError:
                results_data.append(str(res))
        return results_data

    return await loop.run_in_executor(None, _predict)
