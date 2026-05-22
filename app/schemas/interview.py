# app/schemas/interview.py
from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from enum import Enum

# 👇 1. Define your global limit variable here
MAX_QUESTIONS_LIMIT = 20

class DifficultyLevel(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"

# CLEANED UP: Removed the duplicate definition of this class
class DifficultyDistribution(BaseModel):
    # 👇 2. Update the 'le' (less than or equal to) limit using the variable
    easy: int = Field(default=0, ge=0, le=MAX_QUESTIONS_LIMIT, description="Number of easy questions")
    medium: int = Field(default=0, ge=0, le=MAX_QUESTIONS_LIMIT, description="Number of medium questions")
    hard: int = Field(default=0, ge=0, le=MAX_QUESTIONS_LIMIT, description="Number of hard questions")

    @model_validator(mode="after")
    def validate_total_count(self) -> "DifficultyDistribution":
        total = self.easy + self.medium + self.hard
        if total == 0:
            raise ValueError("You must request at least 1 question.")
        
        # 👇 3. Use the variable in the total sum validation check
        if total > MAX_QUESTIONS_LIMIT:
            raise ValueError(f"Total questions requested ({total}) exceeds the limit of {MAX_QUESTIONS_LIMIT}.")
        return self

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

class GenerateCustomQuestionsRequest(BaseModel):
    job_description: str = Field(..., min_length=50)
    resume: Optional[str] = None
    distribution: DifficultyDistribution

# --- Response ---
class QuestionOut(BaseModel):
    id: int
    difficulty: DifficultyLevel
    question: str
    answer: str

    class Config:
        from_attributes = True

class GenerateQuestionsResponse(BaseModel):
    question_set_id: int
    questions: List[QuestionOut]
