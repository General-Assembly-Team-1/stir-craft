"""
Test-specific Django settings for StirCraft.

This file ensures tests run reliably regardless of local database setup.
Inherits from main settings but overrides database to use SQLite in memory.
"""

from .settings import *

# Override database to use SQLite in memory for tests
# This eliminates PostgreSQL dependency issues during testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster test runs
# This makes tests run much faster by not applying all migrations
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Speed up password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests to reduce noise
LOGGING_CONFIG = None
import logging
logging.disable(logging.CRITICAL)

# Test-specific settings
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# Cache configuration for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Ensure test database creation works
SECRET_KEY = 'test-secret-key-for-tests-only'
DEBUG = True

# Allow all hosts for testing
ALLOWED_HOSTS = ['*']
