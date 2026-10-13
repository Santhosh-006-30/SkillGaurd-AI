"""
Attendance Reconciliation Service — Phase 9
Computes discrepancy between AI-estimated physical presence and centre-submitted headcounts.
Conservative terminology: "Estimated Physical Presence" (not verified identity).
[SIMULATED DEMO — Thresholds are configurable demonstration parameters, not official MSDE policy]
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ReconciliationResult:
    estimated_presence: int
    submitted_count: int
    discrepancy: int
    discrepancy_percentage: float
    category: str  # NORMAL | REVIEW | HIGH_DISCREPANCY | CRITICAL
    attendance_score: float
    action_required: bool
    narrative: str

def classify_discrepancy(estimated: int, submitted: int) -> ReconciliationResult:
    """
    Classify attendance discrepancy across three time-window categories per SIH PS 26245.
    
    Classification thresholds (configurable):
      0–10%   → NORMAL       (within noise tolerance)
      10–20%  → REVIEW       (flag for secondary inspection)
      >20%    → HIGH         (strong intervention trigger)
      >40%    → CRITICAL     (likely ghost attendance or centre non-compliance)
    """
    discrepancy = abs(submitted - estimated)
    pct = (discrepancy / max(1, submitted)) * 100.0
    pct_rounded = round(pct, 1)

    if pct_rounded <= 10.0:
        category = "NORMAL"
        score = max(90.0, 100.0 - pct_rounded)
        action_required = False
        narrative = (
            f"Estimated physical presence ({estimated}) is consistent with the submitted headcount "
            f"({submitted}). Discrepancy of {discrepancy} ({pct_rounded}%) is within normal tolerance."
        )
    elif pct_rounded <= 20.0:
        category = "REVIEW"
        score = max(60.0, 100.0 - (pct_rounded * 2.0))
        action_required = True
        narrative = (
            f"Moderate discrepancy detected: estimated presence ({estimated}) vs submitted ({submitted}). "
            f"Difference of {discrepancy} ({pct_rounded}%) warrants secondary inspection review."
        )
    elif pct_rounded <= 40.0:
        category = "HIGH_DISCREPANCY"
        score = max(30.0, 100.0 - (pct_rounded * 2.5))
        action_required = True
        narrative = (
            f"High discrepancy: estimated presence ({estimated}) diverges substantially from submitted "
            f"headcount ({submitted}) by {discrepancy} trainees ({pct_rounded}%). Compliance intervention required."
        )
    else:
        category = "CRITICAL"
        score = max(10.0, 100.0 - (pct_rounded * 3.0))
        action_required = True
        narrative = (
            f"Critical discrepancy ({pct_rounded}%): Estimated physical presence of only {estimated} "
            f"against submitted attendance of {submitted}. Potential ghost-attendance pattern. "
            f"Immediate investigation recommended. [SIMULATED DEMO SCENARIO]"
        )

    return ReconciliationResult(
        estimated_presence=estimated,
        submitted_count=submitted,
        discrepancy=discrepancy,
        discrepancy_percentage=pct_rounded,
        category=category,
        attendance_score=round(score, 1),
        action_required=action_required,
        narrative=narrative
    )
