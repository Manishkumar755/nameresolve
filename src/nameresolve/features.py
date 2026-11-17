"""Pair features. Order of FEATURE_NAMES matches the order of the returned vector."""

from __future__ import annotations

import jellyfish
from rapidfuzz import fuzz
from rapidfuzz.distance import JaroWinkler, Levenshtein

from nameresolve.normalize import normalize

FEATURE_NAMES = [
    "jaro_winkler",
    "levenshtein_sim",
    "token_sort",
    "token_set",
    "trigram_jaccard",
    "metaphone_eq",
    "first_initial_eq",
    "last_token_eq",
    "same_tokens",
    "len_diff",
    "token_count_diff",
]


def _trigrams(s: str) -> set[str]:
    padded = f" {s} "
    return {padded[i : i + 3] for i in range(len(padded) - 2)}


def _jaccard(a: str, b: str) -> float:
    A, B = _trigrams(a), _trigrams(b)
    return len(A & B) / len(A | B) if (A or B) else 0.0


def pair_features(x: str, y: str) -> list[float]:
    nx, ny = normalize(x), normalize(y)
    tx, ty = nx.split(), ny.split()
    if not tx or not ty:
        return [0.0] * len(FEATURE_NAMES)

    return [
        JaroWinkler.normalized_similarity(nx, ny),
        Levenshtein.normalized_similarity(nx, ny),
        fuzz.token_sort_ratio(nx, ny) / 100,
        fuzz.token_set_ratio(nx, ny) / 100,
        _jaccard(nx, ny),
        float(jellyfish.metaphone(nx.replace(" ", "")) == jellyfish.metaphone(ny.replace(" ", ""))),
        float(tx[0][0] == ty[0][0]),
        float(tx[-1] == ty[-1]),
        float(sorted(tx) == sorted(ty)),
        float(abs(len(nx) - len(ny))),
        float(abs(len(tx) - len(ty))),
    ]