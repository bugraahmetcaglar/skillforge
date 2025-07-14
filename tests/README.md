# Testing Guide

Testing setup and guidelines for SkillForge using pytest and model-bakery.

## 🧪 Test Stack

- **pytest**: Main testing framework
- **pytest-django**: Django integration
- **model-bakery**: Model instance generation
- **coverage**: Code coverage reporting
- **pytest-sugar**: Enhanced output

## 📁 Structure

```
tests/
├── conftest.py              # Global fixtures
├── unit/                    # Isolated component tests
│   ├── conftest.py         # Unit test fixtures
│   ├── core/               # Core utilities tests
│   └── user/               # User app tests
├── integration/            # Component interaction tests
├── e2e/                    # End-to-end API tests
└── README.md              # This file
```

## ⚙️ Configuration

### pytest.ini
```ini
[pytest]
DJANGO_SETTINGS_MODULE = skillforge.settings.test
testpaths = tests
addopts = --strict-markers -v --no-migrations --reuse-db
markers =
    unit: Unit tests
    integration: Integration tests  
    e2e: End-to-end tests
    api: API endpoint tests
    model: Model tests
    serializer: Serializer tests
```

### Test Settings (`skillforge/settings/test.py`)
```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "test_skillforge",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
    }
}

# Speed optimizations
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
```

## 🏭 Fixtures

### Global Fixtures (`tests/conftest.py`)
```python
@pytest.fixture
def api_client():
    ...

@pytest.fixture
def user(db):
    ...

@pytest.fixture
def authenticated_client(api_client, user):
    ...
```

Global fixtures for API client, user creation, and authenticated client setup.

## 🧪 Test Types

### Unit Tests
Test individual functions/methods in isolation with mock dependencies.

### Integration Tests  
Test component interactions like service-to-model or view-to-serializer integration.

### E2E Tests
Test complete API workflows from request to response including authentication.

## 🚀 Running Tests

### Basic Commands
```bash
# All tests
pytest

# By category
pytest -m unit
pytest -m integration
pytest -m e2e

# Specific file
pytest tests/unit/user/test_user_model.py

# With coverage
coverage run -m pytest
coverage report
coverage html
```

### Docker Commands
```bash
# Run in container
docker-compose exec web pytest

# With coverage
docker-compose exec web coverage run -m pytest
docker-compose exec web coverage report
```

### Advanced Options
```bash
# Parallel execution
pytest -n auto

# Stop on first failure
pytest -x

# Re-run failed tests
pytest --lf

# Verbose output
pytest -v -s
```

## 📊 Coverage

### Generate Reports
```bash
# Run with coverage
coverage run --source='.' -m pytest

# View report
coverage report

# HTML report
coverage html
open htmlcov/index.html
```

### Coverage Config (`.coveragerc`)
```ini
[run]
source = .
omit = 
    */migrations/*
    */tests/*
    */venv/*
    manage.py
    */settings/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise NotImplementedError
```

## 🎯 Best Practices

### Test Organization
- **Unit**: Test individual functions/methods
- **Integration**: Test component interactions  
- **E2E**: Test complete workflows

### Fixture Usage
```python
# Simple cases - use baker
user = baker.make(User)

# Complex cases - use fixtures
@pytest.fixture
def admin_user():
    return baker.make(User, is_staff=True)
```

### Mocking External Services
```python
from unittest.mock import patch

@patch('apps.telegram.apis.requests.post')
def test_telegram_call(mock_post):
    mock_post.return_value.ok = True
    # Test code here
```

## 🔧 Common Patterns

### API Testing
```python
def test_create_endpoint(authenticated_client):
    data = {"name": "Test"}
    response = authenticated_client.post("/api/endpoint/", data)
    assert response.status_code == 201
```

### Model Testing  
```python
def test_model_method():
    obj = baker.make(MyModel, field="value")
    result = obj.my_method()
    assert result == "expected"
```

### Serializer Testing
```python
def test_serializer_validation():
    data = {"invalid": "data"}
    serializer = MySerializer(data=data)
    assert not serializer.is_valid()
```

## 🚨 Debugging

### Use pdb
```python
def test_debug():
    import pdb; pdb.set_trace()
    # Debug here
```

### Print debugging
```python
def test_with_output(capfd):
    print("Debug info")
    result = function()
    captured = capfd.readouterr()
    assert "Debug info" in captured.out
```

## 📈 CI/CD

Tests run automatically on:
- Push to main/development
- Pull requests
- GitHub Actions workflow

See `.github/workflows/tests.yml` for CI configuration.