from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.database.models import User
from app.core.security import get_current_user
from app.services.evaluation_metrics import get_full_evaluation_report

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.get("/results", response_model=dict)
def get_evaluation_results(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns AI model evaluation metrics: Precision, Recall, F1, FPR, FNR.
    Computed against simulated benchmark ground truth dataset (SIH PS 26245 mandate).
    [SIMULATED DEMO DATA]
    """
    report = get_full_evaluation_report()
    return {
        "success": True,
        "data": report
    }
