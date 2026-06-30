import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.nl2sql import NL2SQLQueryRequest, NL2SQLQueryResponse
from app.services.nl2sql_service import LLMConfigError, NL2SQLService, SQLSafetyError


router = APIRouter(prefix="/nl2sql", tags=["nl2sql"])


@router.post("/query", response_model=NL2SQLQueryResponse)
def query_nl2sql(payload: NL2SQLQueryRequest, db: Session = Depends(get_db)):
    service = NL2SQLService()
    try:
        return service.query(db, payload.question)
    except SQLSafetyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LLMConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"LLM 调用失败: {exc}") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"SQL 执行失败: {exc}") from exc
