"""
KNUST student ID card verification via OCR.

Requires: opencv-python-headless, pytesseract, Pillow
System:   tesseract OCR (macOS: brew install tesseract)

Limitations:
- OCR accuracy depends on photo quality, glare, blur, and angle.
- White text on blue backgrounds is preprocessed (invert, blue-mask) but remains
  harder to read than black-on-white text.
- University name is NOT validated (removed — unreliable on KNUST cards).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher


@dataclass
class IDVerificationResult:
    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ocr_text: str = ""
    matched_fields: dict = field(default_factory=dict)


STUDENT_PATTERNS = [
    r"\bstudent\b",
    r"student\s*id",
    r"id\s*card",
    r"\bundergraduate\b",
    r"\bpostgraduate\b",
]


def _normalize(text: str) -> str:
    text = text.lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def _load_image(image_file):
    import cv2
    import numpy as np
    from PIL import Image

    if hasattr(image_file, "read"):
        image_file.seek(0)
        data = image_file.read()
        image_file.seek(0)
        arr = np.frombuffer(data, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    else:
        img = cv2.imread(str(image_file))
    if img is None:
        pil = Image.open(image_file)
        img = cv2.cvtColor(np.array(pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    return img


def _ocr_variants(img) -> list:
    """
    Build preprocessing variants optimised for KNUST cards (white text on blue header).
    """
    import cv2

    variants = []
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Standard adaptive threshold
    blurred = cv2.bilateralFilter(gray, 9, 75, 75)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    variants.append(thresh)

    # Inverted grayscale — white-on-blue becomes dark-on-light (best for header text)
    inverted = cv2.bitwise_not(gray)
    variants.append(inverted)
    inv_thresh = cv2.adaptiveThreshold(
        inverted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 11
    )
    variants.append(inv_thresh)

    # CLAHE contrast boost then invert
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    variants.append(cv2.bitwise_not(enhanced))

    # Blue-background mask: isolate blue regions, invert to highlight white text
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_blue = (90, 40, 40)
    upper_blue = (130, 255, 255)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    blue_region = cv2.bitwise_and(gray, gray, mask=blue_mask)
    if cv2.countNonZero(blue_mask) > 100:
        variants.append(cv2.bitwise_not(blue_region))

    # Top third of card (university header area) — inverted
    h = img.shape[0]
    top = gray[0 : max(h // 3, 1), :]
    if top.size > 0:
        top_inv = cv2.bitwise_not(top)
        variants.append(top_inv)

    # Original colour (fallback)
    variants.append(gray)

    return variants


def _extract_text(image_file) -> str:
    import pytesseract

    img = _load_image(image_file)
    seen_lines: set[str] = set()
    combined: list[str] = []

    for variant in _ocr_variants(img):
        try:
            text = pytesseract.image_to_string(variant)
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if line and line not in seen_lines:
                seen_lines.add(line)
                combined.append(line)

    return "\n".join(combined)


def _check_student_label(text: str) -> bool:
    normalized = _normalize(text)
    for pattern in STUDENT_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
    return False


def _extract_id_numbers(text: str) -> list[str]:
    candidates = re.findall(r"\b\d{6,12}\b", text.replace("-", " ").replace("/", " "))
    return list(dict.fromkeys(candidates))


STAFF_PATTERNS = [
    r"\bstaff\b",
    r"staff\s*id",
    r"staffid",
]


def _check_staff_label(text: str) -> bool:
    normalized = _normalize(text)
    for pattern in STAFF_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
    return False


def _id_number_matches(ocr_text: str, entered_id: str) -> bool:
    entered = re.sub(r"[\s\-/]", "", entered_id.strip())
    if not entered:
        return False
    ocr_flat = re.sub(r"[\s\-/]", "", ocr_text)
    if entered in ocr_flat:
        return True
    for candidate in _extract_id_numbers(ocr_text):
        if entered == candidate or entered.endswith(candidate) or candidate.endswith(entered):
            return True
        if len(entered) >= 6 and len(candidate) >= 6:
            if _ratio(entered, candidate) >= 0.85:
                return True
    return False


def _token_found(normalized: str, name_part: str) -> bool:
    part = _normalize(name_part)
    if not part or len(part) < 2:
        return False
    if part in normalized:
        return True
    for token in normalized.split():
        if len(token) >= 3 and _ratio(token, part) >= 0.75:
            return True
    return False


def _name_matches(ocr_text: str, first_name: str, last_name: str) -> bool:
    normalized = _normalize(ocr_text)
    parts = [p for p in [first_name, last_name] if p and p.strip()]
    if not parts:
        return False
    matched = sum(1 for p in parts if _token_found(normalized, p))
    return matched >= len(parts) or (len(parts) >= 2 and matched >= 1 and _token_found(normalized, last_name))


def _programme_matches(ocr_text: str, programme: str, threshold: float = 0.42) -> bool:
    if not programme.strip():
        return False
    normalized = _normalize(ocr_text)
    prog = _normalize(programme)
    if prog in normalized:
        return True
    words = [w for w in prog.split() if len(w) > 2]
    if len(words) >= 2 and sum(1 for w in words if w in normalized) >= max(1, len(words) - 1):
        return True
    if _ratio(normalized, prog) >= threshold:
        return True
    chunk_size = max(len(prog) + 10, 20)
    for i in range(0, max(len(normalized) - chunk_size + 1, 1), 4):
        chunk = normalized[i : i + chunk_size]
        if _ratio(chunk, prog) >= threshold:
            return True
    return False


def verify_knust_student_id(
    image_file,
    *,
    student_id_number: str,
    first_name: str,
    last_name: str,
    programme: str,
) -> IDVerificationResult:
    result = IDVerificationResult(is_valid=False)

    try:
        import cv2  # noqa: F401
        import pytesseract  # noqa: F401
    except ImportError:
        result.errors.append(
            "ID verification libraries not installed. Run: pip install opencv-python-headless pytesseract"
        )
        return result

    try:
        ocr_text = _extract_text(image_file)
    except pytesseract.TesseractNotFoundError:
        result.errors.append(
            "Tesseract OCR is not installed on this system. Install it (e.g. brew install tesseract)."
        )
        return result
    except Exception as exc:
        result.errors.append(f"Could not read ID image: {exc}")
        return result

    result.ocr_text = ocr_text

    if not ocr_text.strip():
        result.errors.append(
            "No text could be extracted from the ID image. Try a clearer photo with good lighting."
        )
        return result

    if not _check_student_label(ocr_text):
        result.warnings.append('Could not clearly read a "Student" label — continuing other checks.')

    if not _id_number_matches(ocr_text, student_id_number):
        result.errors.append(
            f"Student number '{student_id_number}' does not appear to match the ID card."
        )
    else:
        result.matched_fields["student_id"] = student_id_number

    if not _name_matches(ocr_text, first_name, last_name):
        result.errors.append(
            f"Name '{first_name} {last_name}' does not appear to match the ID card."
        )
    else:
        result.matched_fields["name"] = f"{first_name} {last_name}".strip()

    if not _programme_matches(ocr_text, programme):
        result.errors.append(
            f"Programme '{programme}' does not appear to match the ID card."
        )
    else:
        result.matched_fields["programme"] = programme

    result.is_valid = len(result.errors) == 0
    return result


def verify_knust_staff_id(
    image_file,
    *,
    staff_id_number: str,
    first_name: str,
    last_name: str,
    department: str,
) -> IDVerificationResult:
    result = IDVerificationResult(is_valid=False)

    try:
        import cv2  # noqa: F401
        import pytesseract  # noqa: F401
    except ImportError:
        result.errors.append(
            "ID verification libraries not installed. Run: pip install opencv-python-headless pytesseract"
        )
        return result

    try:
        ocr_text = _extract_text(image_file)
    except pytesseract.TesseractNotFoundError:
        result.errors.append(
            "Tesseract OCR is not installed on this system. Install it (e.g. brew install tesseract)."
        )
        return result
    except Exception as exc:
        result.errors.append(f"Could not read ID image: {exc}")
        return result

    result.ocr_text = ocr_text

    if not ocr_text.strip():
        result.errors.append(
            "No text could be extracted from the ID image. Try a clearer photo with good lighting."
        )
        return result

    has_staff = re.search(r"\bstaff\b", _normalize(ocr_text))
    has_staff_id = re.search(r"staff\s*id|staffid", _normalize(ocr_text))

    if not has_staff:
        result.warnings.append('Could not clearly read a "Staff" label — continuing other checks.')
    else:
        result.matched_fields["staff_label"] = "staff"

    if not has_staff_id:
        result.warnings.append('Could not clearly read a "Staff ID" label — continuing other checks.')
    else:
        result.matched_fields["staff_id_label"] = "staff_id"

    if not _id_number_matches(ocr_text, staff_id_number):
        result.errors.append(
            f"Staff ID number '{staff_id_number}' does not appear to match the ID card."
        )
    else:
        result.matched_fields["staff_id"] = staff_id_number

    if not _name_matches(ocr_text, first_name, last_name):
        result.errors.append(
            f"Name '{first_name} {last_name}' does not appear to match the ID card."
        )
    else:
        result.matched_fields["name"] = f"{first_name} {last_name}".strip()

    if department.strip() and not _programme_matches(ocr_text, department):
        result.errors.append(
            f"Department '{department}' does not appear to match the ID card."
        )
    elif department.strip():
        result.matched_fields["department"] = department

    result.is_valid = len(result.errors) == 0
    return result
