"""
Recurrence rules for CA firm compliance tasks.

Each rule defines:
  - frequency: "monthly" | "quarterly" | "annual"
  - due_day: day of month the task is due
  - due_month: (annual only) calendar month the task is due
  - due_months_offset: months after period end when due (e.g., 1 = next month)
  - quarter_months: (quarterly only) which months start each quarter
"""
from datetime import date
from calendar import monthrange
from typing import Optional

# ── Recurrence Config ─────────────────────────────────────────────────────────
# Each entry: task_type → rule dict
RECURRENCE_RULES: dict = {
    "GSTR-3B": {
        "frequency": "monthly",
        "due_day": 20,
        "due_months_offset": 1,   # due on 20th of the NEXT month
        "description": "Monthly GST return, due 20th of the following month",
    },
    "GSTR-1": {
        "frequency": "monthly",
        "due_day": 11,
        "due_months_offset": 1,   # due on 11th of the NEXT month
        "description": "Monthly GST outward supplies return, due 11th of next month",
    },
    "TDS": {
        "frequency": "monthly",
        "due_day": 7,
        "due_months_offset": 1,   # due on 7th of the NEXT month
        "description": "Monthly TDS deposit, due 7th of the following month",
    },
    "GST Quarterly": {
        "frequency": "quarterly",
        "due_day": 30,
        "due_months_offset": 1,   # due 30th of the month AFTER quarter end
        # Quarter end months: Mar(Q4), Jun(Q1), Sep(Q2), Dec(Q3)
        "quarter_end_months": [3, 6, 9, 12],
        "description": "Quarterly GST return for composition dealers, due 30th of following month",
    },
    "Income Tax Audit": {
        "frequency": "annual",
        "due_day": 30,
        "due_month": 9,           # Due 30 September each FY
        "description": "Annual income tax audit, due 30 September",
    },
    "ROC Annual Filing": {
        "frequency": "annual",
        "due_day": 30,
        "due_month": 11,          # Due 30 November each FY
        "description": "Annual ROC filing, due 30 November",
    },
}

# Document templates per task type (same as seed.py for consistency)
DOCUMENT_TEMPLATES: dict = {
    "GSTR-3B": ["Sales Register", "Purchase Register", "ITC Statement", "Bank Statement"],
    "GSTR-1": ["Sales Register", "Tax Invoice Copies", "Credit Note Details"],
    "TDS": ["Salary Register", "TDS Computation", "Form 16", "Challan Copies"],
    "GST Quarterly": ["Sales Register", "Purchase Register", "ITC Statement", "Reconciliation Statement"],
    "Income Tax Audit": ["Balance Sheet", "P&L Statement", "Tax Audit Report", "Computation of Income", "Fixed Assets Register"],
    "ROC Annual Filing": ["Balance Sheet", "P&L Statement", "Directors Report", "Auditors Report", "AGM Notice"],
}

ASSIGNEES = [
    "Vikram Singh",
    "Anjali Mehta",
    "Rahul Verma",
    "Deepika Nair",
    "Arjun Desai",
    "Kavya Iyer",
]


# ── Helper Functions ──────────────────────────────────────────────────────────

def get_period_label(task_type: str, year: int, month: int) -> Optional[str]:
    """
    Return a human-readable period label for a task type in a given year/month.
    Returns None if this task_type should not be generated for this month.
    """
    rule = RECURRENCE_RULES.get(task_type)
    if not rule:
        return None

    freq = rule["frequency"]

    if freq == "monthly":
        # Always applies — label is the period month (the month being filed FOR)
        month_name = date(year, month, 1).strftime("%b %Y")
        return month_name

    elif freq == "quarterly":
        quarter_end_months = rule.get("quarter_end_months", [3, 6, 9, 12])
        if month not in quarter_end_months:
            return None
        # Determine quarter label
        quarter_map = {3: "Q4", 6: "Q1", 9: "Q2", 12: "Q3"}
        quarter = quarter_map.get(month, "Q?")
        fy_label = f"FY{str(year)[2:]}" if month > 3 else f"FY{str(year - 1)[2:]}"
        return f"{quarter} {fy_label}"

    elif freq == "annual":
        # Only generate in the due month
        due_month = rule.get("due_month")
        if month != due_month:
            return None
        # Financial year label: Apr YYYY – Mar YYYY+1
        if month <= 3:
            fy_start = year - 1
        else:
            fy_start = year
        fy_end = fy_start + 1
        return f"FY {fy_start}-{str(fy_end)[2:]}"

    return None


def get_due_date(task_type: str, year: int, month: int) -> Optional[date]:
    """
    Return the due date for a task_type for the given year/month period.
    """
    rule = RECURRENCE_RULES.get(task_type)
    if not rule:
        return None

    freq = rule["frequency"]
    due_day = rule["due_day"]

    if freq == "monthly":
        offset = rule.get("due_months_offset", 1)
        due_month = month + offset
        due_year = year
        if due_month > 12:
            due_month -= 12
            due_year += 1
        # Clamp to last day of month if due_day > month length
        max_day = monthrange(due_year, due_month)[1]
        actual_day = min(due_day, max_day)
        return date(due_year, due_month, actual_day)

    elif freq == "quarterly":
        quarter_end_months = rule.get("quarter_end_months", [3, 6, 9, 12])
        if month not in quarter_end_months:
            return None
        offset = rule.get("due_months_offset", 1)
        due_month = month + offset
        due_year = year
        if due_month > 12:
            due_month -= 12
            due_year += 1
        max_day = monthrange(due_year, due_month)[1]
        actual_day = min(due_day, max_day)
        return date(due_year, due_month, actual_day)

    elif freq == "annual":
        due_month = rule.get("due_month", month)
        if month != due_month:
            return None
        max_day = monthrange(year, due_month)[1]
        actual_day = min(due_day, max_day)
        return date(year, due_month, actual_day)

    return None


def get_task_types_for_month(year: int, month: int) -> list[str]:
    """Return all task types that should be generated for the given year/month."""
    result = []
    for task_type in RECURRENCE_RULES:
        label = get_period_label(task_type, year, month)
        if label is not None:
            result.append(task_type)
    return result


def round_robin_assignee(client_id: int, task_type: str) -> str:
    """Deterministically assign based on client_id + task_type to spread load evenly."""
    index = (client_id + hash(task_type)) % len(ASSIGNEES)
    return ASSIGNEES[abs(index)]
