from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)          
    password_hash = Column(String, nullable=False)

    provider = Column(String, default="local")
    provider_id = Column(String, nullable=True)

    incidents = relationship("Incident", back_populates="user")


class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True, index=True)

    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    legal_articles = Column(Text)
    explanation = Column(Text)
    recommendation = Column(Text)
    what_to_say = Column(Text)

    user = relationship("User", back_populates="incidents")
