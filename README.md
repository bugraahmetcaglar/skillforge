# SkillForge User Management API

This project demonstrates a professional-grade implementation of a User Management API built with Django and Django REST Framework. It showcases best practices for building secure, maintainable, and scalable RESTful APIs.

## Features

- User registration and authentication
- JWT token-based authentication with token refresh
- User profile management (get, list, update)
- Role-based permissions
- API documentation using Swagger/ReDoc
- Containerized development environment with Docker
- Background task processing with Celery and Redis
- Data persistence with PostgreSQL

## Architecture Highlights

### Two Implementation Approaches

This project intentionally demonstrates two different implementation approaches for building REST APIs with Django:

1. **Class-Based Views (CBVs)**: Individual views for specific operations, providing maximum customization and clarity.
2. **ViewSets**: Consolidated CRUD operations in a single class, reducing code duplication and leveraging automated URL routing.

Both approaches are valid in professional Django development, and this project shows when each might be preferred.

### Project Structure

```
skillforge/
├── apps/
│   └── user/
│       ├── migrations/
│       ├── admin.py
│       ├── apps.py
│       ├── models.py         # User model definition
│       ├── permissions.py    # Custom permission classes
│       ├── serializers.py    # Serializers for the User model
│       ├── tests.py
│       ├── urls.py           # URL routing for user operations
│       ├── views.py          # Class-based views implementation
│       └── viewsets.py       # ViewSet implementation
├── core/
│   ├── fields.py             # Custom model fields
│   └── models.py             # Base abstract models
├── skillforge/
│   ├── asgi.py
│   ├── settings.py           # Project settings
│   ├── urls.py               # Main URL routing
│   └── wsgi.py
├── requirements/
│   ├── base.txt              # Base dependencies
│   ├── dev.txt               # Development dependencies
│   ├── local.txt             # Local development dependencies
│   └── test.txt              # Testing dependencies
├── docker-compose.yml        # Docker services configuration
├── Dockerfile                # Docker container definition
└── manage.py                 # Django management script
```

## API Endpoints

The API is organized under the `/api/v1/user/` base path.

### Using Class-Based Views:

- `POST /api/v1/user/register/` - Register a new user
- `GET /api/v1/user/list/` - List all users (admin only)
- `GET /api/v1/user/<uuid:pk>/` - Get user details
- `GET /api/v1/user/me/` - Get current user details
- `PUT/PATCH /api/v1/user/<uuid:pk>/update/` - Update user
- `PUT/PATCH /api/v1/user/me/update/` - Update current user

### Using ViewSets:

- `GET /api/v1/user/users/` - List all users (admin only)
- `POST /api/v1/user/users/` - Create a new user
- `GET /api/v1/user/users/<uuid:pk>/` - Get user details
- `PUT/PATCH /api/v1/user/users/<uuid:pk>/` - Update user
- `DELETE /api/v1/user/users/<uuid:pk>/` - Delete user
- `POST /api/v1/user/users/register/` - Register a new user (returns token)
- `GET/PUT/PATCH /api/v1/user/users/me/` - Get/update current user details
- `POST /api/v1/user/users/regenerate_token/` - Regenerate auth token

### Token Operations:

- `POST /api/v1/user/token/` - Obtain token pair
- `POST /api/v1/user/token/refresh/` - Refresh access token
- `POST /api/v1/user/token/verify/` - Verify token
- `POST /api/v1/user/token/regenerate/` - Regenerate token pair

## Setup and Installation

### Prerequisites

- Docker and Docker Compose
- Git

### Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/skillforge.git
   cd skillforge
   ```

2. Create a `dev.env` file with the following variables:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key
   DB_NAME=skillforge-dev
   DB_USER=skillforge
   DB_PASSWORD=skillforge
   DB_HOST=db
   DB_PORT=5432
   ```

### Git Hooks Setup

```bash
mkdir -p .git/hooks
chmod +x scripts/git-hooks/pre-commit
ln -sf ../../scripts/git-hooks/pre-commit .git/hooks/pre-commit
```


3. Start the Docker services:
   ```
   docker-compose up -d
   ```

4. Create and apply migrations:
   ```
   docker-compose exec web python manage.py makemigrations
   docker-compose exec web python manage.py migrate
   ```

5. Create a superuser:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

6. Access the API documentation at:
   ```
   http://localhost:8000/docs/
   ```

## Best Practices Demonstrated

1. **Proper Authentication**: JWT-based authentication with token refresh
2. **Permissions Management**: Custom permission classes for object-level permissions
3. **API Versioning**: Using URL versioning for API stability
4. **Clean Code Structure**: Separation of concerns, modular design
5. **Comprehensive Documentation**: Swagger/ReDoc API documentation
6. **Security**: Password validation, secure token handling
7. **Containerization**: Docker for consistent development environments
8. **Efficient Data Handling**: Using serializers for data validation and transformation

## Development Philosophy

This project follows several key principles:

1. **DRY (Don't Repeat Yourself)**: Shared code is abstracted to avoid duplication
2. **KISS (Keep It Simple, Stupid)**: Simple solutions are preferred over complex ones
3. **YAGNI (You Aren't Gonna Need It)**: Only implement what is currently needed
4. **Composition over Inheritance**: Favor composition over inheritance where possible

## Testing

Run the test suite with:

```
docker-compose exec web python manage.py test
```

For more comprehensive testing with coverage reporting:

```
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage report
```