from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.database import get_db
from app.models import Client, ComplianceTask, TaskDocument
from app.schemas import TaskGenerateRequest, TaskGenerateResponse
from app.recurrence import (
    RECURRENCE_RULES,
    DOCUMENT_TEMPLATES,
    get_period_label,
    get_due_date,
    get_task_types_for_month,
    round_robin_assignee,
)

router = APIRouter(prefix="/tasks", tags=["Task Generation"])


@router.post(
    "/generate",
    response_model=TaskGenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate recurring compliance tasks for a given month/year",
    description=(
        "Generates compliance tasks for all clients based on recurrence rules. "
        "Running it multiple times for the same period is safe — existing tasks "
        "for a (client, task_type, period_label) combo are skipped."
    ),
)
def generate_tasks(request: TaskGenerateRequest, db: Session = Depends(get_db)):
    year = request.year
    month = request.month
    period_str = date(year, month, 1).strftime("%B %Y")

    # Determine which task types apply this month
    applicable_task_types = get_task_types_for_month(year, month)
    if not applicable_task_types:
        return TaskGenerateResponse(
            period=period_str,
            tasks_created=0,
            tasks_skipped=0,
            documents_created=0,
        )

    # Fetch all clients
    clients: List[Client] = db.query(Client).all()
    if not clients:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No clients found. Run /seed first.",
        )

    tasks_created = 0
    tasks_skipped = 0
    documents_created = 0

    for task_type in applicable_task_types:
        period_label = get_period_label(task_type, year, month)
        due_date = get_due_date(task_type, year, month)
        doc_templates = DOCUMENT_TEMPLATES.get(task_type, ["Document 1"])

        if period_label is None or due_date is None:
            continue

        for client in clients:
            # ── Idempotency check ────────────────────────────────────────────
            existing = (
                db.query(ComplianceTask)
                .filter(
                    ComplianceTask.client_id == client.id,
                    ComplianceTask.task_type == task_type,
                    ComplianceTask.period_label == period_label,
                )
                .first()
            )
            if existing:
                tasks_skipped += 1
                continue

            # ── Create the task ──────────────────────────────────────────────
            assignee = round_robin_assignee(client.id, task_type)
            new_task = ComplianceTask(
                client_id=client.id,
                task_type=task_type,
                period_label=period_label,
                due_date=due_date,
                assignee=assignee,
                status="Not Started",
            )
            db.add(new_task)
            db.flush()  # get new_task.id without committing yet

            # ── Create default documents ─────────────────────────────────────
            for doc_name in doc_templates:
                doc = TaskDocument(
                    task_id=new_task.id,
                    document_name=doc_name,
                    is_received=False,
                )
                db.add(doc)
                documents_created += 1

            tasks_created += 1

    db.commit()

    return TaskGenerateResponse(
        period=period_str,
        tasks_created=tasks_created,
        tasks_skipped=tasks_skipped,
        documents_created=documents_created,
    )
