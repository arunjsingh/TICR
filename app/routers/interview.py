# app/routers/interview.py
import logging
import traceback

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

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
    payload: GenerateQuestionsRequest = Body(...),
    db: AsyncSession = Depends(get_db),
):
    # 1. Call Ollama
    try:
        logger.debug("▶ Calling generate_questions service...")
        raw_questions = await generate_questions(
            job_description=payload.job_description,
            resume=payload.resume,
            test_mode=payload.test_mode,
        )
        logger.debug(f"▶ Got {len(raw_questions)} questions back")
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e))
    except Exception as e:
        logger.error(f"▶ Ollama call failed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=502, detail=f"Ollama error: {str(e)}")

    # 2. Persist to DB
    try:
        logger.debug("▶ Saving to DB...")
        question_set = QuestionSet(
            job_desc=payload.job_description,
            resume=payload.resume,
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