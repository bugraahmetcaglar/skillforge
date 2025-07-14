# SkillForge

Modern Django REST API platform with user management, contact handling, AI integration, and financial tracking.

## 🚀 Features

- **User Management**: JWT auth, role-based permissions
- **Contact Management**: vCard import, duplicate detection
- **AI Integration**: Turkish NLP, Telegram bot
- **Finance Tracking**: Multi-currency subscriptions
- **Background Tasks**: Django-Q processing
- **Advanced Logging**: Structured logs with analytics

## 🏗️ Tech Stack

- Django 5.2.2 + DRF 3.16.0
- PostgreSQL 16.2 + Redis
- Django-Q2 for background tasks
- JWT authentication
- pytest + model-bakery testing

## ⚡ Quick Start

1. **Setup Environment**
   ```bash
   git clone <repo-url>
   cd skillforge
   cp dev.env.example dev.env
   ```

2. **Start Services**
   ```bash
   docker-compose up -d
   ```

3. **Setup Database**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access**
   - API Docs: http://localhost:8000/docs/
   - Admin: http://localhost:8000/admin/

## 🧪 Development

```bash
# Code quality
docker-compose exec web black .
docker-compose exec web pytest

# Database operations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Django shell
docker-compose exec web python manage.py shell
```

## 📄 License

Apache License 2.0