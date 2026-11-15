"""Text normalization shared by data generation, features, and the API."""

from __future__ import annotations

import re
import unicodedata

HONORIFICS = frozenset({"mr", "mrs", "ms", "dr", "shri", "smt", "kumari"})

# Keep ASCII word characters, whitespace, and the Devanagari block (U+0900-U+097F).
_NON_NAME_CHARS = re.compile(r"[^\w\s\u0900-\u097F]")


def normalize(name: str) -> str:
    """Return a canonical form: NFKC, lowercase, no punctuation, no honorifics."""
    text = unicodedata.normalize("NFKC", name).lower()
    text = _NON_NAME_CHARS.sub(" ", text)
    tokens = [t for t in text.split() if t not in HONORIFICS]
    return " ".join(tokens)