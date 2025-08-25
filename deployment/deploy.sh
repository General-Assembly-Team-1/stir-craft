#!/bin/bash
# ==============================================================================
# StirCraft Deployment Scripts
# ==============================================================================
# Collection of utility scripts for deploying and managing StirCraft
# ==============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ------------------------------------------------------------------------------
# Development Environment Setup
# ------------------------------------------------------------------------------
setup_dev() {
    print_status "Setting up development environment..."
    
    # Check prerequisites
    if ! command_exists docker; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command_exists docker-compose; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file from .env.example..."
        cp .env.example .env
        print_warning "Please edit .env file with your configuration before continuing"
    fi
    
    # Build and start services
    print_status "Building Docker images..."
    docker-compose build
    
    print_status "Starting development services..."
    docker-compose up -d
    
    # Wait for database to be ready
    print_status "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose exec web python stircraft/manage.py migrate
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose exec web python stircraft/manage.py collectstatic --noinput
    
    # Create superuser (optional)
    read -p "Do you want to create a superuser? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose exec web python stircraft/manage.py createsuperuser
    fi
    
    print_success "Development environment is ready!"
    print_status "Access the application at: http://localhost:8000"
    print_status "Admin interface at: http://localhost:8000/admin"
}

# ------------------------------------------------------------------------------
# Production Deployment
# ------------------------------------------------------------------------------
deploy_production() {
    print_status "Deploying to production..."
    
    # Check if production environment file exists
    if [ ! -f .env.prod ]; then
        print_error "Production environment file (.env.prod) not found!"
        print_status "Copy .env.prod.example to .env.prod and configure it first."
        exit 1
    fi
    
    # Backup database before deployment
    backup_database
    
    # Pull latest images or build
    print_status "Building production images..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
    
    # Stop existing services
    print_status "Stopping existing services..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
    
    # Start production services
    print_status "Starting production services..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    # Wait for services to be ready
    print_status "Waiting for services to be ready..."
    sleep 30
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec web python stircraft/manage.py migrate
    
    # Collect static files
    print_status "Collecting static files..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml exec web python stircraft/manage.py collectstatic --noinput
    
    # Health check
    print_status "Performing health check..."
    if curl -f http://localhost/health/ >/dev/null 2>&1; then
        print_success "Production deployment successful!"
    else
        print_error "Health check failed. Please check the logs."
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs
        exit 1
    fi
}

# ------------------------------------------------------------------------------
# Database Management
# ------------------------------------------------------------------------------
backup_database() {
    print_status "Creating database backup..."
    
    # Create backup directory
    mkdir -p backups
    
    # Generate backup filename with timestamp
    BACKUP_FILE="backups/stircraft_backup_$(date +%Y%m%d_%H%M%S).sql"
    
    # Create backup
    docker-compose exec db pg_dump -U stircraft stircraft > "$BACKUP_FILE"
    
    if [ -f "$BACKUP_FILE" ]; then
        print_success "Database backup created: $BACKUP_FILE"
    else
        print_error "Failed to create database backup"
        exit 1
    fi
}

restore_database() {
    if [ -z "$1" ]; then
        print_error "Please specify backup file to restore"
        echo "Usage: $0 restore <backup_file>"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_warning "This will replace the current database. Are you sure?"
    read -p "Type 'yes' to continue: " -r
    if [ "$REPLY" != "yes" ]; then
        print_status "Database restore cancelled"
        exit 0
    fi
    
    print_status "Restoring database from: $BACKUP_FILE"
    
    # Stop web service to prevent connections
    docker-compose stop web
    
    # Restore database
    docker-compose exec -T db psql -U stircraft -d stircraft < "$BACKUP_FILE"
    
    # Start web service
    docker-compose start web
    
    print_success "Database restored successfully"
}

# ------------------------------------------------------------------------------
# Maintenance Commands
# ------------------------------------------------------------------------------
show_logs() {
    SERVICE="${1:-}"
    if [ -n "$SERVICE" ]; then
        docker-compose logs -f "$SERVICE"
    else
        docker-compose logs -f
    fi
}

restart_services() {
    print_status "Restarting services..."
    docker-compose restart
    print_success "Services restarted"
}

update_dependencies() {
    print_status "Updating dependencies..."
    docker-compose build --no-cache
    docker-compose down
    docker-compose up -d
    print_success "Dependencies updated"
}

cleanup() {
    print_status "Cleaning up unused Docker resources..."
    docker system prune -f
    docker volume prune -f
    print_success "Cleanup completed"
}

# ------------------------------------------------------------------------------
# SSL Certificate Management (Let's Encrypt)
# ------------------------------------------------------------------------------
setup_ssl() {
    DOMAIN="${1:-}"
    if [ -z "$DOMAIN" ]; then
        print_error "Please specify domain name"
        echo "Usage: $0 ssl <domain>"
        exit 1
    fi
    
    print_status "Setting up SSL certificate for: $DOMAIN"
    
    # Install certbot if not present
    if ! command_exists certbot; then
        print_error "Certbot is not installed. Please install certbot first."
        exit 1
    fi
    
    # Create SSL directory
    mkdir -p docker/nginx/ssl
    
    # Generate certificate
    certbot certonly --webroot \
        -w docker/nginx/ssl \
        -d "$DOMAIN" \
        --email "admin@$DOMAIN" \
        --agree-tos \
        --no-eff-email
    
    # Copy certificates
    cp "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" docker/nginx/ssl/
    cp "/etc/letsencrypt/live/$DOMAIN/privkey.pem" docker/nginx/ssl/
    
    print_success "SSL certificate installed for $DOMAIN"
    print_status "Don't forget to update nginx configuration with your domain name"
}

renew_ssl() {
    print_status "Renewing SSL certificates..."
    certbot renew --quiet
    
    # Copy renewed certificates
    for cert_dir in /etc/letsencrypt/live/*/; do
        domain=$(basename "$cert_dir")
        cp "$cert_dir/fullchain.pem" "docker/nginx/ssl/fullchain.pem"
        cp "$cert_dir/privkey.pem" "docker/nginx/ssl/privkey.pem"
    done
    
    # Reload nginx
    docker-compose exec nginx nginx -s reload
    
    print_success "SSL certificates renewed"
}

# ------------------------------------------------------------------------------
# Main Script Logic
# ------------------------------------------------------------------------------
case "${1:-}" in
    "dev"|"development")
        setup_dev
        ;;
    "prod"|"production")
        deploy_production
        ;;
    "backup")
        backup_database
        ;;
    "restore")
        restore_database "$2"
        ;;
    "logs")
        show_logs "$2"
        ;;
    "restart")
        restart_services
        ;;
    "update")
        update_dependencies
        ;;
    "cleanup")
        cleanup
        ;;
    "ssl")
        setup_ssl "$2"
        ;;
    "renew-ssl")
        renew_ssl
        ;;
    *)
        echo "StirCraft Deployment Script"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  dev                 Set up development environment"
        echo "  prod                Deploy to production"
        echo "  backup              Create database backup"
        echo "  restore <file>      Restore database from backup"
        echo "  logs [service]      Show logs for all services or specific service"
        echo "  restart             Restart all services"
        echo "  update              Update dependencies and rebuild"
        echo "  cleanup             Clean up unused Docker resources"
        echo "  ssl <domain>        Set up SSL certificate for domain"
        echo "  renew-ssl           Renew SSL certificates"
        echo ""
        echo "Examples:"
        echo "  $0 dev                          # Set up development environment"
        echo "  $0 prod                         # Deploy to production"
        echo "  $0 backup                       # Create database backup"
        echo "  $0 restore backups/backup.sql   # Restore from backup"
        echo "  $0 logs web                     # Show web service logs"
        echo "  $0 ssl example.com              # Set up SSL for example.com"
        ;;
esac
