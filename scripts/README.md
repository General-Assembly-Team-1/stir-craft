# StirCraft Scripts

This folder contains utility scripts to make development easier.

## 🧪 Testing Scripts

### `run_tests.sh`
**Purpose:** Run Django tests with proper PostgreSQL setup  
**Usage:**
```bash
./scripts/run_tests.sh           # Standard test run
./scripts/run_tests.sh --verbose # Detailed output
./scripts/run_tests.sh --quiet   # Minimal output
```

**What it does:**
- Checks PostgreSQL connection
- Activates virtual environment
- Runs all tests with proper database credentials
- Provides clear error messages if setup is missing

### `update_test_report.py`
**Purpose:** Auto-generate test failure reports  
**Usage:**
```bash
python scripts/update_test_report.py
```

**What it does:**
- Runs full test suite with detailed output
- Parses test results and failures
- Updates `docs/TEST_FAILURE_REPORT.md` automatically
- Shows summary of test status

## 🌿 Git/Branch Scripts

### `update_branches_team.sh`
**Purpose:** Sync local repository with team changes  
**Usage:**
```bash
./scripts/update_branches_team.sh
```

**What it does:**
- Fetches latest changes from remote
- Updates all local branches
- Helps avoid merge conflicts

### `update_branches.sh`
**Purpose:** Basic branch updating (simpler version)  
**Usage:**
```bash
./scripts/update_branches.sh
```

## 📋 Development Workflow

**Before starting work:**
```bash
./scripts/update_branches_team.sh  # Get latest changes
./scripts/run_tests.sh             # Verify everything works
```

**Before committing:**
```bash
./scripts/run_tests.sh             # Make sure your changes don't break tests
git add . && git commit -m "..."   # Commit if tests pass
```

**When debugging test failures:**
```bash
./scripts/run_tests.sh --verbose   # See detailed test output
python scripts/update_test_report.py  # Generate detailed failure report
```

## 🔧 Making Scripts Executable

If you get "permission denied" errors:
```bash
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

## 💡 Tips

- All scripts are designed to be run from the project root directory
- Scripts will check for common setup issues and provide helpful error messages
- Use `./scripts/run_tests.sh` instead of manual `python manage.py test` commands
- The test runner handles all the PostgreSQL environment setup automatically
