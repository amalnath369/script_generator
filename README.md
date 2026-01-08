# Story2Screenplay API

A robust REST API service that converts user-submitted stories into screenplays using a Large Language Model (LLM) integration. The service bridges a PostgreSQL database with the OpenRouter.ai LLM API, handling rate limits and background tasks asynchronously.


# 1. Problem Understanding & Assumptions

Interpretation:
The goal is to create a REST API that converts user-submitted stories into screenplays using a Large Language Model (LLM) integration. This involves accepting story inputs, processing them asynchronously, and returning structured screenplay outputs.

**Use Case:**

A writer submits a story via API.

The system generates a screenplay automatically using an LLM (OpenRouter.ai) and returns it.

Supports high concurrency and handles external API rate limits.

**Assumptions:**
No user authentication in version 1; all submissions are treated anonymously.

Each story is plain text with a maximum length of 5000 characters.

OpenRouter.ai API reliably returns screenplay text in JSON.

Rate limiting: 5 LLM requests per minute per client IP.

Pagination is applied for retrieving previously generated screenplays.

Redis & Celery handle background task queuing, ensuring non-blocking responses.



# 2. Design Decisions

**Clean Architecture & Framework Independence**

    The project follows Clean Architecture principles to ensure long-term maintainability, testability, and flexibility.

    The core idea is dependency inversion:

    High-level business rules do not depend on frameworks, databases, or external services.

    Architectural Layers
    Domain → Application / Use Cases → Infrastructure → API (FastAPI)


    Domain Layer

    Contains pure Python dataclasses (Script, GeneratedScript) and enums.

    No dependency on FastAPI, SQLAlchemy, or PostgreSQL.

    Responsible only for business rules and validation.

    Example: content length validation, immutable status updates.

    Application / Use Case Layer

    Orchestrates workflows (e.g., create script → enqueue LLM task → update status).

    Depends only on domain interfaces, not implementations.

    Infrastructure Layer

    Contains SQLAlchemy models, repositories, Redis, Celery, and OpenRouter integrations.

    Implements interfaces defined by the application layer.

    API Layer

    FastAPI routes, request/response schemas.

    Responsible only for HTTP concerns (status codes, request parsing).

    This separation ensures that business logic remains isolated and reusable, regardless of delivery mechanism.


**Database Independence**

    Although PostgreSQL is used in version 1, the domain layer does not depend on SQLAlchemy or PostgreSQL.

    Domain entities are implemented using Python @dataclass.

    SQLAlchemy models exist only in the infrastructure layer.

    Communication between domain and database is handled via repository patterns.

    Why this matters

    If tomorrow:

    PostgreSQL → MySQL / MongoDB

    SQLAlchemy → another ORM

    Database → external storage service

    Only the infrastructure layer needs to change.
    The domain logic and use cases remain untouched.

    Framework Independence

    FastAPI is used as the web framework, but:

    No FastAPI imports exist in the domain layer.

    Business logic is not tied to request/response objects.

    Validation rules live inside domain entities, not route handlers.

    Future Flexibility

    This allows easy migration to:

    Django / Flask

    gRPC

    CLI-based execution

    Background-only worker services

    Without rewriting business rules.


**Database Schema:**

scripts table: stores original story submissions.

generated_scripts table: stores LLM-generated screenplays.

Both tables inherit from BaseDBModel (with id, created_at, updated_at).

Indexed name,tags,field for faster querying in scripts and also do the same in generated_scripts along with model name(which model genrated the data).

tags stored as an array for categorization.

status field is an Enum to track workflow: PENDING, PROCESSING, COMPLETED, FAILED.



# 3️. Solution Approach

Data Flow:

    User submits a story via POST /convert.

    API checks rate limits; rejects if exceeded.

    Task is enqueued in Celery for async processing.

    Celery worker calls OpenRouter.ai to generate screenplay.

    Result is persisted in generated_scripts table.

    Users can fetch results via GET /screenplays?page=1&size=20.


# 4️. Error Handling Strategy

Database errors: wrapped in try-except, return 404,401,400 , 500 accordingly.

LLM downtime / API errors: retries with exponential backoff.

Rate limit exceeded: 429 HTTP response.

FastAPI global exception handlers used to handle uncaught exceptions consistently.


# 5️. How to Run the Project

    Requirements:

    Python 3.11+

    PostgreSQL

    Redis

    Docker & Docker Compose

    Setup Instructions:

    Clone the repository
            git clone https://github.com/amalnath369/script_generator.git

    Create environment variables
    
    Start services using Docker Compose

            docker-compose up --build

    Run database migrations
        docker-compose exec api alembic upgrade head

# 6. API Calls

All endpoints are exposed via FastAPI and documented using OpenAPI (Swagger).

    Base URL: http://localhost:8000

    Swagger UI: http://localhost:8000/docs

Script Management APIs

These endpoints manage original story scripts submitted by users.

**1️ Create Script**
        POST /scripts/

        Creates a new script entry in the system.

        Rate Limit: 5 requests/minute

        Purpose: Store user story content and metadata for further processing.

        Request Body:

        {
        "name": "Sample Story",
        "content": "Once upon a time...",
        "tags": ["fantasy", "drama"]
        }


        Response: 201 Created

        {
        "id": "uuid",
        "name": "Sample Story",
        "content": "Once upon a time...",
        "tags": ["fantasy", "drama"],
        "status": "PENDING"
        }


**2️ List All Scripts (Paginated)**

        GET /scripts/list_all

        Fetches all scripts with pagination support.

        Rate Limit: 10 requests/minute

        Purpose: Retrieve stored scripts efficiently without overloading the database.

        Query Parameters:

        limit – number of records per page

        offset – starting index

        Response: 200 OK


**3️. Read Script by ID**

        GET /scripts/{script_id}

        Retrieves a single script using its unique identifier.

        Purpose: Fetch script details for review or processing.

        Response: 200 OK
        Errors: 404 Not Found if script does not exist

**4️. Update Script Fields**

    PUT /scripts/{script_id}/status

    Updates script metadata such as name, content, or tags.

    Purpose: Modify an existing script without recreating it.

    Optional Query Parameters:

    name

    content

    tags

**5️. Delete Script**

    DELETE /scripts/{script_id}

    Deletes a script permanently.

    Purpose: Cleanup or remove invalid scripts.

    Response: 204 No Content

 Generated Screenplay APIs

These endpoints handle LLM-generated screenplays linked to original scripts.

**6️. List All Generated Scripts (Paginated)**

        GET /generated-scripts/list_all

        Returns all generated screenplays with pagination.

        Rate Limit: 10 requests/minute

        Purpose: View all generated screenplays efficiently.

**7️. Get Generated Script by ID**

    GET /generated-scripts/{generated_script_id}

    Fetch a specific generated screenplay.

    Rate Limit: 5 requests/minute

    Purpose: Retrieve final screenplay output.

    Response: 200 OK
    Errors: 404 Not Found

**8️. Get Generated Scripts by Script ID**

    GET /generated-scripts/by-script/{script_id}

    Fetches all generated screenplays associated with a specific script.

    Rate Limit: 10 requests/minute

    Purpose: View multiple screenplay versions generated from the same story.

**9️. Delete Generated Script**

    DELETE /generated-scripts/{generated_script_id}

    Deletes a generated screenplay.

    Purpose: Remove outdated or failed generations.

    Response: 204 No Content

**Rate Limiting Strategy**

        Rate limiting is enforced using SlowAPI middleware:

        Script creation: 5/min

        Script listing: 10/min

        Generated script access: 5–10/min

        Global Handler:

        HTTP 429 Too Many Requests
        {
        "detail": "Too many requests"
        }


        This protects:

        External LLM APIs

        Database resources

        Overall system stability

**Pagination Strategy**

        Pagination is implemented using dependency injection:

        Prevents large result sets

        Improves API performance

        Scales efficiently with data growth

        Used in:

        /scripts/list_all

        /generated-scripts/list_all

# 7. Testing Strategy
        Unit Testing

        Framework: Pytest

        Scope: Domain entities (Script and GeneratedScript) and business rules.

        Coverage:

        Entity creation with valid data ✅

        Validation errors for missing fields (id, name, content) ✅

        Content line limit enforcement ✅

        Status updates create new immutable instances ✅

        Execution: Tests run successfully inside the Docker container:

        docker-compose exec api pytest -v


        All 7 unit tests pass, validating core business logic independently of external services, the database, or FastAPI.

        Integration Testing (Partial)

        Framework: Pytest + FastAPI TestClient

        Scope: Minimal integration checks for API endpoints.

        Implementation:

        HTTP-level testing of the FastAPI app root endpoint /

        Confirms server responsiveness and endpoint correctness

        External API calls (LLM) are not yet fully tested due to time constraints

        HTTPX: Partially implemented to allow future mocking of external API requests.

        Integration tests ensure that endpoints are functional and ready for further expansion in future versions.

        Strategy Rationale

        Unit tests first: Ensures that core domain logic is correct and robust.

        Integration tests partial: Validates FastAPI app without overcomplicating the take-home assessment.

        HTTPX planned: External API calls can be fully tested in future iterations, including mocking rate limits and retries.

        Time-boxed implementation: Focused on completing a working MVP with correct domain behavior; additional integration tests and mocking will be added in version 2.

        ✅ Summary

        Unit tests: Complete ✅

        Integration tests: Partial (FastAPI smoke test) ✅

        External API testing (HTTPX): Partially implemented ✅

        Execution environment: Docker container, no virtual environment required

# 8. Limitations (Version 1)

This version of the application intentionally limits certain features to maintain focus on core architecture, stability, and API design.

**1️. No User Authentication or Authorization**

    Version 1 does not include:

    User registration

    Login / authentication

    User-specific data isolation

    All API endpoints are publicly accessible.

    Rate limiting is applied globally, not per user.

    Reason:
    The primary goal of this version is to demonstrate Clean Architecture, async processing, database design, and external API integration. User management is planned for a future release.

**2️. No Continuous or Conversational Generation**

        Generated screenplays are created using single, stateless LLM calls.

        There is no conversational memory or follow-up interaction.

        Users cannot:

        Continue a previous screenplay

        Refine or iterate on the same generation context

        Reason:
        Continuous chat requires session management, context storage, and token tracking, which were intentionally excluded to keep LLM interactions predictable and cost-controlled.

**3️. No Notification System**

    Users are not notified via email or webhook when screenplay generation is completed.

    Clients must poll the API to check the generation status.

    Reason:
    Notification services (email queues, webhooks, push services) were excluded to avoid increasing infrastructure complexity in version 1.

**4️. Input Size Limitation**

    Script content is limited to 1000 lines (or equivalent text size).

    Requests exceeding this limit are rejected at the domain validation layer.

    Reason:
    This protects:

    External LLM token usage

    API response times

    Database storage efficiency

**5️. No Advanced LLM Controls**

    Model selection is fixed at generation time.

    No temperature, tone, or creativity controls exposed to the API consumer.

    Output formatting is standardized.


# 9. Future Enhancements

**Version 2 – User-Centric & Interactive Features**

        Version 2 focuses on user experience, personalization, and interaction.

        Planned Enhancements:

        User Authentication & Authorization

        User registration and login

        User-specific scripts and generated content

        Per-user rate limiting and quotas

        Continuous / Conversational Script Generation

        Context-aware screenplay refinement

        Ability to continue or revise previously generated scripts

        Persistent conversation state management

        Notification System

        Email notifications when screenplay generation is completed

        Optional webhook-based notifications for external integrations

        Goal:
        Transform the system from a stateless API into a user-aware, interactive screenplay generation platform.



**Version 3 – Script-to-Video Generation**

        Version 3 expands the platform beyond text generation into multimedia production.

        Planned Enhancements:

        Script-to-Video Conversion

        Automatic scene-to-video rendering

        Scene-based video composition

        Audio Generation

        AI-generated voiceovers for dialogues

        Background music and sound effects

        Media Processing Pipeline

        Integration with video and audio generation models

        Background processing with distributed workers

        Goal:
        Evolve the application into a full story-to-video generation pipeline, enabling end-to-end content creation.