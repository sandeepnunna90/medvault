from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import uuid

from backend.pdf_parser import extract_text_from_pdf
from backend.ocr_service import image_to_text
from backend.pii_stripper import strip_pii
from backend.extraction import extract_lab_results

load_dotenv()

router = APIRouter(prefix="/reports", tags=["reports"])
security = HTTPBearer()

ALLOWED_TYPES = {"application/pdf", "image/jpeg", "image/png"}


def get_supabase() -> Client:
    return create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_ROLE_KEY"],
    )


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Verify Supabase JWT and return the user_id."""
    supabase = get_supabase()
    try:
        user_response = supabase.auth.get_user(credentials.credentials)
        return str(user_response.user.id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


@router.post("/upload")
async def upload_report(
    file: UploadFile = File(...),
    user_id: str = Depends(verify_token),
):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: PDF, JPG, PNG",
        )

    file_bytes = await file.read()
    supabase = get_supabase()

    # Determine file extension
    ext_map = {
        "application/pdf": "pdf",
        "image/jpeg": "jpg",
        "image/png": "png",
    }
    ext = ext_map[file.content_type]
    unique_name = f"{uuid.uuid4()}.{ext}"
    storage_path = f"{user_id}/{unique_name}"

    # 1. Upload to Supabase Storage
    supabase.storage.from_("reports").upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": file.content_type},
    )

    # 2. Insert a pending row in the reports table
    row = (
        supabase.table("reports")
        .insert({
            "user_id": user_id,
            "storage_path": storage_path,
            "file_name": file.filename,
            "file_type": ext,
            "status": "processing",
        })
        .execute()
    )
    report_id = row.data[0]["id"]

    # 3. Extract text
    try:
        if file.content_type == "application/pdf":
            ocr_text = extract_text_from_pdf(file_bytes)
        else:
            ocr_text = image_to_text(file_bytes)

        cleaned_text = strip_pii(ocr_text)

        # 4. Claude extraction
        extracted_tests = extract_lab_results(cleaned_text)

        # 5. Update report row with OCR results
        supabase.table("reports").update({
            "ocr_text": ocr_text,
            "cleaned_text": cleaned_text,
            "status": "done",
        }).eq("id", report_id).execute()

        # 6. Insert extracted lab results
        if extracted_tests:
            rows = [
                {**test, "report_id": report_id, "user_id": user_id}
                for test in extracted_tests
            ]
            supabase.table("lab_results").insert(rows).execute()

    except Exception as e:
        supabase.table("reports").update({
            "status": "error",
            "error_message": str(e),
        }).eq("id", report_id).execute()
        raise HTTPException(status_code=500, detail=f"Processing failed: {e}")

    return {
        "report_id": report_id,
        "file_name": file.filename,
        "ocr_text": ocr_text,
        "cleaned_text": cleaned_text,
        "extracted_tests": extracted_tests,
        "status": "done",
    }
