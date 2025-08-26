#!/bin/bash

# =============================================================================
# StirCraft Quick Fix Script
# =============================================================================
# A streamlined script for common development environment fixes
# Run from project root: ./quick-fix.sh
# =============================================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ $1${NC}"; }

echo -e "${BLUE}StirCraft Quick Fix - Setting up development environment...${NC}\n"

# 1. Create and activate virtual environment
if [ ! -d ".venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv .venv
    print_success "Virtual environment created"
fi

print_info "Activating virtual environment..."
source .venv/bin/activate
print_success "Virtual environment activated"

# 2. Install dependencies
print_info "Installing Python dependencies..."
pip install -r requirements.txt
print_success "Dependencies installed"

# 3. Setup .env file
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env file created from template"
    else
        cat > .env << EOF
SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_ENGINE=django.db.backends.postgresql
DB_NAME=stircraft
DB_USER=$USER
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432
EOF
        print_success "Basic .env file created"
    fi
    print_warning "Please edit .env file and set your database password"
else
    print_success ".env file already exists"
fi

# 4. Check/create database
print_info "Setting up database..."
cd stircraft

# Try to run migrations
if python manage.py migrate 2>/dev/null; then
    print_success "Database migrations completed"
else
    print_warning "Database migration failed - you may need to:"
    print_info "1. Install PostgreSQL: sudo apt-get install postgresql postgresql-contrib"
    print_info "2. Start PostgreSQL: sudo systemctl start postgresql"
    print_info "3. Create database user: sudo -u postgres createuser -s $USER"
    print_info "4. Set password: sudo -u postgres psql -c \"ALTER USER $USER PASSWORD 'yourpassword';\""
    print_info "5. Update DB_PASSWORD in .env file"
    print_info "6. Create database: createdb stircraft"
fi

# 5. Collect static files
print_info "Collecting static files..."
python manage.py collectstatic --noinput --clear 2>/dev/null || print_warning "Static files collection skipped"

cd ..

echo -e "\n${GREEN}Quick setup complete!${NC}"
echo -e "${BLUE}To start the development server:${NC}"
echo "  1. source .venv/bin/activate"
echo "  2. cd stircraft"
echo "  3. python manage.py runserver"
echo -e "\n${YELLOW}If you see database errors, run the comprehensive check:${NC}"
echo "  ./dev-setup-check.sh"
