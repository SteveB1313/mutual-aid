#!/bin/bash

set -e

IMAGE_NAME="storm-aid"
CONTAINER_NAME="storm-aid"
PORT=8000
HOST_DIR="$(cd "$(dirname "$0")" && pwd)"

# Create .env if it doesn't exist
if [ ! -f "$HOST_DIR/.env" ]; then
    echo "Creating .env file..."
    cat > "$HOST_DIR/.env" << 'EOF'
DJANGO_SECRET_KEY=change-this-secret-key-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EOF
    echo ".env created. Please review and update with your production values."
fi

# Load environment
set -a
source "$HOST_DIR/.env"
set +a

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

echo "Running migrations..."
docker exec $CONTAINER_NAME python manage.py migrate

echo "Collecting static files..."
docker exec $CONTAINER_NAME python manage.py collectstatic --noinput

echo "Creating StormAdmins group..."
docker exec $CONTAINER_NAME python manage.py create_stormadmins_group || echo "Warning: Could not create StormAdmins group"

echo ""
echo "========================================"
echo "Deployment complete!"
echo "App: http://localhost:$PORT"
echo "Admin: http://localhost:$PORT/admin"
echo ""
echo "Create admin user:"
echo "  docker exec -it $CONTAINER_NAME python manage.py createsuperuser"
echo ""
echo "Add user to StormAdmins:"
echo "  docker exec -it $CONTAINER_NAME python manage.py shell"
echo "  >>> from django.contrib.auth.models import User, Group"
echo "  >>> user = User.objects.get(username='yourusername')"
echo "  >>> user.groups.add(Group.objects.get(name='StormAdmins'))"
echo "========================================"
