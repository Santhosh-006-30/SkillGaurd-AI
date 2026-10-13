from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import (
    TrainingCentre, Camera, Alert, ComplianceScore,
    AlertStatus, CameraStatus, RiskLevel
)

class AnalyticsService:
    @staticmethod
    def get_overview(db: Session) -> Dict[str, Any]:
        total_centres = db.query(TrainingCentre).count()
        total_cameras = db.query(Camera).count()
        active_cameras = db.query(Camera).filter(Camera.status == CameraStatus.ONLINE).count()
        offline_cameras = db.query(Camera).filter(Camera.status == CameraStatus.OFFLINE).count()
        
        open_alerts = db.query(Alert).filter(Alert.status == AlertStatus.OPEN).count()
        
        # High/critical risk centres from latest scores
        high_risk_count = (
            db.query(func.count(func.distinct(ComplianceScore.centre_id)))
            .filter(ComplianceScore.risk_level.in_([RiskLevel.HIGH, RiskLevel.CRITICAL]))
            .scalar() or 0
        )

        # Average compliance score
        avg_score = db.query(func.avg(ComplianceScore.overall_score)).scalar() or 85.0

        # Discrepancies and shortages from alerts
        att_disc_alerts = db.query(Alert).filter(Alert.alert_type == "ATTENDANCE_DISCREPANCY").count()
        infra_shortage_alerts = db.query(Alert).filter(Alert.alert_type == "INFRASTRUCTURE_SHORTAGE").count()

        return {
            "total_centres": total_centres,
            "active_cameras": active_cameras,
            "total_cameras": total_cameras,
            "open_alerts": open_alerts,
            "high_risk_centres": high_risk_count,
            "average_compliance": round(float(avg_score), 1),
            "total_attendance_discrepancies": att_disc_alerts,
            "total_infrastructure_shortages": infra_shortage_alerts,
            "offline_cameras": offline_cameras,
        }

    @staticmethod
    def get_risk_distribution(db: Session) -> List[Dict[str, Any]]:
        total = db.query(TrainingCentre).count() or 1
        
        # Count risk levels from latest compliance scores
        risk_counts = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }

        centres = db.query(TrainingCentre).all()
        for c in centres:
            latest = (
                db.query(ComplianceScore)
                .filter(ComplianceScore.centre_id == c.id)
                .order_by(ComplianceScore.timestamp.desc())
                .first()
            )
            if latest and latest.risk_level:
                risk_counts[latest.risk_level.value] = risk_counts.get(latest.risk_level.value, 0) + 1
            else:
                risk_counts["LOW"] += 1

        return [
            {
                "name": r,
                "count": count,
                "percentage": round(count / total * 100.0, 1)
            }
            for r, count in risk_counts.items()
        ]

    @staticmethod
    def get_compliance_trend(db: Session) -> List[Dict[str, Any]]:
        # Returns daily aggregated score trend
        scores = db.query(ComplianceScore).order_by(ComplianceScore.timestamp.asc()).all()
        if not scores:
            return []

        trend = []
        for s in scores:
            date_str = s.timestamp.strftime("%Y-%m-%d")
            trend.append({
                "date": date_str,
                "attendance_score": round(s.attendance_score, 1),
                "infrastructure_score": round(s.infrastructure_score, 1),
                "overall_score": round(s.overall_score, 1)
            })
        return trend

    @staticmethod
    def get_alerts_trend(db: Session) -> List[Dict[str, Any]]:
        # Returns alert counts categorized by severity
        alerts = db.query(Alert).order_by(Alert.created_at.asc()).all()
        if not alerts:
            return []

        daily_map = {}
        for a in alerts:
            d = a.created_at.strftime("%Y-%m-%d")
            if d not in daily_map:
                daily_map[d] = {"date": d, "critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
            sev = a.severity.value if hasattr(a.severity, "value") else str(a.severity)
            if sev == "CRITICAL":
                daily_map[d]["critical_count"] += 1
            elif sev == "HIGH":
                daily_map[d]["high_count"] += 1
            elif sev == "MEDIUM":
                daily_map[d]["medium_count"] += 1
            else:
                daily_map[d]["low_count"] += 1

        return list(daily_map.values())

    @staticmethod
    def get_centre_ranking(db: Session) -> List[Dict[str, Any]]:
        centres = db.query(TrainingCentre).all()
        rankings = []
        for c in centres:
            latest = (
                db.query(ComplianceScore)
                .filter(ComplianceScore.centre_id == c.id)
                .order_by(ComplianceScore.timestamp.desc())
                .first()
            )
            alerts_count = db.query(Alert).filter(Alert.centre_id == c.id, Alert.status == AlertStatus.OPEN).count()
            rankings.append({
                "centre_code": c.centre_code,
                "name": c.name,
                "district": c.district,
                "overall_score": round(latest.overall_score, 1) if latest else 100.0,
                "risk_level": latest.risk_level.value if latest and hasattr(latest.risk_level, "value") else "LOW",
                "open_alerts": alerts_count
            })
        rankings.sort(key=lambda x: x["overall_score"], reverse=True)
        return rankings
