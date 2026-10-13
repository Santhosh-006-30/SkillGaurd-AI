# SkillGuard AI — System Architecture

## 1. Overview
SkillGuard AI is an automated, privacy-first computer vision and compliance analytics platform designed for the Ministry of Skill Development and Entrepreneurship (MSDE) under SIH Problem Statement 26245.

> **SIMULATED DEMO DATA DISCLAIMER**:  
> All seeded centre, attendance, inventory, compliance and alert records are simulated demonstration data and are not official MSDE data.

---

## 2. Architecture Diagram

```
[Training Centre Cameras] (RTSP / Upload / Simulation)
            │
            ▼
┌────────────────────────────────────────────────────────┐
│                   Edge / Ingest Layer                  │
│  - Low-bandwidth frame sampling                        │
│  - Offline buffer queue (local SQLite / memory)        │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                   AI Inference Engine                  │
│  - Person Detection (YOLO, bounding box only)          │
│  - Anonymous Tracking (ByteTrack / short-lived IDs)    │
│  - Occupancy Estimator & Temporal Smoothing            │
│  - Infrastructure Detection (Pretrained / Custom YOLO) │
│  - Apparent Operability & Activity Analysis            │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              Compliance & Reconciliation Engine        │
│  - Attendance Reconciliation & Discrepancy %           │
│  - Infrastructure Inventory Comparison                 │
│  - Multi-window Temporal Persistence (1/5/15/30 min)   │
│  - Weighted Compliance Scoring (40/40/10/10)           │
│  - Risk Engine (LOW, MEDIUM, HIGH, CRITICAL)           │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Backend Core & Data Persistence            │
│  - FastAPI REST Endpoints                              │
│  - SQLAlchemy ORM (SQLite / PostgreSQL)                │
│  - Role-Based Access Control (RBAC)                    │
│  - Automated Evidence Frame Generation                 │
│  - PDF Report Generator                                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│                  Frontend SOC Dashboard                │
│  - Dark Theme Monitoring (React 18 + Vite + Tailwind)  │
│  - Real-Time Presence & Equipment Status               │
│  - Verification & Evidence Viewer                      │
│  - Auditing & Compliance Analytics                     │
└────────────────────────────────────────────────────────┘
```

---

## 3. Database Entity Relationship Model

```
┌─────────────────┐
│      User       │
│ - id            │
│ - username (UQ) │
│ - email (UQ)    │
│ - password_hash │
│ - role (RBAC)   │
└─────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                          TrainingCentre                          │
│ - id                                                             │
│ - centre_code (UQ, IX)                                           │
│ - name, state, district (IX), capacity, status                   │
└──────┬────────────┬─────────────┬─────────────┬───────────┬──────┘
       │ 1          │ 1           │ 1           │ 1         │ 1
       │            │             │             │           │
       ▼ *          ▼ *           ▼ *           ▼ *         ▼ *
┌─────────────┐ ┌──────────────┐ ┌───────────┐ ┌─────────┐ ┌───────────────┐
│   Camera    │ │  Attendance  │ │ Inventory │ │ Alert   │ │  Compliance   │
│ - id        │ │  Record      │ │ Item      │ │ - id    │ │  Score        │
│ - centre_id │ │ - registered │ │ - item_   │ │ - type  │ │ - attendance_ │
│ - zone      │ │ - submitted  │ │   type    │ │ - sever-│ │   score       │
│ - status(IX)│ │   present    │ │ - sanct-  │ │   ity   │ │ - infra_score │
│ - source    │ │ - date (IX)  │ │   ioned   │ │ - stat- │ │ - overall     │
└──────┬──────┘ └──────────────┘ └───────────┘ │   us    │ │ - risk_level  │
       │                                       └─────────┘ └───────────────┘
       ├─────────────────────────┐
       ▼ *                       ▼ *
┌────────────────────────┐  ┌────────────────────────┐
│     DetectionEvent     │  │   ProcessingSession    │
│ - id                   │  │ - id                   │
│ - event_type           │  │ - source               │
│ - object_type          │  │ - status               │
│ - count, confidence    │  │ - frames_processed     │
│ - metadata (JSON)      │  │ - processing_fps       │
│ - evidence_path        │  │ - average_confidence   │
└────────────────────────┘  └────────────────────────┘
```

### Relational Integrity Constraints
- Foreign keys with `PRAGMA foreign_keys = ON` in SQLite.
- `AttendanceRecord`: `registered_count >= 0`, `submitted_present >= 0`, `submitted_present <= registered_count`.
- `ComplianceScore`: scores constrained to `[0.0, 100.0]`.
- `DetectionEvent` & `Alert`: confidence constrained to `[0.0, 1.0]`.

---

## 4. Privacy Guarantees
- No facial recognition, face identification, or biometric extraction.
- Short-lived tracking IDs exist solely during video processing sessions.
- Raw video storage is restricted; only anonymized metadata and required evidence frames are stored.
