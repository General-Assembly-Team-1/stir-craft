# Stir Craft – Internal Development Guide

Welcome to the main app folder for Stir Craft! This document outlines the steps and best practices for developing our cocktail and mocktail app.

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
4. **Apply migrations**:
   ```bash
   python manage.py migrate
   ```
5. **Run the development server**:
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

## Additional Notes

- Refer to the main project README for deployment and environment details.
- Keep this document updated as the project evolves.