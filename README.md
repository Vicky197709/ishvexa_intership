# Error Event Ingestion API

A backend service for ingesting, storing, and grouping application error events. Built with Django REST Framework, PostgreSQL, and Redis.

## Features

- **Event Ingestion**: POST endpoint to receive error events with validation
- **Smart Grouping**: Events with the same fingerprint are grouped into issues
- **Issue Management**: List and retrieve issues with pagination and filters
- **Authentication**: API key-based authentication per project
- **Rate Limiting**: Redis-based rate limiting (100 req/min per IP)
- **API Documentation**: Swagger UI and ReDoc via drf-spectacular

## Tech Stack

- **Framework**: Django 5.0 + Django REST Framework 3.14
- **Database**: PostgreSQL 15
- **Cache**: Redis 7
- **API Docs**: drf-spectacular (Swagger UI + ReDoc)
- **Testing**: pytest + pytest-django
- **Orchestration**: Docker Compose

## Design Decisions

### Fingerprinting Strategy
Events are grouped using a SHA256 hash of:
- Normalized message (trimmed and lowercased)
- Top stack frame (first line of stack trace)

This ensures that similar errors with the same root cause are grouped together, regardless of minor variations in the full stack trace.

### Data Model
- **Project**: Represents an application with a unique API key
- **Issue**: Represents a grouped error with count, first_seen, last_seen
- **Event**: Individual error occurrence linked to an issue

### Authentication
Custom `APIKeyAuthentication` class using the `X-API-Key` header. Each project has a unique API key generated using `secrets.token_urlsafe(32)`.

### Rate Limiting
Using `django-ratelimit` with Redis backend:
- 100 requests per minute per IP
- Applied only to POST /events to prevent abuse

### Pagination
PageNumberPagination with:
- Default page size: 20
- Maximum page size: 100
- Query params: `page`, `page_size`

## Setup

### Prerequisites
- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ishvexa_intership
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Start services with Docker Compose:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

5. Create a project:
```bash
docker-compose exec web python manage.py create_project "My App"
```

This will output an API key that you'll use for authentication.

## API Endpoints

### Documentation
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

### POST /api/v1/events/
Create a new error event.

**Headers:**
```
X-API-Key: <your-api-key>
Content-Type: application/json
```

**Body:**
```json
{
  "project_key": "your-api-key",
  "message": "NullReferenceException in UserService",
  "stack_trace": "File 'user_service.py', line 42\n  get_user()\nFile 'main.py', line 10\n  main()",
  "level": "error",
  "environment": "production",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response (201):**
```json
{
  "issue_id": "uuid-here",
  "fingerprint": "sha256-hash-here",
  "created": true
}
```

**Levels:** `error`, `warning`, `info`

### GET /api/v1/issues/
List issues with pagination and filters.

**Headers:**
```
X-API-Key: <your-api-key>
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `level`: Filter by level (error, warning, info)
- `environment`: Filter by environment

**Example:**
```
GET /api/v1/issues/?level=error&environment=production&page=1
```

**Response (200):**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/v1/issues/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "project": "uuid-here",
      "fingerprint": "sha256-hash-here",
      "message": "NullReferenceException in UserService",
      "level": "error",
      "environment": "production",
      "count": 15,
      "first_seen": "2024-01-15T10:00:00Z",
      "last_seen": "2024-01-15T14:30:00Z",
      "top_stack_frame": "File 'user_service.py', line 42"
    }
  ]
}
```

### GET /api/v1/issues/{id}/
Get issue details with recent events.

**Headers:**
```
X-API-Key: <your-api-key>
```

**Response (200):**
```json
{
  "id": "uuid-here",
  "project": "uuid-here",
  "fingerprint": "sha256-hash-here",
  "message": "NullReferenceException in UserService",
  "level": "error",
  "environment": "production",
  "count": 15,
  "first_seen": "2024-01-15T10:00:00Z",
  "last_seen": "2024-01-15T14:30:00Z",
  "top_stack_frame": "File 'user_service.py', line 42",
  "recent_events": [
    {
      "id": "uuid-here",
      "message": "NullReferenceException in UserService",
      "stack_trace": "File 'user_service.py', line 42\n  get_user()",
      "level": "error",
      "environment": "production",
      "timestamp": "2024-01-15T14:30:00Z",
      "received_at": "2024-01-15T14:30:01Z"
    }
  ]
}
```

## Running Tests

Run all tests:
```bash
docker-compose exec web pytest
```

Run specific test file:
```bash
docker-compose exec web pytest tests/test_services.py
```

Run with coverage:
```bash
docker-compose exec web pytest --cov=apps --cov-report=html
```

## Project Structure

```
.
├── apps/
│   ├── events/          # Event and Issue models, views, serializers
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── authentication.py  # API key authentication
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── services.py       # Fingerprint generation logic
│   │   ├── urls.py
│   │   └── views.py
│   └── projects/       # Project model and management commands
│       ├── admin.py
│       ├── apps.py
│       ├── management/
│       │   └── commands/
│       │       └── create_project.py  # CLI to create projects
│       └── models.py
├── docker-compose.yml
├── Dockerfile
├── error_ingestion/    # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
├── requirements.txt
├── pytest.ini
└── tests/              # Test suite
    ├── test_authentication.py
    ├── test_services.py
    └── test_views.py
```

## Development

### Adding a New Project
```bash
docker-compose exec web python manage.py create_project "Project Name"
```

### Accessing Django Admin
1. Create a superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

2. Access at: http://localhost:8000/admin/

### Viewing Logs
```bash
docker-compose logs -f web
```

## License

This project is part of the Ishvexa Hub Backend Developer Internship program.
