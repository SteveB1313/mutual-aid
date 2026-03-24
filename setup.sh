#!/bin/bash

echo "Setting up Storm Aid application..."

# Install dependencies
echo "Installing requirements..."
python3 -m pip install -r requirements.txt

# Run migrations
echo "Running database migrations..."
python3 manage.py migrate

# Create StormAdmins group
echo "Creating StormAdmins group..."
python3 manage.py create_stormadmins_group

echo ""
echo "Setup complete!"
echo ""
echo "To create an admin user:"
echo "  python3 manage.py createsuperuser"
echo ""
echo "To add a user to StormAdmins group:"
echo "  python3 manage.py shell"
echo "  >>> from django.contrib.auth.models import User, Group"
echo "  >>> user = User.objects.get(username='yourusername')"
echo "  >>> user.groups.add(Group.objects.get(name='StormAdmins'))"
echo ""
