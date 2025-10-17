"""
GuidePoint Model Client Package
Client libraries for interacting with james-mlops models
"""

from .james_mlops_client import (
    JamesMLOpsClient,
    VulnerabilityContext,
    FixApproach,
    PredictionResult,
    ExecutionResult,
    get_fix_confidence,
    report_fix_outcome
)

__all__ = [
    "JamesMLOpsClient",
    "VulnerabilityContext",
    "FixApproach",
    "PredictionResult",
    "ExecutionResult",
    "get_fix_confidence",
    "report_fix_outcome"
]