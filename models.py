from sqlalchemy import create_engine, Column, Integer, String, Text, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///claims.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

class Claim(Base):
    __tablename__ = 'claims'
    id = Column(Integer, primary_key=True)
    claim_number = Column(String(50), unique=True)
    extracted_data = Column(JSON)  # Full structured JSON
    fraud_score = Column(Float)
    summary = Column(Text)
    status = Column(String(20), default='pending')

Base.metadata.create_all(engine)