from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/suspects",
    tags=["National Suspect Identity Registry"]
)

# --- REGISTER A NEW SUSPECT ---
@router.post("", response_model=schemas.SuspectResponse, status_code=status.HTTP_201_CREATED)
def register_suspect(
    suspect_in: schemas.SuspectBase, 
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    # Check if suspect is already registered via Omang Number
    existing_suspect = db.query(models.Suspect).filter(models.Suspect.omang_number == suspect_in.omang_number).first()
    if existing_suspect:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Identity conflict: Omang {suspect_in.omang_number} is already registered."
        )
        
    new_suspect = models.Suspect(**suspect_in.model_dump())
    db.add(new_suspect)
    db.commit()
    db.refresh(new_suspect)
    return new_suspect


# --- GET ALL SUSPECTS ---
@router.get("", response_model=List[schemas.SuspectResponse])
def get_all_suspects(
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    return db.query(models.Suspect).all()


# --- GET SPECIFIC SUSPECT BY OMANG ---
@router.get("/{omang_number}", response_model=schemas.SuspectResponse)
def get_suspect_by_omang(
    omang_number: str,
    db: Session = Depends(get_db),
    current_user: schemas.TokenData = Depends(oauth2.get_current_user)
):
    suspect = db.query(models.Suspect).filter(models.Suspect.omang_number == omang_number).first()
    if not suspect:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Suspect with Omang {omang_number} not found."
        )
    return suspect