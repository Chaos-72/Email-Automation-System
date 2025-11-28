
# backend/routes/ai_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from ..services.llm_service import parse_intent, generate_email

router = APIRouter(prefix="/api/ai", tags=["ai"])

class AnalyzeRequest(BaseModel):
    prompt: str

@router.post("/analyze")
def analyze(req: AnalyzeRequest):
    try:
        parsed = parse_intent(req.prompt)
        return {"ok": True, "parsed": parsed}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class GenerateEmailRequest(BaseModel):
    instruction: str
    recipient: Dict[str, Any] = None

@router.post("/generate-email")
def gen_email(req: GenerateEmailRequest):
    try:
        out = generate_email(req.instruction, req.recipient)
        return {"ok": True, "email": out}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
