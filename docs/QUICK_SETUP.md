# StirCraft Quick Setup Guide

## 🚀 Get Running in 5 Minutes

### Prerequisites Check
```bash
# Check if you have these installed:
python3 --version    # Should be 3.12+
psql --version       # PostgreSQL client
pip --version        # Python package manager
```

### Database Setup (One-time)
```bash
# 1. Create PostgreSQL user and database
sudo -u postgres createuser --interactive --pwprompt macfarley
# Enter password: stircraft123

sudo -u postgres createdb --owner=macfarley stircraft

# 2. Set environment variable (add to ~/.bashrc or ~/.zshrc)
export DB_PASSWORD="stircraft123"
```

### Application Setup (One-time)
```bash
# 3. Clone and setup project
git clone <repo-url>
cd stir-craft
pipenv install

# 4. Run migrations
export DB_PASSWORD="stircraft123"
pipenv run python stircraft/manage.py migrate

# 5. Import test data (optional)
pipenv run python stircraft/manage.py seed_from_thecocktaildb --limit 10
```

### Daily Development
```bash
# Navigate to project
cd stir-craft

# Set database password
export DB_PASSWORD="stircraft123"

# Start development server
pipenv run python stircraft/manage.py runserver
```

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| `password authentication failed` | `sudo -u postgres psql -c "ALTER USER macfarley PASSWORD 'stircraft123';"` |
| `database "stircraft" does not exist` | `sudo -u postgres createdb --owner=macfarley stircraft` |
| `No module named 'django'` | Run `pipenv install` then use `pipenv run` |
| `connection refused` | Start PostgreSQL: `sudo systemctl start postgresql` |

## 📚 Full Documentation

- **Complete Setup**: `docs/DEVELOPMENT_GUIDE.md`
- **CSS Guidelines**: `docs/CSS_ORGANIZATION.md`  
- **Recent Changes**: `docs/PROJECT_CHANGELOG.md`

---

*Need help? Check the full DEVELOPMENT_GUIDE.md or ask the team!*
