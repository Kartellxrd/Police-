from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime
from .import schemas

# Point this to your login router endpoint url location
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS_IN_PRODUCTION" 
ALGORITHM = "HS256"

def get_current_user(token: str = Depends(oauth2_scheme)) -> schemas.TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        staff_id: str = payload.get("sub")
        role: str = payload.get("role")
        
        if staff_id is None:
            raise credentials_exception
            
        token_data = schemas.TokenData(staff_id=staff_id, role=role)
    except JWTError:
        raise credentials_exception
        
    return token_data