from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import date, timedelta
from app.database import get_db
from app.models import ComplianceTask, Client
from app.schemas import (
    ComplianceTaskCreate,
    ComplianceTaskUpdate,
    ComplianceTaskResponse,
    ComplianceTaskWithClient,
    ComplianceTaskWithDocuments,
    WorkloadSummary,
    DashboardResponse,
    DashboardSummary,
    WorkloadBreakdown,
)

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# ── CRUD ──────────────────────────────────────────────────────────────────────

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
    db: Session = Depends(get_db),
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


# ── Dashboard endpoints (MUST come before /{task_id} to avoid route conflicts)

@router.get("/dashboard", tags=["Dashboard"], response_model=DashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    """
    Consolidated dashboard endpoint.
    Returns summary counts + task lists for due_this_week, overdue,
    awaiting_client, and a per-assignee workload breakdown by status.
    """
    today = date.today()
    week_from_now = today + timedelta(days=7)

    # due this week (non-Filed only)
    due_this_week = (
        db.query(ComplianceTask)
        .filter(
            and_(
                ComplianceTask.due_date >= today,
                ComplianceTask.due_date <= week_from_now,
                ComplianceTask.status != "Filed",
            )
        )
        .all()
    )

    # overdue: past due date and not Filed
    overdue = (
        db.query(ComplianceTask)
        .filter(
            and_(
                ComplianceTask.due_date < today,
                ComplianceTask.status != "Filed",
            )
        )
        .all()
    )

    # awaiting client input
    awaiting_client = (
        db.query(ComplianceTask)
        .filter(ComplianceTask.status == "Awaiting Client")
        .all()
    )

    # total open tasks
    total_open = (
        db.query(func.count(ComplianceTask.id))
        .filter(ComplianceTask.status != "Filed")
        .scalar()
        or 0
    )

    # workload breakdown per assignee per status
    rows = (
        db.query(
            ComplianceTask.assignee,
            ComplianceTask.status,
            func.count(ComplianceTask.id).label("cnt"),
        )
        .group_by(ComplianceTask.assignee, ComplianceTask.status)
        .all()
    )

    workload_map: dict = {}
    for assignee, status_val, cnt in rows:
        if assignee not in workload_map:
            workload_map[assignee] = {
                "Not Started": 0,
                "In Progress": 0,
                "Awaiting Client": 0,
                "Filed": 0,
            }
        workload_map[assignee][status_val] = cnt

    workload_list = [
        WorkloadBreakdown(
            assignee=assignee,
            not_started=counts.get("Not Started", 0),
            in_progress=counts.get("In Progress", 0),
            awaiting_client=counts.get("Awaiting Client", 0),
            filed=counts.get("Filed", 0),
            total=sum(counts.values()),
        )
        for assignee, counts in sorted(workload_map.items())
    ]

    return DashboardResponse(
        summary=DashboardSummary(
            due_this_week_count=len(due_this_week),
            overdue_count=len(overdue),
            awaiting_client_count=len(awaiting_client),
            total_open_tasks=total_open,
        ),
        due_this_week=due_this_week,
        overdue=overdue,
        awaiting_client=awaiting_client,
        workload_per_assignee=workload_list,
    )


@router.get("/dashboard/due-this-week", response_model=List[ComplianceTaskWithClient])
def get_tasks_due_this_week(db: Session = Depends(get_db)):
    today = date.today()
    week_from_now = today + timedelta(days=7)
    tasks = db.query(ComplianceTask).filter(
        and_(
            ComplianceTask.due_date >= today,
            ComplianceTask.due_date <= week_from_now,
        )
    ).all()
    return tasks


@router.get("/dashboard/overdue", response_model=List[ComplianceTaskWithClient])
def get_overdue_tasks(db: Session = Depends(get_db)):
    today = date.today()
    tasks = db.query(ComplianceTask).filter(
        and_(
            ComplianceTask.due_date < today,
            ComplianceTask.status != "Filed",
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
    workload = db.query(
        ComplianceTask.assignee,
        func.count(ComplianceTask.id).label("task_count"),
    ).filter(
        ComplianceTask.status != "Filed"
    ).group_by(
        ComplianceTask.assignee
    ).all()
    return [{"assignee": a, "task_count": c} for a, c in workload]


# ── Single-item routes (AFTER all path-specific routes) ───────────────────────

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
