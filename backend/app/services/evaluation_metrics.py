"""
AI Evaluation Metrics — Phase 15
Precision, Recall, F1, FPR, FNR for person detection and discrepancy classification.
Computed on a simulated benchmark ground-truth dataset (SIH PS 26245 mandate).
[SIMULATED DEMO DATA]
"""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class ConfusionMatrix:
    tp: int
    fp: int
    tn: int
    fn: int

    @property
    def precision(self) -> float:
        return self.tp / max(1, self.tp + self.fp)

    @property
    def recall(self) -> float:
        return self.tp / max(1, self.tp + self.fn)

    @property
    def f1_score(self) -> float:
        p = self.precision
        r = self.recall
        return (2 * p * r) / max(0.0001, p + r)

    @property
    def false_positive_rate(self) -> float:
        return self.fp / max(1, self.fp + self.tn)

    @property
    def false_negative_rate(self) -> float:
        return self.fn / max(1, self.fn + self.tp)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1_score": round(self.f1_score, 4),
            "false_positive_rate": round(self.false_positive_rate, 4),
            "false_negative_rate": round(self.false_negative_rate, 4),
            "tp": self.tp,
            "fp": self.fp,
            "tn": self.tn,
            "fn": self.fn,
        }


# Simulated benchmark dataset results (ground truth collected in controlled test environment)
# These are realistic but synthetic metrics for the SIH hackathon demo.
# [SIMULATED DEMO DATA — Not official MSDE-audited metrics]

SIMULATED_PERSON_DETECTION = ConfusionMatrix(tp=392, fp=18, tn=312, fn=28)
SIMULATED_EQUIPMENT_DETECTION = ConfusionMatrix(tp=284, fp=24, tn=198, fn=44)
SIMULATED_DISCREPANCY_CLASSIFICATION = ConfusionMatrix(tp=178, fp=12, tn=218, fn=22)


def get_full_evaluation_report(model_version: str = "YOLOv8n-SkillGuard-v1.0", dataset_samples: int = 450) -> Dict[str, Any]:
    """
    Returns the full AI model evaluation metrics for all three inference tasks.
    """
    return {
        "model_version": model_version,
        "dataset_samples": dataset_samples,
        "evaluation_dataset": "Simulated Benchmark Ground Truth v1.0 [DEMO]",
        "evaluation_note": (
            "Metrics computed on a controlled synthetic benchmark dataset. "
            "Real-world deployment accuracy may vary. "
            "These thresholds are configurable demo parameters, not certified MSDE performance guarantees."
        ),
        "person_detection": SIMULATED_PERSON_DETECTION.to_dict(),
        "equipment_detection": SIMULATED_EQUIPMENT_DETECTION.to_dict(),
        "discrepancy_classification": SIMULATED_DISCREPANCY_CLASSIFICATION.to_dict(),
        "overall_summary": {
            "mean_precision": round(
                (
                    SIMULATED_PERSON_DETECTION.precision +
                    SIMULATED_EQUIPMENT_DETECTION.precision +
                    SIMULATED_DISCREPANCY_CLASSIFICATION.precision
                ) / 3, 4
            ),
            "mean_recall": round(
                (
                    SIMULATED_PERSON_DETECTION.recall +
                    SIMULATED_EQUIPMENT_DETECTION.recall +
                    SIMULATED_DISCREPANCY_CLASSIFICATION.recall
                ) / 3, 4
            ),
            "mean_f1": round(
                (
                    SIMULATED_PERSON_DETECTION.f1_score +
                    SIMULATED_EQUIPMENT_DETECTION.f1_score +
                    SIMULATED_DISCREPANCY_CLASSIFICATION.f1_score
                ) / 3, 4
            ),
        }
    }
