"""Parse CSV rows into Question instances (not saved until caller commits)."""

from __future__ import annotations

import csv
import io

from apps.exams.models import Question


REQUIRED_HEADERS = {"type", "text", "correct", "marks"}


def _normalize_type(raw: str) -> str | None:
    value = raw.strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "mcq": Question.QuestionType.MCQ,
        "multiple_choice": Question.QuestionType.MCQ,
        "true_false": Question.QuestionType.TRUE_FALSE,
        "tf": Question.QuestionType.TRUE_FALSE,
        "short_answer": Question.QuestionType.SHORT_ANSWER,
        "short": Question.QuestionType.SHORT_ANSWER,
    }
    return aliases.get(value)


def _parse_mcq_options(row: dict) -> list[dict]:
    options = []
    for letter in ("a", "b", "c", "d", "e", "f"):
        key = f"option_{letter}"
        label = (row.get(key) or "").strip()
        if label:
            options.append({"key": letter.upper(), "label": label})
    return options


def _parse_row(row: dict, row_num: int) -> tuple[Question | None, str | None]:
    qtype = _normalize_type(row.get("type", ""))
    text = (row.get("text") or "").strip()
    correct = (row.get("correct") or "").strip()
    marks_raw = (row.get("marks") or "1").strip()
    explanation = (row.get("explanation") or "").strip()

    if not qtype:
        return None, f"Row {row_num}: invalid type '{row.get('type')}'."
    if not text:
        return None, f"Row {row_num}: question text is required."
    if not correct:
        return None, f"Row {row_num}: correct answer is required."

    try:
        marks = int(marks_raw)
        if marks < 1:
            raise ValueError
    except ValueError:
        return None, f"Row {row_num}: marks must be a positive integer."

    question = Question(
        text=text,
        question_type=qtype,
        marks=marks,
        explanation=explanation,
    )

    if qtype == Question.QuestionType.MCQ:
        options = _parse_mcq_options(row)
        if len(options) < 2:
            return None, f"Row {row_num}: MCQ needs at least two options (option_a, option_b, …)."
        valid_keys = {opt["key"] for opt in options}
        correct_key = correct.upper()
        if correct_key not in valid_keys:
            by_label = {opt["label"].lower(): opt["key"] for opt in options}
            if correct.lower() in by_label:
                correct_key = by_label[correct.lower()]
            else:
                return None, f"Row {row_num}: correct '{correct}' does not match any option key."
        question.options = options
        question.correct_answer = {"value": correct_key}
    elif qtype == Question.QuestionType.TRUE_FALSE:
        correct_val = correct.lower()
        if correct_val not in ("true", "false"):
            return None, f"Row {row_num}: true/false correct value must be 'true' or 'false'."
        question.options = [
            {"key": "true", "label": "True"},
            {"key": "false", "label": "False"},
        ]
        question.correct_answer = {"value": correct_val}
    else:
        question.options = []
        question.correct_answer = {"reference": correct}

    section = (row.get("section") or "").strip()
    if section:
        question.section = section

    difficulty = (row.get("difficulty") or "").strip().lower()
    if difficulty in {c.value for c in Question.Difficulty}:
        question.difficulty = difficulty

    blooms = (row.get("blooms_level") or row.get("blooms") or "").strip()
    if blooms:
        question.blooms_level = blooms

    tags_raw = (row.get("tags") or row.get("module_tags") or "").strip()
    if tags_raw:
        question.module_tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    return question, None


def import_questions_from_csv(bank, file_obj) -> tuple[int, list[str]]:
    """
    Import questions into bank from a CSV file.
    Returns (created_count, error_messages).
    """
    raw = file_obj.read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))
    if not reader.fieldnames:
        return 0, ["CSV file is empty or missing a header row."]

    headers = {h.strip().lower() for h in reader.fieldnames if h}
    missing = REQUIRED_HEADERS - headers
    if missing:
        return 0, [f"Missing required columns: {', '.join(sorted(missing))}."]

    created = 0
    errors: list[str] = []
    for row_num, row in enumerate(reader, start=2):
        normalized = {k.strip().lower(): (v or "") for k, v in row.items() if k}
        if not any(v.strip() for v in normalized.values() if v):
            continue
        question, err = _parse_row(normalized, row_num)
        if err:
            errors.append(err)
            continue
        question.question_bank = bank
        question.save()
        created += 1

    return created, errors
