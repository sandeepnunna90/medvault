import re

# Patterns to strip
_PATTERNS = [
    (r"\b\d{3}-\d{2}-\d{4}\b", "[SSN]"),                          # SSN
    (r"\b\d{3}/\d{2}/\d{4}\b", "[SSN]"),                          # SSN alt
    (r"\b(DOB|Date of Birth)\s*[:\-]?\s*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b", "[DOB]"),
    (r"\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b", "[DATE]"),           # generic dates
    (r"\b(\+1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}\b", "[PHONE]"),  # US phone
    (r"\b(\+?\d{1,3}[-.\s]?)?\d{10}\b", "[PHONE]"),               # 10-digit international phone
    (r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", "[EMAIL]"),
    (r"\b[A-Z]{1,3}\d{6,12}\b", "[INSURANCE_ID]"),                # insurance / member ID
    (r"\bMRN\s*[:\-]?\s*\d+\b", "[MRN]"),                         # medical record number
    (r"\bNPI\s*[:\-]?\s*\d{10}\b", "[NPI]"),                      # provider NPI
    (r"\bPID\s*[:\-]?\s*\d+\b", "[PID]"),                         # patient ID
    (r"\bAge\s*[:\-]?\s*\d+\s*(Years?|Yrs?|Months?|Mos?)?\b", "[AGE]"),  # age
    (r"\bSex\s*[:\-]?\s*(Male|Female|M|F)\b", "[SEX]"),           # sex/gender
]

_COMPILED = [(re.compile(pattern, re.IGNORECASE), replacement)
             for pattern, replacement in _PATTERNS]


def strip_pii(text: str) -> str:
    for pattern, replacement in _COMPILED:
        text = pattern.sub(replacement, text)
    return text
