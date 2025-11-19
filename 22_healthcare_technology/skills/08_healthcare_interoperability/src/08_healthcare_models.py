#!/usr/bin/env python3
"""Healthcare Data Models - SQLAlchemy ORM models"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    mrn = Column(String(50), unique=True)
    family_name = Column(String(100))
    given_name = Column(String(100))
    dob = Column(DateTime)
    gender = Column(String(1))
    created_at = Column(DateTime, default=datetime.utcnow)
    observations = relationship("Observation", back_populates="patient")

class Observation(Base):
    __tablename__ = 'observations'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    code = Column(String(100))
    value = Column(String(500))
    unit = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    patient = relationship("Patient", back_populates="observations")

class MedicationRequest(Base):
    __tablename__ = 'medication_requests'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    medication_code = Column(String(100))
    status = Column(String(50))
    dose = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100))
    action = Column(String(50))
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    outcome = Column(String(50))
