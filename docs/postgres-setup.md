# PostgreSQL Setup for StirCraft Testing

## The Problem
The project uses PostgreSQL, but teammates often hit connection errors when running tests because:
1. PostgreSQL user `macfarley` needs a password set
2. Environment variables aren't configured properly
3. The `stircraft` database might not exist

## The Solution (NEW!)

### ⚠️ Important: Secrets Management Update
This project now uses **environment files (.env)** for secure secrets management. Never set database passwords directly in shell commands or commit them to git.

### One-Time Setup (for each new machine)

1. **Set PostgreSQL password for your user:**
   ```bash
   sudo -u postgres psql -c "ALTER USER $(whoami) PASSWORD 'your-secure-password';"
   ```
   **Note**: Choose a secure password, not the example passwords shown in documentation.

2. **Create the database (if needed):**
   ```bash
   sudo -u postgres psql -c "CREATE DATABASE stircraft OWNER $(whoami);" 2>/dev/null || echo "Database already exists"
   ```

3. **Create your .env file:**
   ```bash
   # In the stir-craft project root
   cp .env.example .env
   
   # Edit .env and set your actual database password
   nano .env  # or use your preferred editor
   ```

4. **Update your .env file:**
   ```bash
   # In .env file, set your actual database password:
   DATABASE_URL=postgres://your-username:your-secure-password@localhost:5432/stircraft
   ```

5. **Test your connection:**
   ```bash
   # From the stircraft/ directory
   python manage.py check
   # Should show: "Loading .env environment variables..."
   
   python manage.py migrate
   # Should connect without errors
   ```

### Running Tests

**New way (recommended):**
```bash
# From stircraft/ directory - .env is loaded automatically
python manage.py test stir_craft
```

**With verbose output:**
```bash
python manage.py test stir_craft --verbosity=2
```

**Using the test script:**
```bash
# From project root
./scripts/run_tests.sh
```

### ⚠️ Old Method (DEPRECATED)
```bash
# ❌ Don't do this anymore - use .env files instead
DB_PASSWORD=stircraft123 python manage.py test
export DB_PASSWORD=stircraft123
```

## Environment Variables
The project now uses **django-environ** with these settings:

#### Required in .env:
- `SECRET_KEY`: Generate a unique Django secret key
- `DEBUG`: `True` for development, `False` for production
- `DATABASE_URL`: Complete database connection string (recommended)

#### Alternative Database Variables:
- `DB_ENGINE`: `django.db.backends.postgresql` (default)
- `DB_NAME`: `stircraft` (default)
- `DB_USER`: your username (default)
- `DB_PASSWORD`: your secure database password
- `DB_HOST`: `localhost` (default)
- `DB_PORT`: `5432` (default)

#### Your .env file should look like:
```bash
SECRET_KEY=your-generated-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://macfarley:your-password@localhost:5432/stircraft
```

## Troubleshooting

**"Loading .env environment variables..." not showing**
```bash
# Check if .env exists in project root
ls -la .env

# Check if django-environ is installed
pipenv run pip list | grep django-environ
```

**"password authentication failed"**
```bash
# Verify your database password is correct
psql -U $(whoami) -d stircraft
# If this fails, update your .env file with the correct password
```

**"database does not exist"**
```bash
# Create the database
sudo -u postgres psql -c "CREATE DATABASE stircraft OWNER $(whoami);"
```

**"connection refused"**
```bash
# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS
```

**"ImproperlyConfigured: Missing SECRET_KEY"**
```bash
# Generate a new secret key
pipenv run python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"
# Copy the output to your .env file
```

## Security Best Practices

### ✅ DO:
- Use unique passwords for each developer
- Keep your .env file private (it's in .gitignore)
- Generate unique SECRET_KEY for each environment
- Use the .env.example as a template

### ❌ DON'T:
- Commit .env files to git (they're automatically ignored)
- Share actual passwords in documentation or chat
- Use the example passwords (`stircraft123`) in production
- Set sensitive environment variables in shell profiles

## Team Workflow

1. **New team member joins:**
   ```bash
   cp .env.example .env
   # Edit .env with their own secure values
   ```

2. **New environment variable needed:**
   ```bash
   # Add to .env.example (without actual values)
   # Document in this file
   # Commit .env.example changes
   ```

3. **Production deployment:**
   ```bash
   # Use platform-specific secret management
   # GitHub Actions: Repository secrets
   # Heroku: Config vars
   # AWS: Parameter Store
   ```
