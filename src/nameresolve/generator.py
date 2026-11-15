"""Synthetic name-variant generator. All names are invented; no real records."""

from __future__ import annotations

import random
from collections import defaultdict
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

def _typo(name: str, rng: random.Random) -> str:
    """Replace one randomly chosen letter with a random character from TYPO_CHARS.

    Only alphabetic characters are candidates, so spaces are never touched.
    Assumes `name` contains at least one letter.
    """
    positions = [i for i, c in enumerate(name) if c.isalpha()]
    index = rng.choice(positions)
    replacement = rng.choice(TYPO_CHARS)
    return name[:index] + replacement + name[index + 1:]

def variants(first: str, last: str, rng: random.Random) -> list[tuple[str, str]]:
    """Return (transform_tag, variant_name) pairs for one entity.

    Always produces reorder, initial, honorific, and typo variants.
    Adds vowel or consonant variants only when a rule matches the name.
    """
    full = f"{first} {last}"
    out: list[tuple[str, str]] = [
        ("reorder", f"{last} {first}"),
        ("initial", f"{first[0]}. {last}"),
        ("honorific", f"Mr {full}"),
        ("typo", _typo(full, rng)),
    ]
    for label, pairs in (("vowel", VOWEL_SWAPS), ("consonant", CONSONANT_SWAPS)):
        swapped = _swap(full, pairs, rng)
        if swapped is not None:
            out.append((label, swapped))
    return out

def generate(n_entities: int = 200, seed: int = 42) -> list[Record]:
    """Build the full record list: one canonical name plus variants per entity."""
    rng = random.Random(seed)

    combos = [(f, l) for f in FIRST_NAMES for l in LAST_NAMES]
    if n_entities > len(combos):
        raise ValueError(f"need at most {len(combos)} entities; add more names")
    rng.shuffle(combos)

    records: list[Record] = []
    record_id = 0
    for entity_id, (first, last) in enumerate(combos[:n_entities]):
        records.append(Record(record_id, entity_id, f"{first} {last}", "canonical"))
        record_id += 1
        for transform, text in variants(first, last, rng):
            records.append(Record(record_id, entity_id, text, transform))
            record_id += 1
    return records

def make_pairs(
    records: list[Record], rng: random.Random, neg_per_pos: int = 2
) -> list[tuple[Record, Record, int]]:
    """Build labeled pairs: 1 for same entity, 0 for different entities."""
    by_entity: dict[int, list[Record]] = defaultdict(list)
    token_index: dict[str, list[Record]] = defaultdict(list)
    for r in records:
        by_entity[r.entity_id].append(r)
        for tok in r.name.lower().split():
            token_index[tok].append(r)

    # Positives: every pair inside the same entity.
    positives: list[tuple[Record, Record, int]] = []
    for recs in by_entity.values():
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                positives.append((recs[i], recs[j], 1))

    # Negatives: for each anchor, alternate hard (shared word) and random picks.
    negatives: list[tuple[Record, Record, int]] = []
    for a, _, _ in positives:
        for k in range(neg_per_pos):
            tok = rng.choice(a.name.lower().split())
            pool = token_index[tok] if k % 2 == 0 else records
            b = rng.choice(pool)
            if b.entity_id != a.entity_id:
                negatives.append((a, b, 0))

    return positives + negatives

    