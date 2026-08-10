from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import TaskDocument, ComplianceTask
from app.schemas import TaskDocumentCreate, TaskDocumentUpdate, TaskDocumentResponse

router = APIRouter(tags=["Documents"])


@router.post("/tasks/{task_id}/documents", response_model=TaskDocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(task_id: int, document: TaskDocumentCreate, db: Session = Depends(get_db)):
    task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db_document = TaskDocument(task_id=task_id, **document.model_dump())
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/tasks/{task_id}/documents", response_model=List[TaskDocumentResponse])
def list_task_documents(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    documents = db.query(TaskDocument).filter(TaskDocument.task_id == task_id).all()
    return documents


@router.patch("/documents/{document_id}", response_model=TaskDocumentResponse)
def update_document(document_id: int, document_update: TaskDocumentUpdate, db: Session = Depends(get_db)):
    db_document = db.query(TaskDocument).filter(TaskDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    db_document.is_received = document_update.is_received
    
    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(document_id: int, db: Session = Depends(get_db)):
    db_document = db.query(TaskDocument).filter(TaskDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    db.delete(db_document)
    db.commit()
    return None
