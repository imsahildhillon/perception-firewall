"""Transcript state management.

Public entry point: ``TranscriptBuffer``. See README.md in this directory
for its responsibility boundary.
"""

from perception_firewall.transcript.buffer import DEFAULT_SEPARATOR, TranscriptBuffer

__all__ = [
    "DEFAULT_SEPARATOR",
    "TranscriptBuffer",
]
