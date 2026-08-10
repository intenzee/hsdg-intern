from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import date, datetime
from typing import Optional, List


class ClientBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    entity_type: str
    pan: Optional[str] = Field(None, max_length=10)
    gstin: Optional[str] = Field(None, max_length=15)
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=20)
    partner_in_charge: str = Field(..., min_length=1, max_length=255)


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    pass


class ClientResponse(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceTaskBase(BaseModel):
    client_id: int
    task_type: str = Field(..., min_length=1, max_length=100)
    period_label: str = Field(..., min_length=1, max_length=50)
    due_date: date
    assignee: str = Field(..., min_length=1, max_length=255)
    status: str = Field(default="Not Started")


class ComplianceTaskCreate(ComplianceTaskBase):
    pass


class ComplianceTaskUpdate(BaseModel):
    task_type: Optional[str] = Field(None, min_length=1, max_length=100)
    period_label: Optional[str] = Field(None, min_length=1, max_length=50)
    due_date: Optional[date] = None
    assignee: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None


class ComplianceTaskResponse(ComplianceTaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceTaskWithClient(ComplianceTaskResponse):
    client: ClientResponse
    
    model_config = ConfigDict(from_attributes=True)


class ComplianceTaskWithDocuments(ComplianceTaskResponse):
    client: ClientResponse
    documents: List["TaskDocumentResponse"]
    
    model_config = ConfigDict(from_attributes=True)


class TaskDocumentBase(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255)
    is_received: bool = Field(default=False)


class TaskDocumentCreate(BaseModel):
    document_name: str = Field(..., min_length=1, max_length=255)
    is_received: bool = Field(default=False)


class TaskDocumentUpdate(BaseModel):
    is_received: bool


class TaskDocumentResponse(TaskDocumentBase):
    id: int
    task_id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class WorkloadSummary(BaseModel):
    assignee: str
    task_count: int
    
    model_config = ConfigDict(from_attributes=True)


class SeedResponse(BaseModel):
    message: str
    clients_created: int
    tasks_created: int
    documents_created: int
