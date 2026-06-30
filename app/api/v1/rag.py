import httpx
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from app.api.dependencies import get_db
from app.schemas.rag import (
    KnowledgeDocumentListResponse,
    KnowledgeDocumentRead,
    RAGQueryRequest,
    RAGQueryResponse,
)
from app.services.rag_service import (
    EmbeddingConfigError,
    RAGError,
    RAGLLMConfigError,
    RAGService,
)


router = APIRouter(prefix="/rag", tags=["rag"])


@router.post(
    "/documents",
    response_model=KnowledgeDocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(default="安防知识"),
    db: Session = Depends(get_db),
):
    service = RAGService()
    try:
        return service.upload_document(
            db,
            filename=file.filename or "document",
            content_type=file.content_type,
            document_type=document_type,
            file=file.file,
        )
    except RAGError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except EmbeddingConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Embedding 调用失败: {exc}") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"知识库写入失败: {exc}") from exc


@router.get("/documents", response_model=KnowledgeDocumentListResponse)
def list_documents(db: Session = Depends(get_db)):
    return KnowledgeDocumentListResponse(items=RAGService().list_documents(db))


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    deleted = RAGService().delete_document(db, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="知识库文档不存在")
    return None


@router.post("/query", response_model=RAGQueryResponse)
def query_knowledge_base(payload: RAGQueryRequest, db: Session = Depends(get_db)):
    try:
        return RAGService().query(db, question=payload.question, top_k=payload.top_k)
    except EmbeddingConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except RAGLLMConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"RAG 模型调用失败: {exc}") from exc
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail=f"知识库查询失败: {exc}") from exc

