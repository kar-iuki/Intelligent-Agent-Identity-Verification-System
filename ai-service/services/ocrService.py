import re
import difflib
from datetime import datetime

import easyocr
import torch

# Load once at import time — gpu only if CUDA is available
_gpu_available = torch.cuda.is_available()
reader = easyocr.Reader(['en'], gpu=_gpu_available)

CONFIDENCE_FILTER = 0.4
NAME_MATCH_THRESHOLD = 0.85
OVERALL_MATCH_THRESHOLD = 0.70

DATE_PATTERNS = [
    re.compile(r'\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b'),
    re.compile(
        r'\b(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{2,4})\b',
        re.IGNORECASE,
    ),
]

MONTH_MAP = {
    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
}

ID_PATTERN = re.compile(r'^[A-Za-z0-9][A-Za-z0-9\s/-]{5,}$')
NAME_STOPWORDS = {
    'republic', 'kenya', 'national', 'identity', 'card', 'passport',
    'driver', 'licence', 'license', 'sex', 'male', 'female', 'date',
    'birth', 'issue', 'expiry', 'expires', 'valid', 'signature',
    'holder', 'citizen', 'identification', 'number', 'id', 'dob',
}


def extract_text_from_document(image):
    """
    Run EasyOCR and return [{text, confidence}, ...] filtered below 0.4.
    """
    results = reader.readtext(image)
    extracted = []

    for item in results:
        # EasyOCR returns (bbox, text, confidence)
        if len(item) < 3:
            continue
        text = str(item[1]).strip()
        confidence = float(item[2])
        if text and confidence >= CONFIDENCE_FILTER:
            extracted.append({
                'text': text,
                'confidence': confidence,
            })

    return extracted


def _looks_like_name(text):
    words = text.split()
    if len(words) < 2:
        return False
    if any(ch.isdigit() for ch in text):
        return False
    lowered = [w.lower().strip('.,') for w in words]
    if any(w in NAME_STOPWORDS for w in lowered):
        return False
    return all(re.match(r"^[A-Za-z][A-Za-z'\-]*$", w) for w in words)


def _looks_like_id(text):
    cleaned = text.strip()
    if len(re.sub(r'[^A-Za-z0-9]', '', cleaned)) < 6:
        return False
    if not ID_PATTERN.match(cleaned):
        return False
    # Prefer strings that contain digits (ID numbers)
    return any(ch.isdigit() for ch in cleaned)


def _parse_date_string(text):
    text = text.strip()

    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if not match:
            continue
        groups = match.groups()
        try:
            if len(groups) == 3 and groups[1].isalpha():
                day = int(groups[0])
                month = MONTH_MAP[groups[1][:3].lower()]
                year = int(groups[2])
            else:
                day = int(groups[0])
                month = int(groups[1])
                year = int(groups[2])

            if year < 100:
                year += 1900 if year > 30 else 2000

            return datetime(year, month, day).date()
        except (ValueError, KeyError):
            continue

    return None


def parse_identity_details(text_results):
    """Extract name, idNumber, and dateOfBirth heuristics from OCR text."""
    texts = [item['text'] for item in text_results]

    name = None
    name_candidates = [t for t in texts if _looks_like_name(t)]
    if name_candidates:
        name = max(name_candidates, key=lambda t: (len(t.split()), len(t)))

    id_number = None
    id_candidates = [t for t in texts if _looks_like_id(t)]
    if id_candidates:
        # Prefer denser alphanumeric IDs
        id_number = max(
            id_candidates,
            key=lambda t: len(re.sub(r'[^A-Za-z0-9]', '', t)),
        )

    date_of_birth = None
    for text in texts:
        parsed = _parse_date_string(text)
        if parsed:
            date_of_birth = parsed.strftime('%d/%m/%Y')
            break

    return {
        'name': name,
        'idNumber': id_number,
        'dateOfBirth': date_of_birth,
    }


def _normalise_name(value):
    if not value:
        return ''
    return re.sub(r'\s+', ' ', value).strip().lower()


def _normalise_id(value):
    if not value:
        return ''
    return re.sub(r'[^A-Za-z0-9]', '', value).upper()


def _normalise_dob(value):
    if not value:
        return None
    parsed = _parse_date_string(str(value))
    if parsed:
        return parsed.isoformat()

    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(str(value).strip(), fmt).date().isoformat()
        except ValueError:
            continue
    return None


def compute_ocr_confidence(extracted, registered):
    """
    Compare extracted document fields with registered agent details.
    """
    extracted_name = extracted.get('name')
    extracted_id = extracted.get('idNumber')
    extracted_dob = extracted.get('dateOfBirth')

    registered_name = registered.get('name') or ''
    registered_id = registered.get('idNumber') or ''
    registered_dob = registered.get('dateOfBirth') or ''

    name_ratio = difflib.SequenceMatcher(
        None,
        _normalise_name(extracted_name),
        _normalise_name(registered_name),
    ).ratio() if extracted_name and registered_name else 0.0
    name_match = name_ratio >= NAME_MATCH_THRESHOLD

    id_match = (
        bool(extracted_id)
        and bool(registered_id)
        and _normalise_id(extracted_id) == _normalise_id(registered_id)
    )
    id_score = 1.0 if id_match else 0.0

    extracted_dob_norm = _normalise_dob(extracted_dob)
    registered_dob_norm = _normalise_dob(registered_dob)
    dob_match = (
        extracted_dob_norm is not None
        and registered_dob_norm is not None
        and extracted_dob_norm == registered_dob_norm
    )
    dob_score = 1.0 if dob_match else 0.0

    confidence_score = float((name_ratio + id_score + dob_score) / 3.0)

    return {
        'extractedName': extracted_name,
        'extractedIDNumber': extracted_id,
        'extractedDOB': extracted_dob,
        'nameMatch': bool(name_match),
        'idMatch': bool(id_match),
        'dobMatch': bool(dob_match),
        'confidenceScore': round(confidence_score, 4),
        'matched': confidence_score > OVERALL_MATCH_THRESHOLD,
    }


def assess_document_ocr(image, registered_details):
    """
    Full OCR pipeline: extract → parse → compare.
    Returns confidence result plus rawText list.
    """
    text_results = extract_text_from_document(image)
    raw_text = [item['text'] for item in text_results]

    if not text_results:
        return {
            'extractedName': None,
            'extractedIDNumber': None,
            'extractedDOB': None,
            'nameMatch': False,
            'idMatch': False,
            'dobMatch': False,
            'confidenceScore': 0.0,
            'matched': False,
            'rawText': [],
        }

    parsed = parse_identity_details(text_results)
    result = compute_ocr_confidence(parsed, registered_details)
    result['rawText'] = raw_text
    return result
