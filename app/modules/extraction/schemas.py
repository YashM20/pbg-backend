from pydantic import BaseModel


class OcrErrorDetail(BaseModel):
    message: str
    details: str | None = None


class OcrResultData(BaseModel):
    filename: str
    extractedContent: str
    prediction_duration_seconds: float
    results: list


class OcrResponse(BaseModel):
    ok: bool
    status: str
    message: str
    error: OcrErrorDetail | None = None
    code: int
    data: OcrResultData | None = None
