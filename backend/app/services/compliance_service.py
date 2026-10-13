from typing import List, Optional
from sqlalchemy.orm import Session
from app.database.models import ComplianceScore, TrainingCentre, RiskLevel
from app.schemas.compliance import ComplianceScoreCreate

class ComplianceService:
    @staticmethod
    def get_scores(
        db: Session,
        centre_id: Optional[int] = None,
        risk_level: Optional[RiskLevel] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ComplianceScore]:
        query = db.query(ComplianceScore)
        if centre_id:
            query = query.filter(ComplianceScore.centre_id == centre_id)
        if risk_level:
            query = query.filter(ComplianceScore.risk_level == risk_level)
        return query.order_by(ComplianceScore.timestamp.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def get_latest_centre_score(db: Session, centre_id: int) -> Optional[ComplianceScore]:
        return (
            db.query(ComplianceScore)
            .filter(ComplianceScore.centre_id == centre_id)
            .order_by(ComplianceScore.timestamp.desc())
            .first()
        )

    @staticmethod
    def create_score(db: Session, obj_in: ComplianceScoreCreate) -> ComplianceScore:
        score = ComplianceScore(**obj_in.model_dump())
        db.add(score)
        db.commit()
        db.refresh(score)
        return score
