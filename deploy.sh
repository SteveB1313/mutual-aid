#!/bin/bash

set -e

IMAGE_NAME="storm-aid"
CONTAINER_NAME="storm-aid"
PORT=8000
HOST_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ -f "$HOST_DIR/.env" ]; then
    echo "Loading environment from .env..."
    set -a
    source "$HOST_DIR/.env"
    set +a
fi

echo "Building Docker image..."
docker build -t $IMAGE_NAME .

echo "Stopping existing container..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true

echo "Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:8000 \
    -v $HOST_DIR:/app \
    -e DJANGO_SECRET_KEY \
    -e DEBUG \
    -e ALLOWED_HOSTS \
    --restart unless-stopped \
    $IMAGE_NAME

echo "Waiting for container to start..."
sleep 2

echo "Running migrations..."
docker exec $CONTAINER_NAME python manage.py migrate

echo "Collecting static files..."
docker exec $CONTAINER_NAME python manage.py collectstatic --noinput

echo "Creating StormAdmins group..."
docker exec $CONTAINER_NAME python manage.py create_stormadmins_group 2>/dev/null || true

echo ""
echo "========================================"
echo "Deployment complete!"
echo "App running at: http://localhost:$PORT"
echo "Admin panel: http://localhost:$PORT/admin"
echo ""
echo "Create superuser:"
echo "  docker exec -it $CONTAINER_NAME python manage.py createsuperuser"
echo ""
echo "Add user to StormAdmins:"
echo "  docker exec -it $CONTAINER_NAME python manage.py shell"
echo "  >>> from django.contrib.auth.models import User, Group"
echo "  >>> user = User.objects.get(username='yourusername')"
echo "  >>> user.groups.add(Group.objects.get(name='StormAdmins'))"
echo "========================================"
