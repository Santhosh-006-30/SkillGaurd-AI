# SkillGuard AI

**Subtitle**: Privacy-Preserving AI-Based Training Centre Attendance and Infrastructure Compliance Monitoring  
**Problem Statement**: SIH 26245  
**Organization**: Ministry of Skill Development and Entrepreneurship (MSDE)  
**Theme**: Smart Education  

> **IMPORTANT DISCLAIMER**:  
> All seeded centre, attendance, inventory, compliance and alert records are simulated demonstration data and are not official MSDE data.  
> The system strictly adheres to privacy safeguards: zero facial recognition, zero facial embeddings, and conservative operability assessments based solely on observable activity without claiming electrical or mechanical verification.

---

## 🌐 Live Vercel Deployment
* **Live Web App**: [https://skill-gaurd-ai-sih.vercel.app](https://skill-gaurd-ai-sih.vercel.app) (also accessible at [https://skillguard-ai-demo.vercel.app](https://skillguard-ai-demo.vercel.app))
* **Demo Sign-in Accounts**:
  * **Super Admin**: `admin` / `AdminPassword@2026`
  * **State Monitor**: `monitor` / `MonitorPassword@2026`
  * **Field Inspector**: `inspector` / `InspectorPassword@2026`
  * **Centre Operator**: `operator` / `OperatorPassword@2026`

---

## 1. Project Overview
SkillGuard AI is an automated compliance monitoring system designed to verify government-funded vocational and skill training centres. The system estimates physical occupancy, detects sanctioned laboratory infrastructure, observes equipment activity, and reconciles records against official quotas — all without facial recognition or biometric identification.

---

## 2. Privacy-First Principles
- **No Facial Recognition**: Strictly no face matching, recognition, or face database storage.
- **Anonymous Presence Estimation**: Head/body bounding boxes with temporary track IDs only.
- **Edge Processing & Low-Bandwidth Mode**: Metadata aggregation with local event buffering.
- **Conservative Terminology**: "Activity observed" and "Estimated physical presence", never claiming mechanical functionality or biometric identity verification.

---

## 3. Technology Stack
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Recharts, Lucide React
- **Backend**: Python 3.10+, FastAPI, Pydantic, SQLAlchemy, SQLite (PostgreSQL compatible), ReportLab
- **AI/Computer Vision**: YOLOv8, ByteTrack/BoT-SORT, OpenCV, NumPy, Pandas

---

## 4. Database Architecture & Schema (Phase 2)
The database persistence layer is built on SQLAlchemy with SQLite for the MVP (abstracted for seamless PostgreSQL migration).

### Relational Entities
1. **User**: RBAC authentication (`ADMIN`, `MONITOR`, `INSPECTOR`, `CENTRE_OPERATOR`).
2. **TrainingCentre**: Vocational centre profile with capacity, geolocation, and status.
3. **Camera**: Camera endpoint configuration (`UPLOAD`, `WEBCAM`, `RTSP`, `SIMULATION`).
4. **AttendanceRecord**: Official centre-reported attendance records with validation constraints (`submitted_present <= registered_count`).
5. **InventoryItem**: Official sanctioned inventory items (`CHAIR`, `COMPUTER`, `WORKBENCH`, `MACHINE`, `PROJECTOR`) with minimum quotas.
6. **DetectionEvent**: Vision event logging (occupancy counts, zones, bounding boxes; strictly zero biometric storage).
7. **ProcessingSession**: Session telemetry tracking frames, FPS, status, and average confidence.
8. **ComplianceScore**: Calculated weighted audit scores and risk classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
9. **Alert**: Discrepancy, shortage, and health notifications with severity levels (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).

### Database Commands
- **Initialize Schema**:
  ```bash
  python -m app.database.init_db
  ```
- **Seed Simulated Demo Data**:
  ```bash
  python -m app.database.seed
  ```
- **Verify Database & Relationships**:
  ```bash
  python -m app.database.verify_db
  ```

---

## 5. Development Demo Credentials
For testing and development evaluation, the following pre-seeded demo accounts are available:

| Role | Username | Password | Access Scope |
| :--- | :--- | :--- | :--- |
| **ADMIN** | `admin` | `AdminPassword@2026` | Full administrative oversight and system configuration |
| **MONITOR** | `monitor` | `MonitorPassword@2026` | Real-time compliance monitoring & alert review |
| **INSPECTOR** | `inspector` | `InspectorPassword@2026` | Field inspection & evidence verification |
| **CENTRE_OPERATOR** | `operator` | `OperatorPassword@2026` | Centre attendance submission & inventory status |

*(All passwords are saved as secure bcrypt hashes. Plaintext passwords are never stored in the database).*

---

## 6. Simulated Training Centre Scenarios

1. **TN-CBE-001**: *Coimbatore Skill Development Centre 01*
   - Scenario: **COMPLIANT**
   - High attendance match, complete sanctioned inventory, Low Risk.
2. **TN-CBE-002**: *Coimbatore Skill Development Centre 02*
   - Scenario: **ATTENDANCE DISCREPANCY**
   - Significant delta between submitted records and camera presence, High Risk.
3. **TN-CBE-003**: *Coimbatore Skill Development Centre 03*
   - Scenario: **INFRASTRUCTURE DISCREPANCY**
   - Missing sanctioned industrial machinery in Workshop B, High Risk.

---

## 7. Setup & Running

### Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 8. Development Status
See [DEVELOPMENT_STATUS.md](file:///d:/Project/SkillGaurd%20AI/DEVELOPMENT_STATUS.md) for full phase status and test logs.
