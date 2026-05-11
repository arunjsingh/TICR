# app/services/ollama_service.py
import httpx
import json
import re
from typing import Optional

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


def _build_user_prompt(job_description: str, resume: Optional[str]) -> str:
    prompt = f"Job Description:\n{job_description}"
    if resume:
        prompt += f"\n\nCandidate Resume:\n{resume}"
    return prompt


def _extract_json(raw: str) -> dict:
    """Strips markdown fences if the model ignores the system prompt."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


async def generate_questions(
    job_description: str,
    resume: Optional[str] = None,
    test_mode: bool = False,
) -> list[dict]:
    """
    Calls Ollama with qwen2.5:14b and returns a list of question dicts.
    test_mode=True returns 1 easy question instead of 6.
    """
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
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
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

    parsed    = _extract_json(raw_content)
    questions = parsed.get("questions", [])

    if len(questions) != expected_count:
        raise ValueError(f"Expected {expected_count} question(s) from model, got {len(questions)}")

    return questions