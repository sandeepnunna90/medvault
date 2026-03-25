import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

st.set_page_config(page_title="Upload Report", page_icon="📄")

# Guard: must be logged in
if not st.session_state.get("user") or not st.session_state.get("access_token"):
    st.warning("Please log in first.")
    st.stop()

st.title("Upload Lab Report")
st.caption("Supported formats: PDF, JPG, PNG — max 10 MB")

st.info(
    "**Privacy notice:** Your file is stored securely in your private folder. "
    "Personal identifiers (SSN, DOB, phone, email) are automatically removed "
    "before any AI processing."
)

uploaded_file = st.file_uploader(
    "Choose a file",
    type=["pdf", "jpg", "jpeg", "png"],
    help="Upload a lab report PDF or photo",
)

if uploaded_file is not None:
    st.write(f"**File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")

    if st.button("Extract Text", type="primary"):
        with st.spinner("Uploading and extracting text — this may take up to 60 seconds..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}/reports/upload",
                    headers={"Authorization": f"Bearer {st.session_state.access_token}"},
                    files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()

                st.success("Extraction complete!")

                st.subheader("Raw OCR Text")
                st.text_area(
                    label="Raw text (before PII removal)",
                    value=data.get("ocr_text", ""),
                    height=300,
                    disabled=True,
                )

                st.subheader("Cleaned Text (PII Removed)")
                st.text_area(
                    label="Cleaned text",
                    value=data.get("cleaned_text", ""),
                    height=300,
                    disabled=True,
                )

            except requests.exceptions.Timeout:
                st.error("Request timed out. The file may be too large or the server is cold-starting. Try again in 60 seconds.")
            except requests.exceptions.HTTPError as e:
                detail = e.response.json().get("detail", str(e)) if e.response else str(e)
                st.error(f"Upload failed: {detail}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")
