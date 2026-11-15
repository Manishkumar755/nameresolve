"""Synthetic name-variant generator. All names are invented; no real records."""

from __future__ import annotations

import random
from dataclasses import dataclass

# Pool of invented first and last names.
# 20 first names x 15 last names = 300 unique combinations.
FIRST_NAMES = [
    "Mohammad", "Shreya", "Harpreet", "Vikram", "Anjali", "Rahul", "Fatima",
    "Ravi", "Sunita", "Imran", "Deepak", "Neha", "Vivek", "Zoya", "Arjun",
    "Kavita", "Sanjay", "Priya", "Faisal", "Divya",
]

LAST_NAMES = [
    "Singh", "Khan", "Sharma", "Verma", "Ahmed", "Gupta", "Kaur", "Malik",
    "Jaiswal", "Bhatia", "Chauhan", "Qureshi", "Yadav", "Mehta", "Dubey",
]


@dataclass(frozen=True)
class Record:
    """A single name record.

    Attributes:
        record_id: Unique identifier for this record.
        entity_id: Identifier of the real-world entity this record refers to.
        name: The name text.
        transform: "canonical" for the original name, or the name of the
            rule that produced this variant.
    """

    record_id: int
    entity_id: int
    name: str
    transform: str

# Spelling variations common in transliterated Indian names.
# Each tuple is (pattern_to_find, replacement).
VOWEL_SWAPS = [
    ("aa", "a"),
    ("a", "aa"),
    ("ee", "i"),
    ("i", "ee"),
    ("oo", "u"),
    ("u", "oo"),
]

CONSONANT_SWAPS = [
    ("v", "w"),
    ("w", "v"),
    ("j", "z"),
    ("z", "j"),
    ("ph", "f"),
    ("f", "ph"),
    ("sh", "s"),
    ("s", "sh"),
]

# Characters used when introducing a random typo.
TYPO_CHARS = "aeiounrstlm"    

def _swap(name: str, pairs: list[tuple[str, str]], rng: random.Random) -> str | None:
    """Apply one random spelling swap from `pairs` to `name`.

    Returns the modified name, or None if no pattern in `pairs` matches.
    The original casing outside the swapped part is preserved.
    """
    lowered = name.lower()

    # Keep only the rules whose source pattern appears in the name.
    options = [(src, dst) for src, dst in pairs if src in lowered]
    if not options:
        return None

    src, dst = rng.choice(options)

    # Replace the first occurrence only, so one swap is one change.
    index = lowered.index(src)
    return name[:index] + dst + name[index + len(src):]

    