# 🚀 StirCraft Setup Guide

Complete setup instructions for getting StirCraft running locally.

## 📋 **Prerequisites**

Ensure you have these installed:
```bash
python3 --version    # Should be 3.12+
psql --version       # PostgreSQL client
pip --version        # Python package manager
```

### **Install Prerequisites (if needed)**

#### **Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3.12 python3-pip postgresql postgresql-contrib
pip install pipenv
```

#### **macOS:**
```bash
brew install python@3.12 postgresql
pip install pipenv
```

#### **Windows:**
- Install [Python 3.12+](https://python.org)
- Install [PostgreSQL](https://postgresql.org)
- Install pipenv: `pip install pipenv`

## 🗄️ **Database Setup**

### **1. Start PostgreSQL Service**
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# macOS
brew services start postgresql

# Verify it's running
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS
```

### **2. Create Database User & Database**
```bash
# Create user with password
sudo -u postgres psql -c "ALTER USER $(whoami) PASSWORD 'stircraft123';"

# Create database
sudo -u postgres createdb --owner=$(whoami) stircraft

# Verify database creation
psql -d stircraft -c "SELECT version();"
```

### **3. Set Environment Variable (Optional)**
```bash
# Add to your shell profile for convenience
echo 'export DB_PASSWORD="stircraft123"' >> ~/.bashrc
source ~/.bashrc  # or restart terminal
```

## 🛠️ **Application Setup**

### **1. Clone Repository**
```bash
git clone <repository-url>
cd stir-craft/stircraft
```

### **2. Install Dependencies**
```bash
# Install Python dependencies
pipenv install

# Verify installation
pipenv --version
```

### **3. Environment Configuration**
```bash
# Create .env file for local secrets
cat << EOF > .env
DEBUG=True
DB_PASSWORD=stircraft123
SECRET_KEY=your-secret-key-here
EOF
```

### **4. Database Migration**
```bash
# Apply database migrations
DB_PASSWORD=stircraft123 pipenv run python manage.py migrate

# Verify migration success
DB_PASSWORD=stircraft123 pipenv run python manage.py showmigrations
```

### **5. Create Demo Data (Recommended)**
```bash
# Option 1: Full demo database (recommended for presentations)
pipenv run python manage.py seed_dynamic_database --limit 100 --num-users 10

# Option 2: Quick test data
pipenv run python manage.py seed_from_thecocktaildb --limit 25

# Option 3: Minimal setup (no demo data)
# Skip this step for empty database
```

### **6. Verify Setup**
```bash
# Run test suite
./scripts/run_tests.sh

# Start development server
DB_PASSWORD=stircraft123 pipenv run python manage.py runserver
```

## ✅ **Verification Checklist**

Your setup is successful when:
- [ ] PostgreSQL service is running
- [ ] Database `stircraft` exists and is accessible
- [ ] `./scripts/run_tests.sh` shows all tests passing
- [ ] Development server starts without errors
- [ ] You can visit http://127.0.0.1:8000 and see the app
- [ ] Demo data is loaded (if you chose that option)

## 🎯 **Daily Development Workflow**

```bash
# Navigate to project
cd stir-craft/stircraft

# Start development server
DB_PASSWORD=stircraft123 pipenv run python manage.py runserver

# In another terminal, run tests when making changes
./scripts/run_tests.sh

# Visit your local application
open http://127.0.0.1:8000
```

## 🆘 **Troubleshooting**

### **Database Issues**

| Problem | Solution |
|---------|----------|
| `password authentication failed` | Run database setup commands again |
| `database "stircraft" does not exist` | `sudo -u postgres createdb --owner=$(whoami) stircraft` |
| `connection refused` | Start PostgreSQL: `sudo systemctl start postgresql` |
| `role "username" does not exist` | `sudo -u postgres createuser $(whoami)` |

### **Python/Django Issues**

| Problem | Solution |
|---------|----------|
| `No module named 'django'` | Run `pipenv install` then use `pipenv run` |
| `ImportError` | Check you're in the `stircraft/` directory |
| `SECRET_KEY not found` | Create `.env` file with `SECRET_KEY=your-key` |
| `Permission denied` | Make scripts executable: `chmod +x scripts/*.sh` |

### **Development Server Issues**

| Problem | Solution |
|---------|----------|
| `Port already in use` | Kill existing server: `pkill -f runserver` |
| `Static files not loading` | Run `python manage.py collectstatic` |
| `Templates not found` | Check you're running from `stircraft/` directory |
| `Media files 404` | Ensure `media/` directory exists and has permissions |

### **Test Failures**

```bash
# Run tests with verbose output for debugging
./scripts/run_tests.sh --verbose

# Run specific test file
pipenv run python manage.py test stir_craft.tests.test_models

# Check for missing migrations
pipenv run python manage.py makemigrations --check
```

## 🔧 **Advanced Configuration**

### **Environment Variables**
Create `.env` file for local development:
```bash
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=stircraft
DB_USER=your-username
DB_PASSWORD=stircraft123
DB_HOST=localhost
DB_PORT=5432
```

### **Development Database Reset**
```bash
# WARNING: This deletes all data
pipenv run python manage.py flush
pipenv run python manage.py migrate
pipenv run python manage.py seed_dynamic_database
```

### **Production-like Setup**
```bash
# Use production settings
export DJANGO_SETTINGS_MODULE=stircraft.settings
export DEBUG=False

# Collect static files
pipenv run python manage.py collectstatic

# Use a production server (optional)
pipenv install gunicorn
pipenv run gunicorn stircraft.wsgi:application
```

## 📚 **Next Steps**

After successful setup:
1. **Explore the Application** - Browse demo data and features
2. **Review Documentation** - Check `docs/development-workflow.md`
3. **Run Tests** - Understand the test suite with `./scripts/run_tests.sh`
4. **Start Development** - Begin adding features or fixing issues

## 🔗 **Related Documentation**

- **[Development Workflow](development-workflow.md)** - Coding standards and practices
- **[Database Schema](database-schema.md)** - Understanding the data model
- **[Testing Framework](testing-framework.md)** - How to write and run tests
- **[Dynamic Seeding](DYNAMIC_SEEDING_DOCUMENTATION.md)** - Demo data generation

---

*Having trouble? Check the troubleshooting section above or create an issue with your error message and system details.*
