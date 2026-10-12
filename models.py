from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
import datetime
from database import Base

class EmailCase(Base):
    __tablename__ = "email_cases"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), index=True)
    sender = Column(String(255))
    subject = Column(String(255))
    fraud_score = Column(Float)
    origin_country = Column(String(100))
    ml_label = Column(String(50))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Store the entire raw JSON result from our pipeline for the detailed view
    full_analysis = Column(JSON)
