# app/services/ollama_service.py
import httpx
import json
import re
from typing import Optional
from app.schemas.interview import DifficultyDistribution

OLLAMA_BASE_URL = "http://localhost:11434"
MODEL           = "qwen2.5:14b"

SYSTEM_PROMPT = """You are a senior technical interviewer.
Given a job description and optionally a candidate's resume, generate exactly 6 technical interview questions with detailed answers.

STRICT OUTPUT FORMAT — return only valid JSON, no markdown, no extra text:
{
  "questions": [
    {"difficulty": "easy",   "question": "...", "answer": "..."},
    {"difficulty": "easy",   "question": "...", "answer": "..."},
    {"difficulty": "medium", "question": "...", "answer": "..."},
    {"difficulty": "medium", "question": "...", "answer": "..."},
    {"difficulty": "hard",   "question": "...", "answer": "..."},
    {"difficulty": "hard",   "question": "...", "answer": "..."}
  ]
}

Rules:
- Questions must be purely technical (no HR/culture questions)
- Answers should be thorough — 3 to 6 sentences
- Tailor questions to the skills mentioned in the job description
- If a resume is provided, personalize questions to the candidate's background
- Return ONLY the JSON object above, nothing else
"""

TEST_SYSTEM_PROMPT = """You are a senior technical interviewer.
Generate exactly 1 hard technical interview question with a detailed answer.

STRICT OUTPUT FORMAT — return only valid JSON, no markdown, no extra text:
{
  "questions": [
    {"difficulty": "hard", "question": "...", "answer": "..."}
  ]
}

Rules:
- Question must be purely technical
- Answer should be 3 to 6 sentences
- Return ONLY the JSON object above, nothing else
"""

# --- Shared Helper Functions ---

def _build_user_prompt(job_description: str, resume: Optional[str]) -> str:
    prompt = f"Job Description:\n{job_description}"
    if resume:
        prompt += f"\n\nCandidate Resume:\n{resume}"
    return prompt


def _extract_json(raw: str) -> dict:
    match = re.search(r"(\{.*\}|\[.*\])", raw, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON structure found in LLM response.")
    clean_raw = match.group(1)
    clean_raw = re.sub(r"^```(?:json)?\s*", "", clean_raw)
    clean_raw = re.sub(r"\s*```$", "", clean_raw)
    return json.loads(clean_raw)


def _build_dynamic_system_prompt(dist: DifficultyDistribution) -> str:
    total_expected = dist.easy + dist.medium + dist.hard
    example_items = []
    if dist.easy > 0: example_items.append('{"difficulty": "easy", "question": "...", "answer": "..."}')
    if dist.medium > 0: example_items.append('{"difficulty": "medium", "question": "...", "answer": "..."}')
    if dist.hard > 0: example_items.append('{"difficulty": "hard", "question": "...", "answer": "..."}')
    json_template = ",\n    ".join(example_items)

    return f"""You are a senior technical interviewer.
Given a job description and optionally a candidate's resume, generate exactly {total_expected} technical interview questions broken down as follows:
- Easy questions: {dist.easy}
- Medium questions: {dist.medium}
- Hard questions: {dist.hard}

STRICT OUTPUT FORMAT — return only valid JSON, no markdown, no extra text:
{{
  "questions": [
    {json_template}
  ]
}}

Rules:
- Questions must be purely technical (no HR/culture questions)
- Answers should be thorough — 3 to 6 sentences
- Match the exact numbers requested for easy, medium, and hard fields
- Return ONLY the JSON object above, nothing else"""


# --- Endpoint Service Target 1: Static Generation (Original) ---

async def generate_questions(
    job_description: str,
    resume: Optional[str] = None,
    test_mode: bool = False,
) -> list[dict]:
    """Calls Ollama with qwen2.5:14b for the fixed 6-question endpoint."""
    expected_count = 1 if test_mode else 6
    prompt         = TEST_SYSTEM_PROMPT if test_mode else SYSTEM_PROMPT

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user",   "content": _build_user_prompt(job_description, resume)},
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 16384,     # Expanded memory token threshold limit
            "num_predict": 4096,  # Prevents truncation of complex answers
        },
    }

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        if resp.status_code == 404:
            payload_v1 = {
                "model": MODEL,
                "prompt": f"{prompt}\n\n{_build_user_prompt(job_description, resume)}",
                "stream": False,
                "options": payload["options"],
            }
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload_v1)
        resp.raise_for_status()

    body = resp.json()
    raw_content = body.get("message", {}).get("content") or body.get("response", "")

    # --- DEBUG CHANGE ---
    print("\n=== DEBUG: STATIC OLLAMA RAW OUTPUT START ===")
    print(raw_content)
    print("=== DEBUG: STATIC OLLAMA RAW OUTPUT END ===\n")

    parsed    = _extract_json(raw_content)
    questions = parsed.get("questions", [])

    if len(questions) != expected_count:
        raise ValueError(f"Expected {expected_count} question(s) from model, got {len(questions)}")

    return questions


# --- Endpoint Service Target 2: Dynamic Custom Generation (New) ---

async def generate_custom_questions(
    job_description: str,
    distribution: DifficultyDistribution,
    resume: Optional[str] = None,
) -> list[dict]:
    """Calls Ollama with dynamic difficulty distribution configurations."""
    expected_count = distribution.easy + distribution.medium + distribution.hard
    system_prompt  = _build_dynamic_system_prompt(distribution)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": _build_user_prompt(job_description, resume)},
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "top_p": 0.9,
            "num_ctx": 16384,     # Expanded memory token threshold limit
            "num_predict": 4096,  # Prevents truncation of complex answers
        },
    }

    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        if resp.status_code == 404:
            payload_v1 = {
                "model": MODEL,
                "prompt": f"{system_prompt}\n\n{_build_user_prompt(job_description, resume)}",
                "stream": False,
                "options": payload["options"],
            }
            resp = await client.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload_v1)
        resp.raise_for_status()

    body = resp.json()
    raw_content = body.get("message", {}).get("content") or body.get("response", "")

    # --- DEBUG CHANGE ---
    print("\n=== DEBUG: CUSTOM OLLAMA RAW OUTPUT START ===")
    print(raw_content)
    print("=== DEBUG: CUSTOM OLLAMA RAW OUTPUT END ===\n")

    parsed    = _extract_json(raw_content)
    questions = parsed.get("questions", [])

    if len(questions) != expected_count:
        raise ValueError(f"Expected {expected_count} questions from model, got {len(questions)}")

    return questions
