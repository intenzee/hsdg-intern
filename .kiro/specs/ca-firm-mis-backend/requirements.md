# Requirements Document

## Introduction

This document specifies the requirements for a CA Firm MIS (Management Information System) backend API. The system replaces Excel-based compliance tracking with a structured database-driven solution. It manages client data, compliance tasks, document checklists, and provides dashboard views for tracking work status. This is a Day 1 production-quality backend implementation focused on core compliance tracking workflows for a CA firm.

## Glossary

- **CA_Firm_MIS**: The Management Information System backend API for tracking compliance tasks
- **Client**: A business entity that the CA firm serves, identified by name, entity type, and tax identifiers
- **Compliance_Task**: A specific compliance activity (tax filing, audit, ROC filing) with due date and status
- **Task_Type**: Category of compliance work (GSTR-3B, GSTR-1, TDS, Income Tax Audit, ROC Annual Filing)
- **Task_Period**: Time period for compliance (monthly, quarterly, annual) with specific format
- **Task_Status**: Current state of a task (Not Started, In Progress, Awaiting Client, Filed)
- **Document_Checklist**: List of required documents for a compliance task
- **Document_Item**: Individual document in a checklist with received/pending status
- **Assignee**: Team member responsible for completing a task
- **Partner_In_Charge**: Senior CA partner responsible for a client relationship
- **Recurring_Task**: Compliance task that auto-generates on monthly, quarterly, or annual basis
- **Dashboard**: Aggregated views showing tasks requiring attention
- **Seed_Data**: Pre-loaded realistic data for system initialization

## Requirements

### Requirement 1: Manage Client Master Data

**User Story:** As a CA firm administrator, I want to manage client master records, so that I can maintain accurate client information and relationships.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL store Client records with name, entity type, PAN, GSTIN, contact information, and Partner_In_Charge
2. WHEN a create client request is received with valid data, THE CA_Firm_MIS SHALL create a new Client record and return the Client identifier
3. WHEN an update client request is received with valid data and existing Client identifier, THE CA_Firm_MIS SHALL update the Client record
4. WHEN a list clients request is received, THE CA_Firm_MIS SHALL return all Client records with their attributes
5. WHEN a delete client request is received with existing Client identifier, THE CA_Firm_MIS SHALL remove the Client record
6. WHEN a client request contains invalid data, THE CA_Firm_MIS SHALL return a descriptive validation error

### Requirement 2: Manage Compliance Tasks

**User Story:** As a CA firm team member, I want to create and track compliance tasks per client, so that I can ensure timely completion of filing obligations.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL store Compliance_Task records with Client reference, Task_Type, Task_Period, due date, Assignee, and Task_Status
2. WHEN a create task request is received with valid data, THE CA_Firm_MIS SHALL create a new Compliance_Task and return the task identifier
3. WHEN an update task request is received with valid data and existing task identifier, THE CA_Firm_MIS SHALL update the Compliance_Task record
4. WHEN a list tasks request is received, THE CA_Firm_MIS SHALL return all Compliance_Task records with their attributes
5. WHEN a delete task request is received with existing task identifier, THE CA_Firm_MIS SHALL remove the Compliance_Task record
6. WHEN a task status update is received, THE CA_Firm_MIS SHALL update the Task_Status to the new value
7. THE CA_Firm_MIS SHALL support Task_Period formats for monthly ("Jul 2026"), quarterly ("Q2 FY26"), and annual ("FY 2025-26") periods

### Requirement 3: Manage Document Checklists per Task

**User Story:** As a CA team member, I want to track required documents for each task, so that I can identify missing information before filing.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL store Document_Checklist records linked to Compliance_Task records
2. THE CA_Firm_MIS SHALL store Document_Item records with name and received status (true or false)
3. WHEN a create document item request is received for a task, THE CA_Firm_MIS SHALL add the Document_Item to the task's checklist
4. WHEN an update document item request is received, THE CA_Firm_MIS SHALL update the Document_Item received status
5. WHEN a get task checklist request is received, THE CA_Firm_MIS SHALL return all Document_Item records for that Compliance_Task
6. WHEN a delete document item request is received, THE CA_Firm_MIS SHALL remove the Document_Item from the checklist

### Requirement 4: Auto-Generate Recurring Compliance Tasks

**User Story:** As a CA firm administrator, I want the system to automatically create recurring compliance tasks, so that I don't manually create monthly, quarterly, and annual obligations.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL define recurring task generation rules based on Task_Type and frequency (monthly, quarterly, annual)
2. WHEN a recurring task generation is triggered for monthly tasks, THE CA_Firm_MIS SHALL create Compliance_Task records for each eligible Client for the target month
3. WHEN a recurring task generation is triggered for quarterly tasks, THE CA_Firm_MIS SHALL create Compliance_Task records for each eligible Client for the target quarter
4. WHEN a recurring task generation is triggered for annual tasks, THE CA_Firm_MIS SHALL create Compliance_Task records for each eligible Client for the target year
5. WHEN generating recurring tasks, THE CA_Firm_MIS SHALL set appropriate due dates based on Task_Type rules
6. THE CA_Firm_MIS SHALL prevent duplicate task generation for the same Client, Task_Type, and Task_Period combination

### Requirement 5: Provide Dashboard Views

**User Story:** As a CA firm partner, I want to see dashboard views of critical tasks, so that I can prioritize work and identify bottlenecks.

#### Acceptance Criteria

1. WHEN a dashboard request is received for tasks due this week, THE CA_Firm_MIS SHALL return all Compliance_Task records with due dates within the next 7 days
2. WHEN a dashboard request is received for overdue tasks, THE CA_Firm_MIS SHALL return all Compliance_Task records with due dates before today and Task_Status not equal to "Filed"
3. WHEN a dashboard request is received for tasks awaiting client, THE CA_Firm_MIS SHALL return all Compliance_Task records with Task_Status equal to "Awaiting Client"
4. WHEN a dashboard request is received for workload per assignee, THE CA_Firm_MIS SHALL return counts of non-filed Compliance_Task records grouped by Assignee
5. THE CA_Firm_MIS SHALL include Client name and task details in all dashboard responses

### Requirement 6: Filter Compliance Tasks

**User Story:** As a CA team member, I want to filter tasks by multiple criteria, so that I can find specific tasks quickly.

#### Acceptance Criteria

1. WHEN a filter request is received with Client identifier, THE CA_Firm_MIS SHALL return Compliance_Task records for that Client
2. WHEN a filter request is received with Assignee identifier, THE CA_Firm_MIS SHALL return Compliance_Task records assigned to that team member
3. WHEN a filter request is received with Task_Status, THE CA_Firm_MIS SHALL return Compliance_Task records matching that status
4. WHEN a filter request is received with Task_Type, THE CA_Firm_MIS SHALL return Compliance_Task records of that type
5. WHEN a filter request is received with date range (start and end dates), THE CA_Firm_MIS SHALL return Compliance_Task records with due dates within that range
6. WHEN a filter request is received with multiple criteria, THE CA_Firm_MIS SHALL return Compliance_Task records matching all specified criteria (AND logic)

### Requirement 7: Initialize System with Seed Data

**User Story:** As a developer, I want the system to load realistic seed data on initialization, so that the system can be demonstrated with production-like data.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL provide a seed data script that creates at least 15 Client records with realistic CA firm client attributes
2. THE CA_Firm_MIS SHALL provide a seed data script that creates at least 60 Compliance_Task records across multiple clients and task types
3. THE CA_Firm_MIS SHALL provide a seed data script that creates 2 to 5 Document_Item records per Compliance_Task
4. WHEN the seed data script is executed, THE CA_Firm_MIS SHALL populate the database with all Client, Compliance_Task, and Document_Item records
5. THE CA_Firm_MIS SHALL ensure seed data includes diverse entity types, task types, periods, statuses, and assignees
6. THE CA_Firm_MIS SHALL ensure seed data persists across container restarts using Docker volumes

### Requirement 8: Run System via Docker Compose

**User Story:** As a developer, I want to run the entire system with a single command, so that I can quickly set up the development environment.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL provide a Docker Compose configuration that starts the FastAPI backend and PostgreSQL database
2. WHEN the command "docker compose up --build" is executed, THE CA_Firm_MIS SHALL start all required services
3. THE CA_Firm_MIS SHALL automatically run database migrations on container startup
4. THE CA_Firm_MIS SHALL automatically execute the seed data script after migrations complete
5. THE CA_Firm_MIS SHALL persist database data using Docker volumes across container restarts
6. THE CA_Firm_MIS SHALL expose the FastAPI API on a documented port accessible from the host machine

### Requirement 9: Provide API Documentation

**User Story:** As a developer, I want to access interactive API documentation, so that I can understand and test available endpoints.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL expose OpenAPI (Swagger) documentation at the "/docs" endpoint
2. WHEN the "/docs" endpoint is accessed, THE CA_Firm_MIS SHALL display interactive API documentation for all endpoints
3. THE CA_Firm_MIS SHALL include request schemas, response schemas, and status codes in the API documentation
4. THE CA_Firm_MIS SHALL expose ReDoc documentation at the "/redoc" endpoint as an alternative documentation view

### Requirement 10: Validate Data Integrity

**User Story:** As a system administrator, I want the system to enforce data integrity constraints, so that the database remains consistent and reliable.

#### Acceptance Criteria

1. THE CA_Firm_MIS SHALL enforce foreign key constraints between Compliance_Task and Client records
2. THE CA_Firm_MIS SHALL enforce foreign key constraints between Document_Item and Compliance_Task records
3. WHEN a Client deletion is attempted with existing Compliance_Task records, THE CA_Firm_MIS SHALL prevent deletion and return an error
4. WHEN a Compliance_Task deletion is attempted with existing Document_Item records, THE CA_Firm_MIS SHALL cascade delete all related Document_Item records
5. THE CA_Firm_MIS SHALL enforce required field constraints on all entity attributes marked as mandatory
6. THE CA_Firm_MIS SHALL enforce unique constraints on Client PAN and GSTIN fields where provided
