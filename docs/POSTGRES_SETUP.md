# PostgreSQL Setup for StirCraft Testing

## The Problem
The project uses PostgreSQL, but teammates often hit connection errors when running tests because:
1. PostgreSQL user `macfarley` needs a password set
2. Database environment variables aren't configured
3. The `stircraft` database might not exist

## The Solution

### One-Time Setup (for each new machine)

1. **Set PostgreSQL password for your user:**
   ```bash
   sudo -u postgres psql -c "ALTER USER $(whoami) PASSWORD 'stircraft123';"
   ```

2. **Create the database (if needed):**
   ```bash
   sudo -u postgres psql -c "CREATE DATABASE stircraft OWNER $(whoami);" 2>/dev/null || echo "Database already exists"
   ```

3. **Test your connection:**
   ```bash
   DB_PASSWORD=stircraft123 psql -h localhost -U $(whoami) -d stircraft -c "SELECT current_user;"
   ```

### Running Tests

**Simple way (recommended):**
```bash
DB_PASSWORD=stircraft123 python stircraft/manage.py test stir_craft
```

**With environment variable:**
```bash
export DB_PASSWORD=stircraft123
python stircraft/manage.py test stir_craft
```

**Full verbose output:**
```bash
DB_PASSWORD=stircraft123 python stircraft/manage.py test stir_craft --verbosity=2
```

## Environment Variables
The project uses these PostgreSQL settings (from `settings.py`):
- `DB_ENGINE`: `django.db.backends.postgresql` (default)
- `DB_NAME`: `stircraft` (default)
- `DB_USER`: your username (default)
- `DB_PASSWORD`: **REQUIRED** - set to `stircraft123`
- `DB_HOST`: `localhost` (default)
- `DB_PORT`: `5432` (default)

## Troubleshooting

**"password authentication failed"** → Run the setup commands above

**"database does not exist"** → Run the database creation command above

**"connection refused"** → Start PostgreSQL: `sudo systemctl start postgresql`

## Making It Permanent
Add this to your `~/.bashrc` or `~/.zshrc`:
```bash
export DB_PASSWORD=stircraft123
```

Then run `source ~/.bashrc` (or `source ~/.zshrc`)
