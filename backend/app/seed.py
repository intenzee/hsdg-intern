"""
Seed script for populating the database with realistic test data.
Creates 15+ clients, 60+ tasks, and associated document checklists.
"""
from datetime import date, timedelta
from random import choice, randint, sample
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, Client, ComplianceTask, TaskDocument


# Realistic seed data
ENTITY_TYPES = ["Individual", "Company", "LLP", "Partnership", "Trust"]

PARTNERS = ["Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Reddy"]

ASSIGNEES = [
    "Vikram Singh",
    "Anjali Mehta", 
    "Rahul Verma",
    "Deepika Nair",
    "Arjun Desai",
    "Kavya Iyer"
]

TASK_TYPES = [
    "GSTR-3B",
    "GSTR-1", 
    "TDS",
    "GST Quarterly",
    "Income Tax Audit",
    "ROC Annual Filing"
]

STATUSES = ["Not Started", "In Progress", "Awaiting Client", "Filed"]

DOCUMENT_TEMPLATES = {
    "GSTR-3B": ["Sales Register", "Purchase Register", "ITC Statement", "Bank Statement"],
    "GSTR-1": ["Sales Register", "Tax Invoice Copies", "Credit Note Details"],
    "TDS": ["Salary Register", "TDS Computation", "Form 16", "Challan Copies"],
    "GST Quarterly": ["Sales Register", "Purchase Register", "ITC Statement", "Reconciliation Statement"],
    "Income Tax Audit": ["Balance Sheet", "P&L Statement", "Tax Audit Report", "Computation of Income", "Fixed Assets Register"],
    "ROC Annual Filing": ["Balance Sheet", "P&L Statement", "Directors Report", "Auditors Report", "AGM Notice"]
}

# Client name templates
CLIENT_PREFIXES = ["Tech", "Global", "Prime", "Royal", "Supreme", "Modern", "Elite", "Excel"]
CLIENT_SUFFIXES = ["Industries", "Enterprises", "Solutions", "Services", "Group", "Corporation", "Trading", "Manufacturing"]
INDIVIDUAL_NAMES = [
    "Rajesh Malhotra", "Sunita Kapoor", "Vijay Agarwal", "Meera Joshi", 
    "Sanjay Gupta", "Neha Chopra", "Manoj Kumar", "Pooja Sharma"
]


def generate_pan():
    """Generate a realistic-looking PAN number."""
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    return f"{choice(letters)}{choice(letters)}{choice(letters)}{choice(letters)}{choice(letters)}{choice(digits)}{choice(digits)}{choice(digits)}{choice(digits)}{choice(letters)}"


def generate_gstin():
    """Generate a realistic-looking GSTIN."""
    state_code = str(randint(1, 37)).zfill(2)
    pan = generate_pan()
    entity_number = str(randint(1, 9))
    z_letter = "Z"
    checksum = choice("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{state_code}{pan}{entity_number}{z_letter}{checksum}"


def create_clients(db: Session, count: int = 15):
    """Create realistic client records."""
    clients = []
    
    for i in range(count):
        if i < len(INDIVIDUAL_NAMES):
            # Create individual clients
            entity_type = "Individual"
            name = INDIVIDUAL_NAMES[i]
            gstin = None if randint(0, 1) else generate_gstin()
        else:
            # Create business clients
            entity_type = choice([e for e in ENTITY_TYPES if e != "Individual"])
            name = f"{choice(CLIENT_PREFIXES)} {choice(CLIENT_SUFFIXES)}"
            gstin = generate_gstin()
        
        client = Client(
            name=name,
            entity_type=entity_type,
            pan=generate_pan(),
            gstin=gstin,
            contact_name=f"Contact Person {i+1}",
            contact_email=f"contact{i+1}@example.com",
            contact_phone=f"+91 {''.join([str(randint(0,9)) for _ in range(10)])}",
            partner_in_charge=choice(PARTNERS)
        )
        clients.append(client)
    
    db.add_all(clients)
    db.commit()
    
    # Refresh to get IDs
    for client in clients:
        db.refresh(client)
    
    return clients


def create_tasks(db: Session, clients: list, count: int = 60):
    """Create realistic compliance tasks."""
    tasks = []
    base_date = date.today()
    
    # Ensure diverse task distribution
    tasks_per_client = count // len(clients) + 1
    
    for client in clients:
        # Create 3-5 tasks per client
        num_tasks = min(tasks_per_client, randint(3, 5))
        
        for _ in range(num_tasks):
            task_type = choice(TASK_TYPES)
            
            # Generate realistic period labels
            if task_type in ["GSTR-3B", "GSTR-1", "TDS"]:
                # Monthly tasks
                month_offset = randint(-2, 3)
                period_date = base_date + timedelta(days=30 * month_offset)
                period_label = period_date.strftime("%b %Y")
                due_offset = randint(0, 60)
            elif task_type == "GST Quarterly":
                # Quarterly tasks
                quarter = choice(["Q1", "Q2", "Q3", "Q4"])
                fy_year = "FY26"
                period_label = f"{quarter} {fy_year}"
                due_offset = randint(30, 120)
            else:
                # Annual tasks
                fy_start = randint(2024, 2026)
                fy_end = fy_start + 1
                period_label = f"FY {fy_start}-{str(fy_end)[2:]}"
                due_offset = randint(180, 365)
            
            due_date = base_date + timedelta(days=due_offset)
            
            # Weight statuses to create realistic distribution
            status_weights = ["Not Started"] * 3 + ["In Progress"] * 2 + ["Awaiting Client"] * 1 + ["Filed"] * 2
            status = choice(status_weights)
            
            task = ComplianceTask(
                client_id=client.id,
                task_type=task_type,
                period_label=period_label,
                due_date=due_date,
                assignee=choice(ASSIGNEES),
                status=status
            )
            tasks.append(task)
            
            if len(tasks) >= count:
                break
        
        if len(tasks) >= count:
            break
    
    db.add_all(tasks)
    db.commit()
    
    # Refresh to get IDs
    for task in tasks:
        db.refresh(task)
    
    return tasks


def create_documents(db: Session, tasks: list):
    """Create document checklists for tasks."""
    documents = []
    
    for task in tasks:
        # Get appropriate document template
        doc_template = DOCUMENT_TEMPLATES.get(task.task_type, ["Document 1", "Document 2", "Document 3"])
        
        # Create 2-5 documents per task
        num_docs = min(len(doc_template), randint(2, 5))
        selected_docs = sample(doc_template, num_docs)
        
        for doc_name in selected_docs:
            # Randomly set some documents as received
            is_received = choice([True, False, False])  # 33% received
            
            document = TaskDocument(
                task_id=task.id,
                document_name=doc_name,
                is_received=is_received
            )
            documents.append(document)
    
    db.add_all(documents)
    db.commit()
    
    return documents


def seed_database():
    """Main seed function - drops existing data and creates fresh seed data."""
    print("Starting database seeding...")
    
    # Create tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        db.query(TaskDocument).delete()
        db.query(ComplianceTask).delete()
        db.query(Client).delete()
        db.commit()
        
        # Create seed data
        print("Creating 15+ clients...")
        clients = create_clients(db, count=18)
        print(f"✓ Created {len(clients)} clients")
        
        print("Creating 60+ compliance tasks...")
        tasks = create_tasks(db, clients, count=65)
        print(f"✓ Created {len(tasks)} tasks")
        
        print("Creating document checklists...")
        documents = create_documents(db, tasks)
        print(f"✓ Created {len(documents)} document items")
        
        print("\n" + "="*50)
        print("✓ Database seeding completed successfully!")
        print("="*50)
        print(f"Summary:")
        print(f"  - Clients: {len(clients)}")
        print(f"  - Tasks: {len(tasks)}")
        print(f"  - Documents: {len(documents)}")
        print("="*50 + "\n")
        
        return {
            "clients_created": len(clients),
            "tasks_created": len(tasks),
            "documents_created": len(documents)
        }
        
    except Exception as e:
        print(f"✗ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
