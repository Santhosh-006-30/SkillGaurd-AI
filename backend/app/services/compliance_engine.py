"""
Compliance Scoring Engine — Phase 13
Weighted composite scoring: 40% attendance, 40% infrastructure, 10% activity, 10% consistency.
Thresholds are configurable demonstration parameters, NOT official MSDE policy.
[SIMULATED DEMO DATA]
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass

WEIGHT_ATTENDANCE = 0.40
WEIGHT_INFRASTRUCTURE = 0.40
WEIGHT_ACTIVITY = 0.10
WEIGHT_CONSISTENCY = 0.10

@dataclass
class ComplianceEngineResult:
    attendance_score: float
    infrastructure_score: float
    activity_score: float
    consistency_score: float
    overall_score: float
    risk_level: str
    breakdown: Dict[str, Any]
    recommendations: list

def compute_composite_score(
    attendance_score: float,
    infrastructure_score: float,
    activity_score: float = 90.0,
    consistency_score: float = 90.0
) -> ComplianceEngineResult:
    """
    Compute the weighted composite compliance index.
    Formula: 0.40 × Att + 0.40 × Infra + 0.10 × Activity + 0.10 × Consistency
    """
    overall = round(
        (WEIGHT_ATTENDANCE * attendance_score) +
        (WEIGHT_INFRASTRUCTURE * infrastructure_score) +
        (WEIGHT_ACTIVITY * activity_score) +
        (WEIGHT_CONSISTENCY * consistency_score),
        1
    )

    if overall >= 80.0:
        risk = "LOW"
    elif overall >= 60.0:
        risk = "MEDIUM"
    elif overall >= 40.0:
        risk = "HIGH"
    else:
        risk = "CRITICAL"

    recommendations = []
    if attendance_score < 70.0:
        recommendations.append("Schedule immediate attendance audit — estimated presence significantly below declared count.")
    if infrastructure_score < 70.0:
        recommendations.append("Infrastructure inventory below minimum standards — conduct physical asset verification.")
    if activity_score < 70.0:
        recommendations.append("Equipment operational status uncertain — technical inspection recommended.")
    if consistency_score < 70.0:
        recommendations.append("Data inconsistency detected across reporting windows — cross-validate with physical records.")
    if not recommendations:
        recommendations.append("All compliance indicators within acceptable thresholds. Continue routine monitoring.")

    return ComplianceEngineResult(
        attendance_score=round(attendance_score, 1),
        infrastructure_score=round(infrastructure_score, 1),
        activity_score=round(activity_score, 1),
        consistency_score=round(consistency_score, 1),
        overall_score=overall,
        risk_level=risk,
        breakdown={
            "attendance_weight": f"{int(WEIGHT_ATTENDANCE * 100)}%",
            "infrastructure_weight": f"{int(WEIGHT_INFRASTRUCTURE * 100)}%",
            "activity_weight": f"{int(WEIGHT_ACTIVITY * 100)}%",
            "consistency_weight": f"{int(WEIGHT_CONSISTENCY * 100)}%",
            "weighted_attendance": round(WEIGHT_ATTENDANCE * attendance_score, 1),
            "weighted_infrastructure": round(WEIGHT_INFRASTRUCTURE * infrastructure_score, 1),
            "weighted_activity": round(WEIGHT_ACTIVITY * activity_score, 1),
            "weighted_consistency": round(WEIGHT_CONSISTENCY * consistency_score, 1),
        },
        recommendations=recommendations
    )


def compute_infrastructure_score(
    detected_counts: Dict[str, int],
    sanctioned_counts: Dict[str, int],
    minimum_required: Dict[str, int]
) -> float:
    """
    Calculate infrastructure compliance as % of minimum required assets detected.
    """
    total_required = sum(minimum_required.values())
    if total_required == 0:
        return 100.0

    compliant_items = 0
    for item_type, required in minimum_required.items():
        detected = detected_counts.get(item_type, 0)
        compliant_items += min(detected, required)

    score = (compliant_items / max(1, total_required)) * 100.0
    return round(min(100.0, score), 1)
