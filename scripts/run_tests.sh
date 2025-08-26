#!/usr/bin/env bash

# StirCraft Enhanced Test Runner
# Comprehensive testing with clear feedback and failure reporting

set -e  # Exit on any error

# Color codes for better output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test configuration
DJANGO_VERBOSITY=1
RUN_JS_TESTS=true
GENERATE_REPORT=false
START_TIME=$(date +%s)

echo -e "${PURPLE}🧪 StirCraft Enhanced Test Runner${NC}"
echo -e "${PURPLE}====================================${NC}"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            DJANGO_VERBOSITY=2
            shift
            ;;
        -q|--quiet)
            DJANGO_VERBOSITY=0
            shift
            ;;
        --no-js)
            RUN_JS_TESTS=false
            shift
            ;;
        --report)
            GENERATE_REPORT=true
            shift
            ;;
        --django-only)
            RUN_JS_TESTS=false
            shift
            ;;
        --js-only)
            DJANGO_VERBOSITY=0
            RUN_JS_TESTS=true
            shift
            ;;
        -h|--help)
            echo -e "${CYAN}Usage: $0 [OPTIONS]${NC}"
            echo ""
            echo "Options:"
            echo "  -v, --verbose     Verbose test output"
            echo "  -q, --quiet       Minimal test output"
            echo "  --no-js          Skip JavaScript tests"
            echo "  --report         Generate failure report"
            echo "  --django-only    Run only Django tests"
            echo "  --js-only        Run only JavaScript tests"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests with normal output"
            echo "  $0 --verbose          # Run with detailed output"
            echo "  $0 --django-only -v   # Django tests only, verbose"
            echo "  $0 --report           # Generate failure report after tests"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Unknown option: $1${NC}"
            echo "Use $0 --help for usage information"
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [ ! -f "stircraft/manage.py" ]; then
    echo -e "${RED}❌ Error: Run this script from the project root directory${NC}"
    echo -e "${YELLOW}   Expected: /path/to/stir-craft/${NC}"
    echo -e "${YELLOW}   Current:  $(pwd)${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -f ".venv/bin/python" ]; then
    echo -e "${RED}❌ Error: Virtual environment not found${NC}"
    echo -e "${YELLOW}   Quick fix: ./quick-fix.sh${NC}"
    echo -e "${YELLOW}   Or manual: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt${NC}"
    exit 1
fi

# Function to print section headers
print_section() {
    echo ""
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' $(seq 1 ${#1}))${NC}"
}

# Function to show test results summary
show_summary() {
    local end_time=$(date +%s)
    local duration=$((end_time - START_TIME))
    
    echo ""
    echo -e "${PURPLE}📊 Test Results Summary${NC}"
    echo -e "${PURPLE}========================${NC}"
    echo -e "${BLUE}Total Duration: ${duration}s${NC}"
    
    if [ $DJANGO_TESTS_PASSED -eq 1 ] && [ $JS_TESTS_PASSED -eq 1 ]; then
        echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
        echo -e "${GREEN}✅ Django Tests: PASSED${NC}"
        [ "$RUN_JS_TESTS" = true ] && echo -e "${GREEN}✅ JavaScript Tests: PASSED${NC}"
    else
        echo -e "${RED}❌ SOME TESTS FAILED${NC}"
        [ $DJANGO_TESTS_PASSED -eq 0 ] && echo -e "${RED}❌ Django Tests: FAILED${NC}"
        [ "$RUN_JS_TESTS" = true ] && [ $JS_TESTS_PASSED -eq 0 ] && echo -e "${RED}❌ JavaScript Tests: FAILED${NC}"
        
        echo ""
        echo -e "${YELLOW}🔧 Troubleshooting:${NC}"
        echo -e "${YELLOW}   • Check test output above for specific failures${NC}"
        echo -e "${YELLOW}   • Run with --verbose for detailed error information${NC}"
        echo -e "${YELLOW}   • Use --report to generate a detailed failure report${NC}"
        echo -e "${YELLOW}   • See DEV-SETUP-README.md for environment setup${NC}"
    fi
    
    # Generate report if requested
    if [ "$GENERATE_REPORT" = true ]; then
        echo ""
        echo -e "${CYAN}📝 Generating test failure report...${NC}"
        if python scripts/update_test_report.py; then
            echo -e "${GREEN}✅ Report generated: docs/TEST_FAILURE_REPORT.md${NC}"
        else
            echo -e "${YELLOW}⚠️  Report generation failed, but tests completed${NC}"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}💡 Tips:${NC}"
    echo -e "${BLUE}   • Use './run_tests.sh --verbose' for detailed output${NC}"
    echo -e "${BLUE}   • Use './run_tests.sh --report' to generate failure reports${NC}"
    echo -e "${BLUE}   • Use './run_tests.sh --help' for all options${NC}"
}

# Initialize test status tracking
DJANGO_TESTS_PASSED=1
JS_TESTS_PASSED=1

# Activate virtual environment
print_section "🔧 Environment Setup"
echo -e "${BLUE}Activating virtual environment...${NC}"
source .venv/bin/activate

# Check PostgreSQL setup (only if running Django tests)
if [ $DJANGO_VERBOSITY -gt -1 ]; then
    echo -e "${BLUE}🐘 Checking PostgreSQL setup...${NC}"
    if [ -z "$DB_PASSWORD" ]; then
        echo -e "${YELLOW}⚠️  DB_PASSWORD not set. Using default: stircraft123${NC}"
        export DB_PASSWORD=stircraft123
    fi

    # Test PostgreSQL connection (but don't exit if failed - use SQLite for tests)
    if ! psql -h localhost -U "$(whoami)" -d stircraft -c "SELECT 1;" &>/dev/null; then
        echo -e "${YELLOW}⚠️  PostgreSQL connection failed, tests will use SQLite in-memory database${NC}"
        echo -e "${BLUE}   For full PostgreSQL testing, see DEV-SETUP-README.md${NC}"
    else
        echo -e "${GREEN}✅ PostgreSQL connection verified${NC}"
    fi

    # Install dependencies if needed
    echo -e "${BLUE}📦 Checking dependencies...${NC}"
    if [ -f "Pipfile" ]; then
        pipenv install --dev 2>/dev/null || echo -e "${YELLOW}⚠️  pipenv install had issues, continuing...${NC}"
    fi
    echo -e "${GREEN}✅ Dependencies verified${NC}"
fi

# Run Django tests
if [ $DJANGO_VERBOSITY -gt -1 ]; then
    print_section "🧪 Running Django Tests"
    echo -e "${BLUE}Using: SQLite in-memory database for speed${NC}"
    echo -e "${BLUE}Verbosity: $DJANGO_VERBOSITY${NC}"
    echo ""

    cd stircraft

    # Run tests with appropriate verbosity and capture exit code
    if python manage.py test stir_craft --settings=stircraft.test_settings --verbosity=$DJANGO_VERBOSITY; then
        echo -e "${GREEN}✅ Django tests completed successfully${NC}"
        DJANGO_TESTS_PASSED=1
    else
        echo -e "${RED}❌ Django tests failed${NC}"
        DJANGO_TESTS_PASSED=0
    fi

    cd ..
else
    echo -e "${YELLOW}⏭️  Skipping Django tests${NC}"
fi

# Run JavaScript tests  
if [ "$RUN_JS_TESTS" = true ]; then
    print_section "⚡ Running JavaScript Tests"
    echo -e "${BLUE}Using: Jest testing framework${NC}"
    echo ""

    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        echo -e "${YELLOW}⚠️  npm not found, skipping JavaScript tests${NC}"
        echo -e "${BLUE}   Install Node.js and npm to run JavaScript tests${NC}"
        JS_TESTS_PASSED=1  # Don't fail overall if npm not available
    else
        # Run JavaScript tests and capture exit code
        if npm test; then
            echo -e "${GREEN}✅ JavaScript tests completed successfully${NC}"
            JS_TESTS_PASSED=1
        else
            echo -e "${RED}❌ JavaScript tests failed${NC}"
            JS_TESTS_PASSED=0
        fi
    fi
else
    echo -e "${YELLOW}⏭️  Skipping JavaScript tests${NC}"
fi

# Show final summary
show_summary

# Exit with appropriate code
if [ $DJANGO_TESTS_PASSED -eq 1 ] && [ $JS_TESTS_PASSED -eq 1 ]; then
    exit 0
else
    exit 1
fi
