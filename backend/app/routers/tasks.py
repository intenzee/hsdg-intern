from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import ComplianceTask, Client
from app.schemas import (
    ComplianceTaskCreate,
    ComplianceTaskUpdate,
    ComplianceTaskResponse,
    ComplianceTaskWithClient,
    ComplianceTaskWithDocuments,
    WorkloadSummary
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("", response_model=ComplianceTaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: ComplianceTaskCreate, db: Session = Depends(get_db)):
    client = db.query(Client).filter(Client.id == task.client_id).first()
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    valid_statuses = ["Not Started", "In Progress", "Awaiting Client", "Filed"]
    if task.status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    
    db_task = ComplianceTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.get("", response_model=List[ComplianceTaskWithClient])
def list_tasks(
    client_id: Optional[int] = Query(None),
    assignee: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    task_type: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None),
    date_to: Optional[date] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceTask)
    
    filters = []
    if client_id is not None:
        filters.append(ComplianceTask.client_id == client_id)
    if assignee:
        filters.append(ComplianceTask.assignee == assignee)
    if status:
        filters.append(ComplianceTask.status == status)
    if task_type:
        filters.append(ComplianceTask.task_type == task_type)
    if date_from:
        filters.append(ComplianceTask.due_date >= date_from)
    if date_to:
        filters.append(ComplianceTask.due_date <= date_to)
    
    if filters:
        query = query.filter(and_(*filters))
    
    tasks = query.offset(skip).limit(limit).all()
    return tasks


@router.get("/{task_id}", response_model=ComplianceTaskWithDocuments)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=ComplianceTaskResponse)
def update_task(task_id: int, task_update: ComplianceTaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task_update.status:
        valid_statuses = ["Not Started", "In Progress", "Awaiting Client", "Filed"]
        if task_update.status not in valid_statuses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(ComplianceTask).filter(ComplianceTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db.delete(db_task)
    db.commit()
    return None


@router.get("/dashboard/due-this-week", response_model=List[ComplianceTaskWithClient])
def get_tasks_due_this_week(db: Session = Depends(get_db)):
    today = date.today()
    week_from_now = today + timedelta(days=7)
    
    tasks = db.query(ComplianceTask).filter(
        and_(
            ComplianceTask.due_date >= today,
            ComplianceTask.due_date <= week_from_now
        )
    ).all()
    
    return tasks


@router.get("/dashboard/overdue", response_model=List[ComplianceTaskWithClient])
def get_overdue_tasks(db: Session = Depends(get_db)):
    today = date.today()
    
    tasks = db.query(ComplianceTask).filter(
        and_(
            ComplianceTask.due_date < today,
            ComplianceTask.status != "Filed"
        )
    ).all()
    
    return tasks


@router.get("/dashboard/awaiting-client", response_model=List[ComplianceTaskWithClient])
def get_tasks_awaiting_client(db: Session = Depends(get_db)):
    tasks = db.query(ComplianceTask).filter(
        ComplianceTask.status == "Awaiting Client"
    ).all()
    
    return tasks


@router.get("/dashboard/workload", response_model=List[WorkloadSummary])
def get_workload_by_assignee(db: Session = Depends(get_db)):
    from sqlalchemy import func
    
    workload = db.query(
        ComplianceTask.assignee,
        func.count(ComplianceTask.id).label("task_count")
    ).filter(
        ComplianceTask.status != "Filed"
    ).group_by(
        ComplianceTask.assignee
    ).all()
    
    return [{"assignee": assignee, "task_count": count} for assignee, count in workload]
