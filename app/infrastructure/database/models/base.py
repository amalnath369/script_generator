from sqlalchemy import Column, Integer, DateTime
from app.infrastructure.database.session import Base



class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)