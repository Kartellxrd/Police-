from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional
from enum import Enum

# --- ENUMERATION CONTROLLERS ---
class UserRole(str, Enum):
    Desk_Officer = "Desk_Officer"
    CID_Detective = "CID_Detective"
    Admin = "Admin"

# --- SYSTEM ACCOUNT AUTH SCHEMAS ---
class StaffUserBase(BaseModel):
    staff_id: str = Field(..., examples=["BPS-4102"])
    first_name: str = Field(..., examples=["Thabo"])
    last_name: str = Field(..., examples=["Molefi"])
    assigned_station: str = Field(..., examples=["Gaborone Central"])
    system_role: UserRole = UserRole.Desk_Officer

class StaffUserCreate(StaffUserBase):
    password: str = Field(..., min_length=6, examples=["securepass123"])

class StaffUserResponse(StaffUserBase):
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    staff_id: str
    password: str

# --- NATIONAL SUSPECT IDENTITY SCHEMAS ---
class SuspectBase(BaseModel):
    omang_number: str = Field(..., min_length=9, max_length=9, examples=["123456789"])
    first_name: str
    last_name: str
    date_of_birth: date
    gender: str
    biometric_token: Optional[str] = None
    risk_tier: str = "Low Risk"

    @field_validator("omang_number")
    @classmethod
    def validate_omang(cls, value: str) -> str:
        if not value.isdigit():
            raise ValueError("Omang number must contain digits only")
        return value

class SuspectResponse(SuspectBase):
    class Config:
        from_attributes = True

# --- CROSS-DISTRICT CRIME LEDGER SCHEMAS ---
class CrimeRecordCreate(BaseModel):
    omang_number: str = Field(..., min_length=9, max_length=9)
    offense_type: str = Field(..., examples=["Armed Robbery"])
    case_narrative: str
    incident_station: str = Field(..., examples=["Francistown Phase IV"])

class CrimeRecordResponse(BaseModel):
    case_uuid: str
    omang_number: str
    offense_type: str
    case_narrative: str
    timestamp_logged: datetime
    incident_station: str
    logged_by: Optional[str]

    class Config:
        from_attributes = True

# --- NEWLY ADDED SECURITY & SESSION TOKENS ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    staff_id: Optional[str] = None
    role: Optional[str] = None