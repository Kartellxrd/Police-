from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# --- STAFF REGISTRATION ENDPOINT ---
@router.post("/register", response_model=schemas.StaffUserResponse, status_code=status.HTTP_201_CREATED)
def register_staff(staff_in: schemas.StaffUserCreate, db: Session = Depends(get_db)):
    # 1. Check if the staff member already exists
    existing_staff = db.query(models.StaffUser).filter(models.StaffUser.staff_id == staff_in.staff_id).first()
    if existing_staff:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Staff record with ID {staff_in.staff_id} is already registered."
        )
    
    # 2. Hash the incoming password securely
    hashed_password = utils.hash_password(staff_in.password)
    
    # 3. Prepare data for database insertion
    staff_data = staff_in.model_dump()
    staff_data.pop("password")  # Strip the raw text password
    staff_data["password_hash"] = hashed_password
    
    # 4. Save to the database
    new_staff = models.StaffUser(**staff_data)
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    
    return new_staff

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    
    # OAuth2PasswordRequestForm expects a 'username' field, which maps to your staff_id
    user = db.query(models.StaffUser).filter(models.StaffUser.staff_id == user_credentials.username).first()
    
    if not user or not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
        
    # FIX: Safely extract string if it's an Enum instance, otherwise read directly as string
    role_str = user.system_role.value if hasattr(user.system_role, "value") else user.system_role
        
    # Create token passing the verified staff ID and their role string
    access_token = utils.create_access_token(
        data={
            "sub": user.staff_id, 
            "role": role_str
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
    
    # OAuth2PasswordRequestForm expects a 'username' field, which maps to your staff_id
    user = db.query(models.StaffUser).filter(models.StaffUser.staff_id == user_credentials.username).first()
    
    if not user or not utils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credentials"
        )
        
    # Create token passing the staff ID and their role (extracting string value from Enum)
    access_token = utils.create_access_token(
        data={
            "sub": user.staff_id, 
            "role": user.system_role.value
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}