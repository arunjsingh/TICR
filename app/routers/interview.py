# app/routers/interview.py
import logging
import traceback

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.utils.file_parser import extract_text_from_file
from app.db.database import get_db
from app.models.interview import Question, QuestionSet
from app.schemas.interview import (
    GenerateQuestionsRequest,
    GenerateQuestionsResponse,
    QuestionOut,
)
from app.services.ollama_service import generate_questions

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/generate-questions", response_model=GenerateQuestionsResponse)
async def generate_interview_questions(
    # Optional Text inputs (Form fields)
    job_description_text: Optional[str] = Form(None),
    resume_text: Optional[str] = Form(None),
    
    # Optional File inputs (File fields)
    job_description_file: Optional[UploadFile] = File(None),
    resume_file: Optional[UploadFile] = File(None),
    
    test_mode: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    # 1. Logic to prioritize File over Text (or vice versa)
    final_jd = ""
    final_resume = None

    if job_description_file:
        final_jd = await extract_text_from_file(job_description_file)
        logger.info("Final JD:", final_jd)
    else:
        final_jd = job_description_text or ""

    # 2. Process Resume
    if resume_file:
        final_resume = await extract_text_from_file(resume_file)
    else:
        final_resume = resume_text


    # Validation
    if len(final_jd) < 50:
        raise HTTPException(status_code=400, detail="Job description text too short.")

    # 2. Call Ollama using the extracted strings
    try:
        raw_questions = await generate_questions(
            job_description=final_jd,
            resume=final_resume,
            test_mode=test_mode,
        )
        logger.debug(f"▶ Got {len(raw_questions)} questions back")
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"▶ Ollama call failed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=502, detail=f"Ollama error: {str(e)}")

    # 2. Persist to DB
    try:
        logger.debug("Saving to DB...")
        question_set = QuestionSet(
            job_desc=final_jd,
            resume=final_resume,
        )
        db.add(question_set)
        await db.flush()
        logger.debug(f"▶ QuestionSet id={question_set.id}")

        db_questions = []
        for q in raw_questions:
            db_q = Question(
                question_set_id=question_set.id,
                difficulty=q["difficulty"],
                question_text=q["question"],
                answer_text=q["answer"],
            )
            db.add(db_q)
            db_questions.append(db_q)

        await db.commit()
        logger.debug("▶ Commit successful")

        for q in db_questions:
            await db.refresh(q)

    except Exception as e:
        await db.rollback()
        logger.error(f"▶ DB error:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    # 3. Return response
    return GenerateQuestionsResponse(
        question_set_id=question_set.id,
        questions=[
            QuestionOut(
                id=q.id,
                difficulty=q.difficulty,
                question=q.question_text,
                answer=q.answer_text,
            )
            for q in db_questions
        ],
    )