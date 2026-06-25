from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/dashboard",
    tags=["Operational Analytics Hub"]
)

@router.get("/stats")
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    # 1. Gather total volumetric records
    total_suspects = db.query(models.Suspect).count()
    total_crimes = db.query(models.CrimeRecord).count()
    
    # 2. Count suspects by risk tier (Low Risk, Medium Risk, High Risk)
    risk_counts = (
        db.query(models.Suspect.risk_tier, func.count(models.Suspect.omang_number))
        .group_by(models.Suspect.risk_tier)
        .all()
    )
    
    # Format the risk matrix into a clean key-value object for the frontend
    risk_breakdown = {tier: count for tier, count in risk_counts}
    
    # 3. Pull the 5 most recently logged crime records for the dashboard activity feed
    recent_incidents = (
        db.query(models.CrimeRecord)
        .order_by(models.CrimeRecord.timestamp_logged.desc())
        .limit(5)
        .all()
    )
    
    return {
        "metrics": {
            "total_suspects": total_suspects,
            "total_crimes": total_crimes,
            "risk_breakdown": risk_breakdown
        },
        "recent_activity": recent_incidents
    }