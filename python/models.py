from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Collection(Base):
    __tablename__ = 'Collection'
    colid = Column(Integer, primary_key=True, autoincrement=True)
    searchword = Column(String(50), nullable=False)
    date = Column(DateTime, nullable=False)
