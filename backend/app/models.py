import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from .database import Base

class StaffUser(Base):
    __tablename__ = "staff_users"

    staff_id = Column(String(20), primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    assigned_station = Column(String(100), nullable=False)
    system_role = Column(String(50), server_default="Desk_Officer")

class Suspect(Base):
    __tablename__ = "suspects"

    omang_number = Column(String(9), primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(10), nullable=False)
    biometric_token = Column(String(100), unique=True, nullable=True)
    risk_tier = Column(String(50), server_default="Low Risk")

class CrimeRecord(Base):
    __tablename__ = "crime_records"

    case_uuid = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    omang_number = Column(String(9), ForeignKey("suspects.omang_number", ondelete="CASCADE"), nullable=False)
    offense_type = Column(String(100), nullable=False)
    case_narrative = Column(Text, nullable=False)  # 🧠 Fixed: Changed to capital 'Text' type class
    timestamp_logged = Column(DateTime(timezone=True), server_default=text("now()"))
    incident_station = Column(String(100), nullable=False)
    logged_by = Column(String(20), ForeignKey("staff_users.staff_id"), nullable=True)