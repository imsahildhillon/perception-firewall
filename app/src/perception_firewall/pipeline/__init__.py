"""Session lifecycle and end-to-end pipeline orchestration.

Public entry points: ``Session`` (lifecycle + transcript state for one
monitoring session) and ``ApplicationPipeline`` (connects the existing
interfaces/mocks/prefilter/fusion/risk components end-to-end). See
README.md in this directory for the full design.
"""

from perception_firewall.pipeline.orchestrator import ApplicationPipeline
from perception_firewall.pipeline.session import Session

__all__ = [
    "ApplicationPipeline",
    "Session",
]
