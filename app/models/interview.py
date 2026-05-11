# app/models/interview.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base  # adjust to your existing declarative base import
import enum


class DifficultyLevel(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class QuestionSet(Base):
    """One generation run — tied to a job description and optional resume."""
    __tablename__ = "question_sets"

    id         = Column(Integer, primary_key=True, index=True)
    job_desc   = Column(Text, nullable=False)
    resume     = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    questions  = relationship("Question", back_populates="question_set", cascade="all, delete-orphan")


class Question(Base):
    """A single technical question + answer, linked to a QuestionSet."""
    __tablename__ = "questions"

    id              = Column(Integer, primary_key=True, index=True)
    question_set_id = Column(Integer, ForeignKey("question_sets.id"), nullable=False)
    difficulty      = Column(Enum(DifficultyLevel), nullable=False)
    question_text   = Column(Text, nullable=False)
    answer_text     = Column(Text, nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)

    question_set    = relationship("QuestionSet", back_populates="questions")