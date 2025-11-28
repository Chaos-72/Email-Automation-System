# backend/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON, Text
from sqlalchemy.sql import func
from .db import Base

class Email(Base):
    __tablename__ = "emails"
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    body_html = Column(Text, nullable=False)
    recipients = Column(JSON, nullable=False)  # list of emails
    send_time = Column(DateTime, nullable=True)
    sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    attendees = Column(JSON, nullable=True)
    google_event_id = Column(String, nullable=True)
    meet_link = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
