import re


SAFE_TEXT_PATTERN = re.compile(r"[^a-zA-Z0-9_.:\-\s/@]")


def sanitize_text(value: str | None, max_len: int = 255) -> str | None:
    if value is None:
        return None
    cleaned = SAFE_TEXT_PATTERN.sub("", value.strip())
    return cleaned[:max_len]
