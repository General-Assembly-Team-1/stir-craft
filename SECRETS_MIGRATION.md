# 🔐 Secrets Management Update - IMPORTANT!

## What Changed
StirCraft now uses **secure environment variables** for all secrets (database passwords, SECRET_KEY, etc). This is a **breaking change** that affects how you set up and run the project.

## For New Team Members

### Quick Setup
```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Generate a unique secret key
pipenv run python -c "from django.core.management.utils import get_random_secret_key; print('SECRET_KEY=' + get_random_secret_key())"

# 3. Edit .env and paste your secret key + database password
nano .env  # or your preferred editor

# 4. Test it works
cd stircraft/
python manage.py check
# Should show: "Loading .env environment variables..."
```

### Your .env should look like:
```bash
SECRET_KEY=your-generated-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://macfarley:your-db-password@localhost:5432/stircraft
```

## For Existing Team Members

### ⚠️ STOP using environment exports
```bash
# ❌ Don't do this anymore:
export DB_PASSWORD=stircraft123
DB_PASSWORD=stircraft123 python manage.py test

# ✅ Do this instead:
# Create .env file (see above)
python manage.py test  # .env is loaded automatically
```

### Migration Steps
1. **Install new dependency**: `pipenv install django-environ`
2. **Create .env file**: Follow "Quick Setup" above
3. **Test it works**: `python manage.py check`
4. **Remove old exports**: Delete `export DB_PASSWORD=...` from your shell profile

## Why This Change?

### Security Benefits
- ✅ Secrets never committed to git
- ✅ Each developer uses unique passwords
- ✅ Production-ready secret management
- ✅ Fails fast in production if secrets are missing

### Team Benefits
- ✅ Consistent setup process
- ✅ No more "forgot to export DB_PASSWORD" errors
- ✅ Easy to add new environment variables
- ✅ Works with any deployment platform

## What's Protected Now
- `SECRET_KEY`: Django's cryptographic secret
- Database credentials (password, host, etc.)
- Future: API keys, email passwords, cloud storage secrets

## Files to Know
- `.env` - Your personal secrets (ignored by git)
- `.env.example` - Template for team (committed to git)
- `.gitignore` - Ensures .env never gets committed

## Troubleshooting

**"Loading .env environment variables..." not showing?**
```bash
ls -la .env  # File should exist
pipenv install django-environ  # Dependency should be installed
```

**Database connection errors?**
```bash
# Check your .env file has the right password
cat .env | grep DATABASE_URL
```

**Production deployment?**
- Use platform secrets (GitHub Actions secrets, Heroku config vars, etc.)
- Set `DEBUG=False` and generate unique SECRET_KEY for each environment

## Questions?
Check the updated documentation:
- `README.md` - Updated setup instructions
- `docs/DEVELOPMENT_GUIDE.md` - Complete secrets management guide
- `docs/POSTGRES_SETUP.md` - Database setup with .env files
