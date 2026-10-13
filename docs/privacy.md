# Privacy Architecture & Safeguards — SkillGuard AI

## 1. Core Principles
SkillGuard AI strictly adheres to privacy-by-design principles to ensure that training centre oversight never compromises trainee or staff privacy.

| Feature | System Status | Justification |
| :--- | :--- | :--- |
| **Facial Recognition** | **DISABLED / NON-EXISTENT** | No biometric templates or identity matching. |
| **Face Identification** | **DISABLED** | Identity is never extracted or queried. |
| **Biometric Database** | **NONE** | No biometric vectors or facial embeddings stored. |
| **Individual Person ID** | **ANONYMOUS** | Tracks use temporary numeric IDs within a single session. |
| **Aggregate Presence** | **ENABLED** | Only count, density, and zone statistics are generated. |
| **Edge Processing** | **SUPPORTED** | Metadata transmitted without uploading continuous raw video. |
| **Raw Video Retention** | **CONFIGURABLE** | Stream frames are discarded post-inference. |

## 2. Terminology Standards
- **Estimated Physical Presence**: The count of individuals anonymously detected within camera zones.
- **Attendance Discrepancy**: Difference between submitted attendance records and estimated presence.
- **Apparent Activity / Operability**: Spatial and temporal interaction observed between individuals and equipment. Does not claim mechanical or electrical verification.
