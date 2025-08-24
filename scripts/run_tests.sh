#!/usr/bin/env bash

# StirCraft Test Runner
# Makes running tests foolproof for all teammates

set -e  # Exit on any error

echo "🧪 StirCraft Test Runner"
echo "======================="

# Check if we're in the right directory
if [ ! -f "stircraft/manage.py" ]; then
    echo "❌ Error: Run this script from the project root directory"
    echo "   Expected: /path/to/stir-craft/"
    echo "   Current:  $(pwd)"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check PostgreSQL setup
echo "🐘 Checking PostgreSQL setup..."
if [ -z "$DB_PASSWORD" ]; then
    echo "⚠️  DB_PASSWORD not set. Using default: stircraft123"
    export DB_PASSWORD=stircraft123
fi

# Test PostgreSQL connection
if ! psql -h localhost -U "$(whoami)" -d stircraft -c "SELECT 1;" &>/dev/null; then
    echo "❌ PostgreSQL connection failed!"
    echo "   Run setup: sudo -u postgres psql -c \"ALTER USER $(whoami) PASSWORD 'stircraft123';\""
    echo "   See docs/POSTGRES_SETUP.md for full setup instructions"
    exit 1
fi

echo "✅ PostgreSQL connection verified"

# Install dependencies if needed
echo "📦 Checking dependencies..."
if [ -f "Pipfile" ]; then
    pipenv install --dev 2>/dev/null || echo "⚠️  pipenv install had issues, continuing..."
fi

# Run tests with PostgreSQL
echo "🏃 Running tests..."
echo "   Using: PostgreSQL database"
echo "   Database: stircraft"
echo ""

cd stircraft

# Run tests with different verbosity levels based on arguments
if [ "$1" = "--verbose" ] || [ "$1" = "-v" ]; then
    python manage.py test stir_craft --verbosity=2
elif [ "$1" = "--quiet" ] || [ "$1" = "-q" ]; then
    python manage.py test stir_craft --verbosity=0
else
    python manage.py test stir_craft --verbosity=1
fi

echo ""
echo "✅ Test run complete!"
echo ""
echo "💡 Tips:"
echo "   • Use './run_tests.sh --verbose' for detailed output"
echo "   • Use './run_tests.sh --quiet' for minimal output"
echo "   • See docs/POSTGRES_SETUP.md for database setup help"
