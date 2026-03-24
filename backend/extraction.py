import os
import json
from typing import Optional
import anthropic
from pydantic import BaseModel, field_validator

VALID_CATEGORIES = {
    "Complete Blood Count",
    "Lipid Panel",
    "Metabolic Panel",
    "Thyroid Function",
    "Liver Function",
    "Kidney Function",
    "Vitamin",
    "Diabetes",
    "Hormone",
    "Other",
}

SYSTEM_PROMPT = """You are a medical data extraction assistant. Extract every lab test result from the lab report text provided.

Return ONLY a valid JSON array. Each element must have these exact fields:
- test_name: string — full name of the test (e.g. "Hemoglobin", "Total Cholesterol")
- value: string — the result value as text (e.g. "12.5", "Positive", "Borderline")
- unit: string or null — measurement unit (e.g. "g/dL", "%", "mg/dL", null if none)
- reference_range_low: number or null — lower bound of normal range (null if not numeric or not present)
- reference_range_high: number or null — upper bound of normal range (null if not numeric or not present)
- date: string or null — test date in YYYY-MM-DD format, null if not found
- lab_source: string or null — name of the lab/facility, null if not found
- category: string — one of: "Complete Blood Count", "Lipid Panel", "Metabolic Panel", "Thyroid Function", "Liver Function", "Kidney Function", "Vitamin", "Diabetes", "Hormone", "Other"
- confidence: integer 0-100 — how confident you are in this extraction

Return only the JSON array, no explanation, no markdown fences."""


class LabResult(BaseModel):
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range_low: Optional[float] = None
    reference_range_high: Optional[float] = None
    date: Optional[str] = None
    lab_source: Optional[str] = None
    category: str = "Other"
    confidence: int = 50

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        return v if v in VALID_CATEGORIES else "Other"

    @field_validator("confidence")
    @classmethod
    def clamp_confidence(cls, v: int) -> int:
        return max(0, min(100, v))


def extract_lab_results(cleaned_text: str) -> list[dict]:
    """Call Claude Sonnet to extract structured lab results from cleaned OCR text."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": cleaned_text}],
    )

    raw = message.content[0].text.strip()

    # Strip markdown fences if Claude included them anyway
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    results = json.loads(raw)

    validated = []
    for item in results:
        try:
            lab_result = LabResult(**item)
            validated.append(lab_result.model_dump())
        except Exception:
            # Skip items that fail validation entirely
            continue

    return validated
