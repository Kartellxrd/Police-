from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, oauth2  # We will create oauth2.py next to extract logged_by
from ..database import get_db

router = APIRouter(
    prefix="/crimes",
    tags=["Cross-District Crime Ledger"]
)

# --- LOG A NEW CRIME RECORD ---
@router.post("", response_model=schemas.CrimeRecordResponse, status_code=status.HTTP_201_CREATED)
def create_crime_record(
    crime_in: schemas.CrimeRecordCreate, 
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)  # Secures the endpoint
):
    # 1. Verify that the suspect exists in the national registry via Omang Number
    suspect = db.query(models.Suspect).filter(models.Suspect.omang_number == crime_in.omang_number).first()
    if not suspect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suspect with Omang Number {crime_in.omang_number} not found. Register the suspect first."
        )
    
    # 2. Build database record layout and inject the authenticated user's ID
    crime_data = crime_in.model_dump()
    crime_data["logged_by"] = current_user.staff_id  # Automatically attributes accountability
    
    new_record = models.CrimeRecord(**crime_data)
    
    # 3. Save transactions to Supabase
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    
    return new_record


# --- RETRIEVE ALL CRIME RECORDS ---
@router.get("", response_model=List[schemas.CrimeRecordResponse])
def get_all_crimes(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    crimes = db.query(models.CrimeRecord).all()
    return crimes


# --- SEARCH CRIME RECORDS BY OMANG ---
@router.get("/suspect/{omang_number}", response_model=List[schemas.CrimeRecordResponse])
def get_crimes_by_suspect(
    omang_number: str,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    crimes = db.query(models.CrimeRecord).filter(models.CrimeRecord.omang_number == omang_number).all()
    return crimes