# Storm Aid

A Django application for managing storm response mutual aid deployments.

## Setup

```bash
# Install dependencies
./setup.sh

# Create admin user
python3 manage.py createsuperuser

# Add user to StormAdmins group
python3 manage.py shell
>>> from django.contrib.auth.models import User, Group
>>> user = User.objects.get(username='yourusername')
>>> user.groups.add(Group.objects.get(name='StormAdmins'))
```

## Docker Deployment

```bash
# Copy and configure environment
cp .env.example .env

# Edit .env with your settings

# Deploy
./deploy.sh
```

## Features

- Company management
- Storm event tracking
- Deployment coordination
- Role-based access control (StormAdmins group)
- Soft delete for all records
