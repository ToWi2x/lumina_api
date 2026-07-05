from sqlalchemy import Column, String, Text, JSON
from database import Base

class Task(Base):
    #explicitly name table in SQLAlchemy
    __tablename__ = "tasks"

    #use the long UUID string generated in main.py for this ID
    id = Column(String, primary_key=True, index=True)
    
    # Track the status (Pending, Processing, Completed)
    status = Column(String, default="Pending")
    
    # Save the original text the user sent
    original_text = Column(Text)
    
    # Store the final AI structured response here
    result = Column(JSON, nullable=True)