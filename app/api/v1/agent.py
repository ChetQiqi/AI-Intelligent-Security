from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.agent import AgentAnalyzeRequest, AgentAnalyzeResponse
from app.services.agent_service import analyze_security_situation


router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/analyze", response_model=AgentAnalyzeResponse)
def analyze(payload: AgentAnalyzeRequest, db: Session = Depends(get_db)):
    return analyze_security_situation(
        db,
        question=payload.question,
        days=payload.days,
    )
