#!/usr/bin/env python3
"""
Test Failure Report Generator for StirCraft

Runs Django tests and automatically updates docs/TEST_FAILURE_REPORT.md
with current test status and any failure details.
"""

import subprocess
import sys
import os
import re
from datetime import datetime
from pathlib import Path


def run_tests_and_capture_output():
    """Run Django tests and capture all output."""
    original_dir = os.getcwd()
    
    try:
        os.chdir('stircraft')
        
        # Set environment for test database
        env = os.environ.copy()
        if 'DB_PASSWORD' not in env:
            env['DB_PASSWORD'] = 'stircraft123'
        
        # Run tests with test settings for reliability
        cmd = [
            sys.executable, 'manage.py', 'test', 'stir_craft', 
            '--settings=stircraft.test_settings',
            '--verbosity=2', 
            '--keepdb'
        ]
        
        print("🧪 Running Django tests...")
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            env=env,
            timeout=600  # 10 minute timeout
        )
        
        # Also run JavaScript tests if npm is available
        js_output = ""
        js_status = 0
        
        os.chdir('..')  # Back to project root
        
        if os.path.exists('package.json'):
            print("⚡ Running JavaScript tests...")
            try:
                js_result = subprocess.run(
                    ['npm', 'test'], 
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                js_output = js_result.stdout + "\n" + js_result.stderr
                js_status = js_result.returncode
            except (subprocess.TimeoutExpired, FileNotFoundError):
                js_output = "JavaScript tests could not be run (npm not found or timeout)"
                js_status = -1
        
        return result.returncode, result.stdout, result.stderr, js_status, js_output
        
    except subprocess.TimeoutExpired:
        return -1, "", "Tests timed out after 10 minutes", -1, ""
    finally:
        os.chdir(original_dir)


def parse_test_output(stdout, stderr, js_status, js_output):
    """Parse test output to extract failure information."""
    combined_output = stdout + "\n" + stderr
    
    # Extract Django test stats
    test_count_match = re.search(r'Ran (\d+) tests?', combined_output)
    total_django_tests = int(test_count_match.group(1)) if test_count_match else 0
    
    # Extract JavaScript test stats
    total_js_tests = 0
    js_failures = []
    
    if js_output:
        js_test_match = re.search(r'Tests:\s+(\d+) passed', js_output)
        if js_test_match:
            total_js_tests = int(js_test_match.group(1))
        
        # Check for JS test failures
        if js_status != 0 and "FAIL" in js_output:
            js_fail_match = re.search(r'(FAIL.*?)(?=PASS|\Z)', js_output, re.DOTALL)
            if js_fail_match:
                js_failures.append({
                    'test': 'JavaScript Test Suite',
                    'details': js_fail_match.group(1).strip()
                })
    
    # Check if Django tests passed
    django_passed = "OK" in combined_output or total_django_tests == 0  # Pass if no Django errors or no Django tests
    js_passed = js_status == 0 if js_output else True  # Pass if no JS tests
    
    if django_passed and js_passed:
        return {
            'status': 'PASSING',
            'total_django_tests': total_django_tests,
            'total_js_tests': total_js_tests,
            'failures': [],
            'errors': [],
            'js_failures': []
        }
    
    # Extract Django failures and errors
    failures = []
    errors = []
    
    # Parse FAIL entries
    fail_pattern = r'FAIL: (.*?)\n(.*?)(?=(?:FAIL:|ERROR:|=+)|\Z)'
    for match in re.finditer(fail_pattern, combined_output, re.DOTALL):
        test_name = match.group(1).strip()
        failure_details = match.group(2).strip()
        failures.append({
            'test': test_name,
            'details': failure_details
        })
    
    # Parse ERROR entries  
    error_pattern = r'ERROR: (.*?)\n(.*?)(?=(?:FAIL:|ERROR:|=+)|\Z)'
    for match in re.finditer(error_pattern, combined_output, re.DOTALL):
        test_name = match.group(1).strip()
        error_details = match.group(2).strip()
        errors.append({
            'test': test_name,
            'details': error_details
        })
    
    return {
        'status': 'FAILING',
        'total_django_tests': total_django_tests,
        'total_js_tests': total_js_tests,
        'failures': failures,
        'errors': errors,
        'js_failures': js_failures
    }


def generate_report(test_results):
    """Generate the test failure report content."""
    now = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    
    total_tests = test_results['total_django_tests'] + test_results['total_js_tests']
    
    if test_results['status'] == 'PASSING':
        return f"""# 🎉 StirCraft Test Status Report

**Last Updated:** {now}  
**Status:** ✅ ALL TESTS PASSING  
**Django Tests:** {test_results['total_django_tests']} ✅  
**JavaScript Tests:** {test_results['total_js_tests']} ✅  
**Total Tests:** {total_tests}  
**Success Rate:** 100%  

## 🚀 Current Status

All tests are currently passing! The test infrastructure is stable and ready for development.

### 🧪 Test Coverage
- **Backend (Django):** {test_results['total_django_tests']} tests covering models, views, forms, and integrations
- **Frontend (JavaScript):** {test_results['total_js_tests']} tests covering UI interactions and AJAX functionality

## 🏃 Running Tests

### Quick Commands
```bash
# Run all tests with enhanced output
./scripts/run_tests.sh

# Verbose output for debugging
./scripts/run_tests.sh --verbose

# Django tests only
./scripts/run_tests.sh --django-only

# JavaScript tests only  
./scripts/run_tests.sh --js-only
```

### Manual Commands
```bash
# Django tests with SQLite (fast)
cd stircraft && python manage.py test stir_craft --settings=stircraft.test_settings

# JavaScript tests
npm test
```

## 📚 Resources
- **Setup Help:** See `DEV-SETUP-README.md` for environment setup
- **PostgreSQL Setup:** See `docs/postgres-setup.md` for database configuration
- **Test Documentation:** See individual test files for specific test scenarios

---

*This report was automatically generated by running `python scripts/update_test_report.py`*
"""
    
    # Calculate stats for failing tests
    failure_count = len(test_results['failures'])
    error_count = len(test_results['errors'])
    js_failure_count = len(test_results['js_failures'])
    total_failures = failure_count + error_count + js_failure_count
    
    django_passing = test_results['total_django_tests'] - failure_count - error_count
    js_passing = test_results['total_js_tests'] - js_failure_count
    
    success_rate = ((django_passing + js_passing) / total_tests * 100) if total_tests > 0 else 0
    
    report = f"""# ❌ StirCraft Test Failure Report

**Last Updated:** {now}  
**Status:** {django_passing + js_passing} PASSING ✅ | {total_failures} FAILING ❌  
**Django Tests:** {django_passing}/{test_results['total_django_tests']} passing  
**JavaScript Tests:** {js_passing}/{test_results['total_js_tests']} passing  
**Total Tests:** {total_tests}  
**Success Rate:** {success_rate:.1f}%  

## ❌ Test Failures ({total_failures})

"""
    
    # Add Django failure details
    for i, failure in enumerate(test_results['failures'], 1):
        report += f"""### {i}. Django Test Failure: {failure['test']}
```
{failure['details']}
```

"""
    
    # Add Django error details
    for i, error in enumerate(test_results['errors'], len(test_results['failures']) + 1):
        report += f"""### {i}. Django Test Error: {error['test']}
```
{error['details']}
```

"""
    
    # Add JavaScript failure details
    for i, js_failure in enumerate(test_results['js_failures'], len(test_results['failures']) + len(test_results['errors']) + 1):
        report += f"""### {i}. JavaScript Test Failure: {js_failure['test']}
```
{js_failure['details']}
```

"""
    
    report += f"""## 🚀 Running Tests

### Quick Commands
```bash
# Run all tests with enhanced output
./scripts/run_tests.sh

# Verbose output for debugging
./scripts/run_tests.sh --verbose

# Generate this report after running tests
./scripts/run_tests.sh --report
```

### Manual Commands
```bash
# Django tests with SQLite (fast)
cd stircraft && python manage.py test stir_craft --settings=stircraft.test_settings --verbosity=2

# JavaScript tests
npm test
```

## 🔧 Troubleshooting

### Common Issues
1. **Database Connection Errors:** Use SQLite test settings with `--settings=stircraft.test_settings`
2. **Import Errors:** Ensure virtual environment is activated and dependencies installed
3. **JavaScript Test Failures:** Check that Node.js and npm are properly installed

### Environment Setup
```bash
# Quick environment setup
./quick-fix.sh

# Comprehensive environment check
./dev-setup-check.sh
```

## 📚 Resources
- **Setup Help:** See `DEV-SETUP-README.md` for environment setup
- **PostgreSQL Setup:** See `docs/postgres-setup.md` for database configuration
- **Development Guide:** See `docs/development-guide.md` for coding standards

---

*This report was automatically generated by running `python scripts/update_test_report.py`*
"""
    
    return report


def update_report_file(content):
    """Update the test failure report file."""
    # Ensure the tests directory exists
    tests_dir = Path('tests')
    tests_dir.mkdir(exist_ok=True)
    
    report_path = tests_dir / 'TEST_FAILURE_REPORT.md'
    with open(report_path, 'w') as f:
        f.write(content)
    
    print(f"✅ Updated {report_path}")


def main():
    """Main function to run tests and update report."""
    print("🧪 Running comprehensive test suite and generating report...")
    
    # Run tests
    return_code, stdout, stderr, js_status, js_output = run_tests_and_capture_output()
    
    # Parse results
    test_results = parse_test_output(stdout, stderr, js_status, js_output)
    
    # Generate and save report
    report_content = generate_report(test_results)
    update_report_file(report_content)
    
    # Print summary
    if test_results['status'] == 'PASSING':
        total_tests = test_results['total_django_tests'] + test_results['total_js_tests']
        print(f"🎉 All {total_tests} tests passing!")
        print(f"   Django: {test_results['total_django_tests']} tests ✅")
        print(f"   JavaScript: {test_results['total_js_tests']} tests ✅")
        print(f"📝 Test report generated at tests/TEST_FAILURE_REPORT.md")
    else:
        failure_count = len(test_results['failures'])
        error_count = len(test_results['errors'])
        js_failure_count = len(test_results['js_failures'])
        total_failures = failure_count + error_count + js_failure_count
        
        print(f"⚠️  {total_failures} test failures detected")
        if failure_count > 0:
            print(f"   Django failures: {failure_count}")
        if error_count > 0:
            print(f"   Django errors: {error_count}")
        if js_failure_count > 0:
            print(f"   JavaScript failures: {js_failure_count}")
        print(f"📝 Detailed failure report updated at tests/TEST_FAILURE_REPORT.md")
    
    # Return the worst exit code
    return max(return_code, js_status) if js_output else return_code


if __name__ == '__main__':
    sys.exit(main())
