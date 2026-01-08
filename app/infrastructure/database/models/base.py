from sqlalchemy import Column, Integer, DateTime, String, func
from app.infrastructure.database.session import Base



class BaseDBModel(Base):
    __abstract__ = True
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)