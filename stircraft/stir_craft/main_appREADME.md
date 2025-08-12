# Stir Craft – Internal Development Guide

Welcome to the main app## Development Guidelines

- Add new models, views, and templates inside `stir_craft/`.
- Use Django's app structure for scalability.
- Static files (images, CSS, JS) go in `stir_craft/static/`.
- Write tests in `stir_craft/tests.py`.
- Run tests before pushing:
  ```bash
  python manage.py test
  ```

## Data Management

### Using the Cocktail Import Command
The `seed_from_thecocktaildb` management command provides flexible options for importing cocktail data:

```bash
# Import a small test batch for development
python manage.py seed_from_thecocktaildb --limit 10

# Import from specific letters (useful for testing)
python manage.py seed_from_thecocktaildb --letters abc --limit 20

# Import a larger dataset for staging
python manage.py seed_from_thecocktaildb --limit 100

# Clear existing data and start fresh
python manage.py seed_from_thecocktaildb --clear --limit 25
```

### What the Import Does
- Fetches cocktail data from TheCocktailDB API
- Creates `Cocktail`, `Ingredient`, `Vessel`, and `RecipeComponent` records
- Intelligently categorizes ingredients (spirits, liqueurs, mixers, etc.)
- Parses measurements from text to structured data
- Adds flavor tags for filtering and search
- Provides comprehensive progress reporting

### Command Options
- `--limit N`: Import maximum N cocktails
- `--letters abc`: Only search letters a, b, c (useful for testing)
- `--clear`: Clear existing cocktail data before importing
- Default behavior: Import ALL available cocktails (500+)r Stir Craft! This document outlines the steps and best practices for developing our cocktail and mocktail app.

## 🚀 Recent Updates

### API Integration & Database Seeding
- **TheCocktailDB API Integration**: Added comprehensive data seeding from a reliable cocktail API
- **PostgreSQL Configuration**: Database configured with proper authentication and optimization
- **Management Commands**: Custom Django commands for data import and maintenance
- **Intelligent Data Processing**: Automated categorization and parsing of cocktail data

### Management Commands
- `seed_from_thecocktaildb`: Import cocktail data with intelligent processing
- Comprehensive error handling and progress reporting
- Flexible options for testing and production use

## Project Structure

- All main app code should be placed in the `stir_craft/` directory (this folder).
- Avoid placing new code in higher-level directories unless absolutely necessary.

## Workflow & Branching

- **Always commit changes to your personal branch** (the one with your name on it). Do **not** commit directly to `main`.
- Open a pull request when your feature or fix is ready for review and merging.

## Current Focus: Wireframes

- We are currently working on wireframes to visualize the project pages.
- Wireframes and design assets are in `static/images/wireframes/`.
- Once wireframes are complete, we will move on to building out the models.

## Setup

1. **Clone the repository** and create/switch to your personal branch.
2. **Install dependencies**:
   ```bash
   pipenv install
   ```
3. **Activate the virtual environment**:
   ```bash
   pipenv shell
   ```
4. **Ensure PostgreSQL is running** and database is configured (see main README.md).
5. **Navigate to the Django project**:
   ```bash
   cd stircraft
   ```
6. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
7. **Seed the database with cocktail data**:
   ```bash
   python manage.py seed_from_thecocktaildb --limit 10
   ```
8. **Create a superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```
9. **Run the development server**:
   ```bash
   python manage.py runserver
   ```

## Development Guidelines

- Add new models, views, and templates inside `stir_craft/`.
- Use Django’s app structure for scalability.
- Static files (images, CSS, JS) go in `stir_craft/static/`.
- Write tests in `stir_craft/tests.py`.
- Run tests before pushing:
  ```bash
  python manage.py test
  ```

## Testing Framework

We have implemented a comprehensive testing scaffold to ensure the reliability of our models and features. Follow these steps to use the testing framework after creating a new feature:

1. **Write Tests for Your Feature:**
   - Add test methods to the appropriate test class in `stir_craft/tests.py`.
   - Use assertions to validate expected behavior (e.g., `assertEqual`, `assertTrue`).
   - If your feature involves multiple models, write integration tests to verify their interactions.

2. **Run Tests Locally:**
   ```bash
   python manage.py test stir_craft
   ```
   - Use `--verbosity=2` for detailed output.
   - Target specific test classes or methods if needed.

3. **Fix Any Failures:**
   - Debug and resolve issues until all tests pass.

4. **Push Your Changes:**
   - Ensure your branch is up to date with `main`.
   - Commit and push your changes to the Feature Branch, including the updated tests.
   - Include your tests in the pull request to Testing Branch.

By maintaining high test coverage, we can ensure the stability and scalability of the Stir Craft app.

## Code Review & Merging

- Open a pull request for review.
- Ensure all tests pass and code follows team conventions.
- Only merge after approval.

## Keeping Your Local Repo Up to Date

To make sure your local repository stays current with the latest changes from the remote (cloud) repository:

1. **Fetch and merge the latest changes from main:**
   ```bash
   git checkout main
   git pull origin main
   ```
2. **Switch back to your personal branch and rebase (or merge) main into it:**
   ```bash
   git checkout <your-branch-name>
   git rebase main
   # or, if you prefer merging:
   git merge main
   ```
3. **Resolve any conflicts, test your code, and continue working.**

Keeping your branch up to date helps avoid merge conflicts and ensures you’re working with the latest code.

## Branch Update Utility

To ensure your local repository stays up to date and avoid merge conflicts, use the `update_branches_team.sh` script before committing changes:

1. **Run the script:**
   ```bash
   ./update_branches_team.sh
   ```
   - This script will fetch the latest changes from the remote repository and update all local branches.
   - Replace `/path/to/your/local/stir-craft` in the script with your local repository path if needed.

2. **Verify updates:**
   - Ensure your branch is up to date with `main`.
   - Resolve any conflicts if they arise.

3. **Switch back to your feature branch:**
   - The script ends with your repository on the `main` branch.
   - Use the following command to return to your feature branch:
     ```bash
     git checkout <your-branch-name>
     ```

By running this utility regularly, you can maintain consistency across team workflows and minimize conflicts during development.

## Additional Notes

- Refer to the main project README for deployment and environment details.
- Keep this document updated as the project evolves.