# StirCraft Utility Scripts

This directory contains utility scripts for various maintenance and debugging tasks.

## Directory Structure

### `/image_management/`
Scripts for managing cocktail images and database assignments:

- **`assign_images.py`** - Assigns existing image files to cocktails that don't have images
- **`import_missing_cocktails.py`** - Imports cocktails from TheCocktailDB API for existing image files
- **`fix_cocktail_images.py`** - General image fixing and assignment script

### `/debugging/`
Scripts for debugging and analysis:

- **`check_broken_images.py`** - Checks for broken image links in the database
- **`debug_users.py`** - Debug user and profile issues

## Usage

All scripts are designed to work with Django's environment. They can be run directly from the project root:

```bash
# From the stircraft/ directory
python scripts/image_management/assign_images.py
python scripts/debugging/check_broken_images.py
```

Or deployed to Heroku:

```bash
# Copy script to root and run
heroku run "cd stircraft && python assign_images.py" --app stircraft-app
```

## Important Notes

- These scripts are utilities and should be used with caution in production
- Always test scripts in development before running in production
- Some scripts modify database records - consider making backups
- Image management scripts specifically handle the cocktail image assignment process

## Recent Usage

These scripts were used to resolve image display issues by:
1. Identifying missing cocktails for existing image files
2. Importing missing cocktails from TheCocktailDB API
3. Assigning images to newly imported cocktails
4. Cleaning up broken image assignments

The process successfully restored database integrity and resolved dual image display issues.
