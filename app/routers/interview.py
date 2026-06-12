from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form 
from sqlalchemy.ext.asyncio import AsyncSession 
from typing import Optional 
import traceback 
import logging 

from app.db.database import get_db 
from app.utils.file_parser import extract_text_from_file 
from app.models.interview import QuestionSet, Question 
# 👇 1. IMPORT YOUR NEW LIMIT VARIABLE HERE
from app.schemas.interview import DifficultyDistribution, GenerateQuestionsResponse, QuestionOut, MAX_QUESTIONS_LIMIT 
from app.services.ollama_service import generate_custom_questions 

logger = logging.getLogger(__name__) 
router = APIRouter(prefix="/interview", tags=["Interview"]) 

@router.post("/generate-custom-questions", response_model=GenerateQuestionsResponse)
async def generate_custom_interview_questions(
    job_description_text: Optional[str] = Form(None, description="Raw job description text"),
    resume_text: Optional[str] = Form(None, description="Raw candidate resume text"),
    job_description_file: Optional[UploadFile] = File(None, description="Upload Job Description (PDF/Word)"),
    resume_file: Optional[UploadFile] = File(None, description="Upload Candidate Resume (PDF/Word)"),
    easy_count: Optional[int] = Form(0, ge=0, le=MAX_QUESTIONS_LIMIT, description="Number of easy questions"),
    medium_count: Optional[int] = Form(0, ge=0, le=MAX_QUESTIONS_LIMIT, description="Number of medium questions"),
    hard_count: Optional[int] = Form(0, ge=0, le=MAX_QUESTIONS_LIMIT, description="Number of hard questions"),
    db: AsyncSession = Depends(get_db),
):
    logger.info("AJS in generate custom interview ROUTER")
    
    # 1. Process Job Description Input
    final_jd = ""
    if job_description_file and job_description_file.filename:
        final_jd = await extract_text_from_file(job_description_file)
        logger.info(f"Extracted JD text from file: {job_description_file.filename}")
    else:
        final_jd = job_description_text or ""

    # 2. Process Resume Input
    final_resume = ""
    if resume_file and resume_file.filename:
        final_resume = await extract_text_from_file(resume_file)
        logger.info(f"Extracted Resume text from file: {resume_file.filename}")
    else:
        final_resume = resume_text or "" # Fixed NoneType bug

    # 3. Validate Inputs and Question Counts
    if len(final_jd) < 50 and len(final_resume) < 50:
        raise HTTPException(
            status_code=400, 
            detail="You must provide either a Job Description or a Resume with at least 50 characters."
        )

    # Convert incoming None/empty form counts safely to 0
    e_cnt = easy_count if easy_count is not None else 0
    m_cnt = medium_count if medium_count is not None else 0
    h_cnt = hard_count if hard_count is not None else 0

    total_questions = e_cnt + m_cnt + h_cnt
    if total_questions == 0:
        raise HTTPException(status_code=400, detail="You must request at least 1 question.")

    if total_questions > MAX_QUESTIONS_LIMIT:
        raise HTTPException(
            status_code=400, 
            detail=f"Total requested questions ({total_questions}) exceeds the maximum limit of {MAX_QUESTIONS_LIMIT}."
        )
    distribution = DifficultyDistribution(easy=e_cnt, medium=m_cnt, hard=h_cnt)

    # 4. Package distribution metrics for the LLM prompt engine 
    distribution = DifficultyDistribution(easy=easy_count, medium=medium_count, hard=hard_count) 

    # 5. Pipeline execution to Ollama instance 
    try: 
        raw_questions = await generate_custom_questions( 
            job_description=final_jd, 
            distribution=distribution, 
            resume=final_resume, 
        ) 
        
        # Safely extract the list if Ollama wrapped it in a "questions" key 
        if isinstance(raw_questions, dict) and "questions" in raw_questions: 
            raw_questions = raw_questions["questions"] 
        elif isinstance(raw_questions, str): 
            import json 
            parsed = json.loads(raw_questions) 
            raw_questions = parsed.get("questions", parsed if isinstance(parsed, list) else []) 
            
        logger.debug(f"▶ Got {len(raw_questions)} dynamic questions back from Ollama") 
    except ValueError as e: 
        # Cleaned up: Put clean error mapping response message back in
        raise HTTPException(status_code=502, detail=f"AI generation mismatch: {str(e)}") 
    except Exception as e: 
        logger.error(f"▶ Ollama dynamic generation failed:\n{traceback.format_exc()}") 
        raise HTTPException(status_code=502, detail=f"Ollama error: {str(e)}") 

    # 6. Database Persistence 
    try: 
        logger.debug("Saving generated custom questions to database...") 
        question_set = QuestionSet( 
            job_desc=final_jd, 
            resume=final_resume, 
        ) 
        db.add(question_set) 
        await db.flush() # Populates question_set.id for child entities 

        db_questions = [] 
        for q in raw_questions: 
            db_q = Question( 
                question_set_id=question_set.id, 
                difficulty=q.get("difficulty", "easy").lower(), 
                question_text=q.get("question", ""), 
                answer_text=q.get("answer", ""), 
            ) 
            db.add(db_q) 
            db_questions.append(db_q) 
        await db.commit() 
        logger.debug(f"▶ Successfully saved QuestionSet id={question_set.id}") 
    except Exception as e: 
        await db.rollback() 
        logger.error(f"▶ Database transaction rolled back due to error:\n{traceback.format_exc()}") 
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}") 

    # 7. Construct and Return Schema Response 
    return GenerateQuestionsResponse( 
        question_set_id=question_set.id, 
        questions=[ 
            QuestionOut( 
                id=q.id, 
                difficulty=q.difficulty, 
                question=q.question_text, 
                answer=q.answer_text, 
            ) for q in db_questions 
        ], 
    )
