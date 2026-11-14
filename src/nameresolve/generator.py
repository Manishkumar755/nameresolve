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