from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post("", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # OAuth2PasswordRequestForm uses 'username' field, so we map it to staff_id
    user = db.query(models.StaffUser).filter(models.StaffUser.staff_id == user_credentials.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
        
    if not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
        
    # Create token passing the staff ID and their role
    access_token = utils.create_access_token(data={"user_id": user.staff_id, "role": user.system_role})
    
    return {"access_token": access_token, "token_type": "bearer"}