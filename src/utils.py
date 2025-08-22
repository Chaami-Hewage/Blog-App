import os
import re
from typing import Literal

from langdetect import detect


def detect_lang_code(text: str) -> Literal["en", "si"]:
    try:
        code = detect(text)
    except Exception:
        code = "en"
    if code == "si":
        return "si"
    # Sinhala Unicode range heuristic
    if re.search(r"[\u0D80-\u0DFF]", text):
        return "si"
    return "en"


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)