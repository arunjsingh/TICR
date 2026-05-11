# app/schemas/interview.py
from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DifficultyLevel(str, Enum):
    easy   = "easy"
    medium = "medium"
    hard   = "hard"


# --- Request ---

class GenerateQuestionsRequest(BaseModel):
    job_description: str = Field(
        ...,
        min_length=50,
        description="Full job description text",
    )
    resume: Optional[str] = Field(
        None,
        description="Candidate resume text (optional)",
    )

    test_mode: bool = Field(
        False,
        description="If true, returns only 1 easy question (for testing purposes)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_description": "We are looking for a senior Python backend engineer with FastAPI, PostgreSQL, and Docker experience. The candidate should have 5+ years of Python development.",
                "resume": "5 years of Python experience, built REST APIs with FastAPI, deployed on AWS ECS. Proficient in PostgreSQL and Redis."
            }
        }


# --- Response ---

class QuestionOut(BaseModel):
    id:         int
    difficulty: DifficultyLevel
    question:   str
    answer:     str

    class Config:
        from_attributes = True


class GenerateQuestionsResponse(BaseModel):
    question_set_id: int
    questions:       List[QuestionOut]