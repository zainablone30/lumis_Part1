"""Keyword + pattern-based crisis detection (O6 safety safeguard)."""
import re

CRISIS_PATTERNS = [
    r"\bkill myself\b", r"\bend my life\b", r"\bsuicide\b", r"\bsuicidal\b",
    r"\bwant to die\b", r"\bno reason to live\b", r"\bself.?harm\b",
    r"\bhurt myself\b", r"\bcan'?t go on\b", r"\bbetter off dead\b",
]

HELPLINE_MESSAGE = (
    "WARNING: If you are in crisis or thinking about harming yourself, please reach out "
    "right now:\n"
    "Pakistan: Umang Helpline 0311-7786264 | Befrienders Karachi 021-34971882\n"
    "International: findahelpline.com\n"
    "You deserve support, and you don't have to go through this alone."
)


class CrisisDetector:
    def __init__(self):
        self.patterns = [re.compile(p, re.IGNORECASE) for p in CRISIS_PATTERNS]

    def check(self, text: str) -> bool:
        return any(p.search(text) for p in self.patterns)

    def get_response_prefix(self) -> str:
        return HELPLINE_MESSAGE
