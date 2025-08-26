#!/bin/bash

# =============================================================================
# StirCraft Django Development Environment Setup and Diagnostic Script
# =============================================================================
# This script checks for common issues with local development setup and 
# provides fixes for PostgreSQL, Python environment, and Django configuration.
#
# Run from project root: ./dev-setup-check.sh
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project configuration
PROJECT_NAME="stircraft"
REQUIRED_PYTHON_VERSION="3.12"
DB_NAME="stircraft"
DJANGO_DIR="stircraft"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

print_header() {
    echo -e "\n${PURPLE}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_action() {
    echo -e "${CYAN}→ $1${NC}"
}

# =============================================================================
# SYSTEM CHECKS
# =============================================================================

check_system_requirements() {
    print_header "Checking System Requirements"
    
    # Check if we're in the right directory
    if [ ! -f "manage.py" ] && [ ! -f "stircraft/manage.py" ]; then
        print_error "Not in project root directory. Please run this script from the stir-craft project root."
        exit 1
    fi
    print_success "Running from correct project directory"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
        if [ "$PYTHON_VERSION" = "$REQUIRED_PYTHON_VERSION" ]; then
            print_success "Python $PYTHON_VERSION found"
        else
            print_warning "Python $PYTHON_VERSION found, but project requires Python $REQUIRED_PYTHON_VERSION"
            print_info "Consider using pyenv to manage Python versions"
        fi
    else
        print_error "Python 3 not found. Please install Python $REQUIRED_PYTHON_VERSION"
        exit 1
    fi
    
    # Check PostgreSQL
    if command -v psql &> /dev/null; then
        print_success "PostgreSQL client (psql) found"
        PG_VERSION=$(psql --version | head -n1 | awk '{print $3}' | cut -d'.' -f1-2)
        print_info "PostgreSQL version: $PG_VERSION"
    else
        print_error "PostgreSQL client not found"
        print_info "Install PostgreSQL:"
        print_info "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
        print_info "  macOS: brew install postgresql"
        print_info "  Or use Docker: docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres"
    fi
    
    # Check if PostgreSQL service is running
    if systemctl is-active --quiet postgresql 2>/dev/null || pgrep -x postgres &> /dev/null; then
        print_success "PostgreSQL service is running"
    else
        print_warning "PostgreSQL service may not be running"
        print_info "Start PostgreSQL:"
        print_info "  Ubuntu/Debian: sudo systemctl start postgresql"
        print_info "  macOS: brew services start postgresql"
    fi
}

# =============================================================================
# PYTHON ENVIRONMENT CHECKS
# =============================================================================

check_python_environment() {
    print_header "Checking Python Environment"
    
    # Check for virtual environment
    if [ -d ".venv" ]; then
        print_success "Virtual environment (.venv) found"
        
        # Check if it's activated
        if [ "$VIRTUAL_ENV" = "$(pwd)/.venv" ]; then
            print_success "Virtual environment is activated"
        else
            print_warning "Virtual environment exists but is not activated"
            print_action "Activate with: source .venv/bin/activate"
        fi
    else
        print_warning "No virtual environment found"
        print_action "Creating virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
        print_action "Activate with: source .venv/bin/activate"
        print_info "After activation, run this script again"
        exit 0
    fi
    
    # Check if dependencies are installed
    if [ "$VIRTUAL_ENV" ]; then
        if python -c "import django" 2>/dev/null; then
            DJANGO_VERSION=$(python -c "import django; print(django.get_version())")
            print_success "Django $DJANGO_VERSION is installed"
        else
            print_warning "Django not found in virtual environment"
            print_action "Installing dependencies..."
            
            # Try pipenv first, then pip
            if command -v pipenv &> /dev/null && [ -f "Pipfile" ]; then
                pipenv install --dev
                print_success "Dependencies installed via pipenv"
            else
                pip install -r requirements.txt
                print_success "Dependencies installed via pip"
            fi
        fi
    else
        print_error "Virtual environment not activated. Please activate and run again."
        exit 1
    fi
}

# =============================================================================
# ENVIRONMENT VARIABLES CHECK
# =============================================================================

check_environment_variables() {
    print_header "Checking Environment Variables"
    
    # Check for .env file
    if [ ! -f ".env" ]; then
        print_warning ".env file not found"
        if [ -f ".env.example" ]; then
            print_action "Creating .env from .env.example..."
            cp .env.example .env
            print_success ".env file created from template"
            print_warning "Please edit .env file with your actual values"
        else
            print_error "No .env.example template found"
            print_action "Creating basic .env file..."
            cat > .env << EOF
# StirCraft Environment Variables
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stircraft
DB_USER=$USER
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Optional: Use DATABASE_URL instead
# DATABASE_URL=postgres://$USER:your-password@localhost:5432/stircraft
EOF
            print_success "Basic .env file created"
        fi
    else
        print_success ".env file found"
    fi
    
    # Load .env file
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
        
        # Check key variables
        if [ -z "$SECRET_KEY" ]; then
            print_error "SECRET_KEY not set in .env"
        else
            print_success "SECRET_KEY is configured"
        fi
        
        if [ "$DEBUG" = "True" ]; then
            print_success "DEBUG mode enabled (good for development)"
        else
            print_warning "DEBUG is False - consider setting DEBUG=True for development"
        fi
        
        if [ -n "$ALLOWED_HOSTS" ]; then
            print_success "ALLOWED_HOSTS configured: $ALLOWED_HOSTS"
        else
            print_warning "ALLOWED_HOSTS not set"
        fi
    fi
}

# =============================================================================
# DATABASE CHECKS
# =============================================================================

check_database() {
    print_header "Checking Database Configuration"
    
    # Load environment variables
    if [ -f ".env" ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    # Set defaults if not in .env
    DB_NAME=${DB_NAME:-stircraft}
    DB_USER=${DB_USER:-$USER}
    DB_HOST=${DB_HOST:-localhost}
    DB_PORT=${DB_PORT:-5432}
    
    print_info "Database config: $DB_USER@$DB_HOST:$DB_PORT/$DB_NAME"
    
    # Test PostgreSQL connection
    if command -v psql &> /dev/null; then
        print_action "Testing PostgreSQL connection..."
        
        # Test if we can connect to PostgreSQL server
        if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c "SELECT 1;" &> /dev/null; then
            print_success "Can connect to PostgreSQL server"
            
            # Check if database exists
            if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
                print_success "Database '$DB_NAME' exists"
            else
                print_warning "Database '$DB_NAME' does not exist"
                print_action "Creating database..."
                PGPASSWORD="$DB_PASSWORD" createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME"
                print_success "Database '$DB_NAME' created"
            fi
            
        else
            print_error "Cannot connect to PostgreSQL server"
            print_info "Common fixes:"
            print_info "1. Check if PostgreSQL is running: sudo systemctl status postgresql"
            print_info "2. Check connection settings in .env file"
            print_info "3. Create database user if needed:"
            print_info "   sudo -u postgres createuser -s $USER"
            print_info "   sudo -u postgres psql -c \"ALTER USER $USER PASSWORD 'yourpassword';\""
            print_info "4. Update DB_PASSWORD in .env file"
            
            # Try to help with user creation
            print_action "Attempting to create database user..."
            if sudo -u postgres createuser -s "$DB_USER" 2>/dev/null; then
                print_success "Database user '$DB_USER' created"
                print_info "Set password with: sudo -u postgres psql -c \"ALTER USER $DB_USER PASSWORD 'yourpassword';\""
                print_info "Then update DB_PASSWORD in .env file"
            else
                print_warning "Could not create database user (may already exist)"
            fi
        fi
    else
        print_error "psql command not available"
    fi
}

# =============================================================================
# DJANGO CHECKS
# =============================================================================

check_django_setup() {
    print_header "Checking Django Configuration"
    
    # Change to Django directory if needed
    if [ -d "$DJANGO_DIR" ]; then
        cd "$DJANGO_DIR"
    fi
    
    # Check if we can import Django
    if python -c "import django; django.setup()" 2>/dev/null; then
        print_success "Django imports successfully"
    else
        print_error "Cannot import Django"
        print_info "Check that virtual environment is activated and dependencies are installed"
        cd ..
        return 1
    fi
    
    # Test Django settings
    print_action "Testing Django settings..."
    if python manage.py check --deploy 2>/dev/null; then
        print_success "Django configuration is valid"
    else
        print_warning "Django check found issues (running in development mode)"
        python manage.py check
    fi
    
    # Check for migrations
    print_action "Checking for pending migrations..."
    if python manage.py showmigrations --plan | grep -q "\[ \]"; then
        print_warning "Pending migrations found"
        print_action "Running migrations..."
        python manage.py migrate
        print_success "Migrations applied"
    else
        print_success "All migrations are up to date"
    fi
    
    # Check for superuser
    print_action "Checking for superuser..."
    if python manage.py shell -c "from django.contrib.auth.models import User; print('Superuser exists' if User.objects.filter(is_superuser=True).exists() else 'No superuser')" | grep -q "No superuser"; then
        print_warning "No superuser found"
        print_action "Create superuser with: python manage.py createsuperuser"
    else
        print_success "Superuser exists"
    fi
    
    cd ..
}

# =============================================================================
# STATIC FILES CHECK
# =============================================================================

check_static_files() {
    print_header "Checking Static Files"
    
    if [ -d "$DJANGO_DIR" ]; then
        cd "$DJANGO_DIR"
        
        # Collect static files
        print_action "Collecting static files..."
        python manage.py collectstatic --noinput --clear
        print_success "Static files collected"
        
        cd ..
    fi
}

# =============================================================================
# FINAL TESTS
# =============================================================================

run_final_tests() {
    print_header "Running Final Tests"
    
    if [ -d "$DJANGO_DIR" ]; then
        cd "$DJANGO_DIR"
        
        # Test server start
        print_action "Testing development server startup..."
        timeout 10s python manage.py runserver --noreload &> /dev/null &
        SERVER_PID=$!
        sleep 3
        
        if kill -0 $SERVER_PID 2>/dev/null; then
            print_success "Development server starts successfully"
            kill $SERVER_PID 2>/dev/null
        else
            print_error "Development server failed to start"
            print_info "Try running manually: python manage.py runserver"
        fi
        
        cd ..
    fi
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

main() {
    echo -e "${PURPLE}"
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║                StirCraft Dev Setup Checker               ║"
    echo "║            Diagnosing and fixing common issues          ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_system_requirements
    check_python_environment
    check_environment_variables
    check_database
    check_django_setup
    check_static_files
    run_final_tests
    
    print_header "Setup Complete!"
    print_success "Your development environment should be ready"
    print_info "To start development server:"
    print_info "  1. Activate virtual environment: source .venv/bin/activate"
    print_info "  2. Navigate to Django directory: cd $DJANGO_DIR"
    print_info "  3. Start server: python manage.py runserver"
    print_info "  4. Visit: http://localhost:8000"
    
    if [ -f ".env" ]; then
        print_warning "Don't forget to review and update .env file with your actual values"
    fi
}

# Make sure script is executable and run main function
if [ "$0" = "${BASH_SOURCE[0]}" ]; then
    main "$@"
fi
