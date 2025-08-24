# StirCraft Quick Setup Guide

## 🚀 Get Running in 10 Minutes

**Follow these steps in order for a smooth setup:**

### 1. Prerequisites Check
```bash
# Check if you have these installed:
python3 --version    # Should be 3.12+
psql --version       # PostgreSQL client
pip --version        # Python package manager
```

### 2. Database Setup (One-time)
```bash
# Create PostgreSQL user with password
sudo -u postgres psql -c "ALTER USER $(whoami) PASSWORD 'stircraft123';"

# Create database 
sudo -u postgres createdb --owner=$(whoami) stircraft

# Set environment variable (optional but recommended)
echo 'export DB_PASSWORD="stircraft123"' >> ~/.bashrc
source ~/.bashrc  # or restart terminal
```

### 3. Application Setup (One-time)
```bash
# Clone and setup project
git clone <repo-url>
cd stir-craft

# Install dependencies
pipenv install

# Run migrations  
DB_PASSWORD=stircraft123 pipenv run python stircraft/manage.py migrate

# Import test data (optional but recommended)
DB_PASSWORD=stircraft123 pipenv run python stircraft/manage.py seed_from_thecocktaildb --limit 10
```

### 4. Verify Everything Works
```bash
# Run the test suite to make sure everything is set up correctly
./scripts/run_tests.sh

# If tests pass, you're good to go!
```

### 5. Daily Development
```bash
# Navigate to project
cd stir-craft

# Start development server
DB_PASSWORD=stircraft123 pipenv run python stircraft/manage.py runserver

# Visit: http://127.0.0.1:8000
```

## 🛠 Available Scripts

**From project root:**
```bash
./scripts/run_tests.sh              # Run all tests (use this often!)
./scripts/run_tests.sh --verbose    # Detailed test output
./scripts/update_branches_team.sh   # Sync with team changes
./scripts/update_test_report.py     # Generate test failure report
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| `password authentication failed` | Run the database setup commands again |
| `database "stircraft" does not exist` | `sudo -u postgres createdb --owner=$(whoami) stircraft` |
| `No module named 'django'` | Run `pipenv install` then use `pipenv run` |
| `connection refused` | Start PostgreSQL: `sudo systemctl start postgresql` |
| `tests fail` | Check `docs/POSTGRES_SETUP.md` for detailed DB setup |

## ✅ Success Indicators

You're set up correctly when:
- [ ] `./scripts/run_tests.sh` shows "57/57 tests passing"
- [ ] Development server starts without errors
- [ ] You can visit http://127.0.0.1:8000 and see the app

## 📚 Next Steps

**After setup works:**
1. **Database Details**: `docs/POSTGRES_SETUP.md` (if you had DB issues)
2. **Development Workflow**: `docs/DEVELOPMENT_GUIDE.md`  
3. **Test Status**: `docs/TEST_FAILURE_REPORT.md`
4. **Recent Changes**: `docs/PROJECT_CHANGELOG.md`

---

*Having trouble? The database setup is the most common issue - see `docs/POSTGRES_SETUP.md` for detailed help.*
