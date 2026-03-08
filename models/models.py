from sqlalchemy import MetaData, Table, Column, Integer, String, TIMESTAMP, ForeignKey, JSON, Boolean
from datetime import datetime
from database import Base


class Link(Base):
    __tablename__ = "link"
    id = Column(Integer, primary_key=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now)
    last_used_at = Column(TIMESTAMP, nullable=True)
    click_count = Column(Integer, default=0) # сколько раз вызывали метод redirect
    expires_at = Column(TIMESTAMP, nullable=True)
