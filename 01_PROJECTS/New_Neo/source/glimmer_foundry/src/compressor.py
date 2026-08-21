"""Graphical engineering filter + Caveman compressor — token savers only."""

from __future__ import annotations

import re


FILLERS = [
    r"\bplease\b",
    r"\bcould you\b",
    r"\bwould you mind\b",
    r"\bkindly\b",
    r"\bi would like you to\b",
    r"\bif you can\b",
    r"\bthanks in advance\b",
    r"\bthank you\b",
]


def graphical_filter(prompt: str) -> str:
    """
    Stage 1–2 token reduction (~30–40% on chatty prompts).
    Clean whitespace → strip polite fillers → collapse spaces.
    """
    cleaned = prompt.strip()
    for pattern in FILLERS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def caveman_compress(prompt: str, max_chars: int = 400) -> str:
    """
    Aggressive reduction (~50–60%). Keeps verbs, numbers, core nouns.
    Used only when the graphical filter is still too long.
    """
    text = graphical_filter(prompt)
    # Drop most articles and filler conjunctions
    text = re.sub(r"\b(the|a|an|and|or|but|that|which|who|whom)\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"[ \t]+", " ", text).strip()
    if len(text) > max_chars:
        text = text[:max_chars].rsplit(" ", 1)[0] + "…"
    return text


def compress_prompt(prompt: str, aggressive: bool = False) -> str:
    """Public entry point used by the training loop."""
    if aggressive:
        return caveman_compress(prompt)
    return graphical_filter(prompt)
