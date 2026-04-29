# AGENTS.md - Storm Aid Project Context

## Project Overview
Storm Aid is a Django application for managing storm response mutual aid deployments. It helps coordinate companies that provide services (tree removal, electrical, roofing, etc.) during storm events.

## Tech Stack
- **Backend**: Django 4.0+ (Python 3.12)
- **Database**: SQLite3 (development), can be adapted for PostgreSQL
- **Server**: Gunicorn with WhiteNoise for static files
- **Deployment**: Docker with multi-stage build
- **Password Hashing**: Argon2 (primary), PBKDF2 (fallback)
- **Caching**: Local memory cache (LocMemCache)

## Project Structure
```
mutual-aid/
├── mutualaid/              # Django project config
│   ├── settings.py         # Settings with env var support
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py
│   └── asgi.py
├── storm_companies/        # Main Django app
│   ├── models.py           # Company, StormEvent, Deployment
│   ├── views.py            # All CRUD views + auth
│   ├── admin.py            # Django admin config
│   ├── tests.py            # Test suite (needs implementation)
│   ├── management/
│   │   └── commands/
│   │       └── create_stormadmins_group.py
│   └── templates/storm_companies/
│       ├── home.html
│       ├── company_form.html
│       ├── company_confirm_delete.html
│       ├── stormevent_form.html
│       ├── stormevent_list.html
│       ├── stormevent_confirm_delete.html
│       ├── deployment_form.html
│       └── deployment_list.html
├── staticfiles/           # Collected static files (gitignored)
├── db.sqlite3            # Development database (gitignored)
├── manage.py
├── requirements.txt       # Django, whitenoise, python-dotenv, argon2-cffi, gunicorn
├── Dockerfile            # Multi-stage Python 3.12 build
├── deploy.sh             # Docker deployment script
├── .env                  # Environment variables (gitignored)
└── .env.example          # Example environment config
```

## Models

### Company
- Fields: name, contact_name, phone, email, address, services (JSON), status, notes, created_at, updated_at, deleted_at
- Status choices: available, deployed, unavailable
- Services: tree, electrical, roofing, general, plumbing, hvac, equipment, other
- Soft delete via `deleted_at` field

### StormEvent
- Fields: name, date, severity, affected_area, description, created_at, deleted_at
- Severity: minor, moderate, severe, catastrophic
- Soft delete via `deleted_at` field

### Deployment
- Fields: company (FK), storm_event (FK), status, requested_at, confirmed_at, deployed_from_city/state, arrived_at, active_at, completed_at, notes, deleted_at
- Status: requested, confirmed, en_route, on_site, completed, cancelled
- Soft delete via `deleted_at` field

## Key Architecture Patterns

### Soft Delete
All models use `deleted_at` field for soft deletes. Always filter with `deleted_at__isnull=True` in queries. Delete views set `deleted_at = timezone.now()` instead of actual deletion.

### Authentication & Authorization
- Uses Django's built-in auth system
- `StormAdmins` group for admin functionality
- Custom `is_storm_admin` check: `user.groups.filter(name='StormAdmins').exists()`
- All create/update/delete views protected with `@user_passes_test(is_storm_admin)`
- Login rate limiting via Django cache (5 attempts per 5 minutes per IP)
- Password hashers: Argon2 preferred, PBKDF2 fallback

### URL Structure
- `/` - Home (lists companies)
- `/login/` - Rate-limited login (redirects to admin login)
- `/admin/` - Django admin
- `/companies/create/` - Create company
- `/companies/<id>/update/` - Update company
- `/companies/<id>/delete/` - Soft delete company
- `/stormevents/` - List storm events
- `/stormevents/create/` - Create storm event
- `/stormevents/<id>/update/` - Update storm event
- `/stormevents/<id>/delete/` - Soft delete storm event
- `/deployments/` - List deployments
- `/deployments/create/` - Create deployment
- `/deployments/<id>/update/` - Update deployment
- `/deployments/<id>/delete/` - Soft delete deployment
- `/health/` - Health check endpoint (JSON response)

## Environment Variables (.env)
```
DJANGO_SECRET_KEY=change-this-secret-key-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Common Commands

### Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python3 manage.py migrate

# Create superuser
python3 manage.py createsuperuser

# Add user to StormAdmins group
python3 manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='yourusername')
>>> user.groups.add(Group.objects.get(name='StormAdmins'))

# Create StormAdmins group
python3 manage.py create_stormadmins_group

# Run development server
python3 manage.py runserver
```

### Testing
```bash
# Run tests (currently tests.py is empty - needs implementation)
python3 manage.py test

# Linting/typechecking - not configured yet
# Consider adding: flake8, black, mypy
```

### Docker Deployment
```bash
# Initial setup
cp .env.example .env
# Edit .env with production values

# Deploy
./deploy.sh

# Create admin user in Docker
docker exec -it storm-aid python manage.py createsuperuser

# View logs
docker logs storm-aid

# Stop/start
docker stop storm-aid
docker start storm-aid
```

## Security Notes
- DEBUG must be False in production
- SECRET_KEY must be changed in production
- ALLOWED_HOSTS must be configured for production
- When DEBUG=False, additional security headers are enabled (HSTS, SSL redirect, secure cookies, etc.)
- Session cookies expire after 24 hours and on browser close
- CSRF protection enabled
- X-Frame-Options set to DENY in production

## Current TODOs / Areas for Improvement
- [ ] Implement tests in `storm_companies/tests.py` (currently empty)
- [ ] Add form validation (currently using raw POST data in views)
- [ ] Consider adding Django forms or DRF serializers
- [ ] Add pagination for list views
- [ ] Consider adding REST API endpoints
- [ ] Add user self-registration or admin approval workflow
- [ ] Implement logging to file (currently console only)
- [ ] Add CI/CD pipeline
- [ ] Consider PostgreSQL for production

## Important Conventions
- Always use `timezone.now()` for datetime fields (not `datetime.now()`)
- Filter out soft-deleted records: `Model.objects.filter(deleted_at__isnull=True)`
- Use `get_object_or_404()` for detail/update/delete views
- All templates in `storm_companies/templates/storm_companies/`
- Static files collected to `staticfiles/` via WhiteNoise
- Deployment mounts host directory to `/app` in Docker for persistence

## Git Workflow
- Never commit `.env`, `db.sqlite3`, `staticfiles/`, `__pycache__/`
- See `.gitignore` for complete list
- No pre-commit hooks configured yet
