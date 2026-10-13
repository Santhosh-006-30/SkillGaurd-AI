# Evaluation Methodology — SkillGuard AI

## 1. Measurable Performance Metrics
SkillGuard AI incorporates quantitative evaluation tools to assess false-positive and false-negative rates across:
1. **Person Detection & Occupancy Counting**
2. **Infrastructure & Equipment Detection**
3. **Attendance Discrepancy Classification**

## 2. Calculated Metrics
- **Precision**: `TP / (TP + FP)`
- **Recall**: `TP / (TP + FN)`
- **F1-Score**: `2 * (Precision * Recall) / (Precision + Recall)`
- **False Positive Rate (FPR)**: `FP / (FP + TN)`
- **False Negative Rate (FNR)**: `FN / (TP + FN)`
- **Confusion Matrix**: Full breakdown of TP, FP, TN, FN.

## 3. Transparency
Evaluation results are bound to dataset sample counts, evaluation timestamps, model versions, and confidence thresholds. Simulated demo data is explicitly flagged.
