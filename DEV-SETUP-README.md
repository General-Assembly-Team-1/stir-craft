# StirCraft Development Environment Setup Scripts

This directory contains scripts to help diagnose and fix common issues when setting up the StirCraft Django project for local development.

## Scripts Overview

### 🔧 `dev-setup-check.sh` - Comprehensive Diagnostic Tool

A thorough script that checks and fixes all aspects of your development environment:

- ✅ System requirements (Python, PostgreSQL)
- ✅ Virtual environment setup
- ✅ Python dependencies
- ✅ Environment variables (.env file)
- ✅ Database connection and setup
- ✅ Django configuration
- ✅ Static files collection
- ✅ Development server test

**Usage:**
```bash
./dev-setup-check.sh
```

### ⚡ `quick-fix.sh` - Fast Setup for Common Issues

A streamlined script for quick environment setup:

- Creates virtual environment
- Installs dependencies
- Sets up basic .env file
- Runs database migrations
- Collects static files

**Usage:**
```bash
./quick-fix.sh
```

## Common Issues and Solutions

### 1. Virtual Environment Issues
If you see "Django not found" or import errors:
```bash
# Run quick fix to create and setup virtual environment
./quick-fix.sh

# Or manually:
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. PostgreSQL Connection Issues
If you get database connection errors:

**Install PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start PostgreSQL service
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

**Create database user:**
```bash
sudo -u postgres createuser -s $USER
sudo -u postgres psql -c "ALTER USER $USER PASSWORD 'yourpassword';"
```

**Create database:**
```bash
createdb stircraft
```

**Update .env file:**
```env
DB_PASSWORD=yourpassword
```

### 3. Environment Variables Issues
If you see SECRET_KEY or configuration errors:

```bash
# Copy template and edit
cp .env.example .env
# Edit .env file with your actual values
```

Required variables:
- `SECRET_KEY` - Django secret key
- `DEBUG=True` - For development
- `DB_PASSWORD` - Your PostgreSQL password

### 4. Migration Issues
If you see database table errors:

```bash
cd stircraft
python manage.py makemigrations
python manage.py migrate
```

### 5. Static Files Issues
If CSS/JS files don't load:

```bash
cd stircraft
python manage.py collectstatic --noinput --clear
```

## Step-by-Step Manual Setup

If scripts don't work, follow these manual steps:

1. **Check you're in the right directory:**
   ```bash
   ls -la | grep manage.py  # Should see stircraft/manage.py
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your values
   ```

5. **Setup database:**
   ```bash
   createdb stircraft  # Create database
   cd stircraft
   python manage.py migrate
   ```

6. **Create superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files:**
   ```bash
   python manage.py collectstatic --noinput
   ```

8. **Test server:**
   ```bash
   python manage.py runserver
   ```

## Troubleshooting

### Permission Denied
```bash
chmod +x dev-setup-check.sh quick-fix.sh
```

### Python Version Issues
This project requires Python 3.12. Use pyenv to manage versions:
```bash
pyenv install 3.12.0
pyenv local 3.12.0
```

### Database User Issues
If you can't create users:
```bash
sudo -u postgres psql
CREATE USER yourusername WITH SUPERUSER PASSWORD 'yourpassword';
\q
```

### Still Having Issues?

1. Run the comprehensive check: `./dev-setup-check.sh`
2. Check the error messages carefully
3. Ensure PostgreSQL is running: `sudo systemctl status postgresql`
4. Verify your .env file has correct database credentials
5. Make sure virtual environment is activated: `which python` should show `.venv/bin/python`

## Getting Help

If you're still stuck:
1. Check the error output from the scripts
2. Look at Django logs when running `python manage.py runserver`
3. Verify all services are running (PostgreSQL)
4. Double-check file permissions and paths
