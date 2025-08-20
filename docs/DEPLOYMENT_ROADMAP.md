# StirCraft — Deployment Roadmap (Heroku-focused)

This roadmap is focused on finishing the Cocktail CRUD surface (highest priority) and then preparing the app for deployment to Heroku. Each entry is formatted so you can copy/paste it into GitHub issues or a project board.

---

## Quick plan

- Finish Cocktail CRUD (update/delete + templates + tests)
- Implement minimal auth (sign-up/sign-in) so creator permissions work
- Implement Lists & Ingredients views used by the UX
- Prepare Heroku infra (requirements, Procfile, staticfiles, production settings)
- Add CI (tests on PRs) and optional Heroku deploy workflow

---

## Milestones

1. Cocktail CRUD (MVP)
2. Auth & Permissions
3. Lists & Ingredient management
4. Heroku Deployment & Infra
5. CI / CD & QA
6. Polish: media, accessibility, monitoring

---

## Milestone 1 — Cocktail CRUD (Top priority)

Copy each block below into a new GitHub issue. Set labels and estimates as suggested.

### Issue: Cocktail — Update view (cocktail_update)
- Summary: Implement an edit flow for cocktails using the existing `CocktailForm` and `RecipeComponentFormSet`.
- Acceptance criteria:
  - GET displays pre-populated `CocktailForm` and inline `RecipeComponentFormSet`.
  - POST atomically updates cocktail fields and components (create/update/delete rows).
  - Only the cocktail creator can access the view (permission enforced).
  - Unit tests: happy path, invalid form, permission denied.
- Labels: `feature`, `backend`, `high`
- Estimate: 4–6h
- Dependencies: `stir_craft/forms/cocktail_forms.py`, reuse `cocktail_create.html` templates.

### Issue: Cocktail — Delete view (cocktail_delete)
- Summary: Implement deletion with a confirmation and proper permission checks.
- Acceptance criteria:
  - Confirmation page or modal before deletion.
  - Only the creator can delete; others receive 403 or redirect.
  - Redirect to `cocktail_index` with success message and test verifying cascade behavior.
- Labels: `feature`, `backend`, `medium`
- Estimate: 1–2h

### Issue: Cocktail — Reuse create template for update
- Summary: Make `cocktail_create.html` support update mode (title/button change).
- Acceptance criteria:
  - Page shows "Create" vs "Save changes" appropriately.
  - Works with update view and preserves formset behaviour.
- Labels: `frontend`, `medium`
- Estimate: 1–2h

### Issue: Cocktail — Detail page edit/delete affordances
- Summary: Show Edit/Delete buttons on `cocktail_detail.html` only for creator.
- Acceptance criteria: Buttons appear only to creator and link to update/delete views.
- Labels: `frontend`, `low`
- Estimate: 30–60m

### Issue: Cocktail — Validation & edge cases
- Summary: Add tests and guard rails for min/max components, missing ingredient rows, and measurement parsing under update.
- Acceptance criteria: Tests for min (1) and max (15) ingredients and behavior on invalid components.
- Labels: `tests`, `backend`, `medium`
- Estimate: 2–4h

---

## Milestone 2 — Auth & Permissions

### Issue: Auth — Sign-up (registration)
- Summary: Implement user registration (create `User` + `Profile`) and auto-login.
- Acceptance criteria: New users can register, are logged in automatically, and redirected to dashboard. Tests for duplicate username/email.
- Labels: `feature`, `backend`, `high`
- Estimate: 3–4h

### Issue: Auth — Sign-in (login)
- Summary: Implement login view or wire Django auth views to `registration/login.html` template.
- Acceptance criteria: Login works and redirects to requested page or dashboard. Tests for invalid credentials.
- Labels: `feature`, `backend`, `medium`

### Issue: Auth — Password reset
- Summary: Wire Django's password-reset views with console backend in dev.
- Acceptance criteria: Password reset emails are created (console) and allow password change locally.
- Labels: `feature`, `low`

---

## Milestone 3 — Lists & Ingredients

### Issue: Lists — Add to list endpoint
- Summary: Add a view to add/remove cocktails to user lists; return JSON for AJAX.
- Acceptance criteria: Works for AJAX and standard POST. Tests for permissions.
- Labels: `feature`, `backend`, `medium`

### Issue: Lists — Create & detail views
- Summary: Create list creation and list detail pages (templates exist).
- Acceptance criteria: Users can create lists and see cocktails inside lists.
- Labels: `feature`, `medium`

### Issue: Ingredients — Index & detail views
- Summary: Implement ingredient index and detail pages using existing templates.
- Acceptance criteria: Pagination and search by name; detail shows recipes that use the ingredient.
- Labels: `feature`, `medium`

---

## Milestone 4 — Heroku Deployment & Infra

These are the minimum infra files and code changes needed to deploy to Heroku.

### Issue: Infra — `requirements.txt` (from Pipfile.lock)
- Summary: Generate `requirements.txt` for Heroku using `pipenv lock -r` and commit it.
- Acceptance criteria: `pip install -r requirements.txt` works in a fresh venv.
- Labels: `infra`, `high`
- Estimate: 30–60m

### Issue: Infra — `Procfile` + `runtime.txt`
- Summary: Add `Procfile` (`web: gunicorn stircraft.wsgi --log-file -`) and `runtime.txt` (e.g. `python-3.11.4`).
- Acceptance criteria: Heroku recognizes Python runtime and runs gunicorn.
- Labels: `infra`, `high`
- Estimate: 15m

### Issue: Infra — Static files + whitenoise
- Summary: Add `STATIC_ROOT`, install and configure `whitenoise` in production settings, ensure `collectstatic` works.
- Acceptance criteria: `python manage.py collectstatic --noinput` succeeds; static served via whitenoise on Heroku.
- Labels: `infra`, `high`
- Estimate: 1–2h

### Issue: Infra — Production settings
- Summary: Add a production settings toggle or `settings_prod.py` enabling secure defaults (HSTS, SECURE_SSL_REDIRECT) and read env vars.
- Acceptance criteria: Site runs with `DEBUG=False` and fails fast on missing `SECRET_KEY` (already present). Document required envs.
- Labels: `infra`, `high`
- Estimate: 2–3h

### Issue: Infra — Heroku setup docs
- Summary: Document `heroku create`, setting `SECRET_KEY` and `DATABASE_URL`, `heroku addons:create heroku-postgresql`, migrations and `collectstatic` steps.
- Acceptance criteria: A dev can follow docs and deploy the app to a new Heroku app.
- Labels: `docs`, `infra`, `low`

---

## Milestone 5 — CI / CD & QA

### Issue: CI — GitHub Actions test workflow
- Summary: Add a workflow to run tests on PRs and pushes (use `.env.example` values or secrets for CI).
- Acceptance criteria: PRs must pass tests before merge.
- Labels: `ci`, `high`

### Issue: CI — Optional Heroku deployment workflow
- Summary: Workflow that runs tests, and on `main` merge deploys to Heroku using repo `HEROKU_API_KEY` secret.
- Acceptance criteria: Deploys only on successful tests and tagged merges.
- Labels: `ci`, `medium`

---

## Milestone 6 — Polish

- Media uploads (S3) — add `MEDIA_ROOT` dev & AWS S3 optional production storage
- Accessibility audit & fixes
- Monitoring (Sentry integration)

---

## PR checklist (copy into PR template)

- [ ] Tests added (unit/integration) for new behavior
- [ ] Lint/format passes (black/ruff)
- [ ] No secrets committed (`.env` absent)
- [ ] README/docs updated with any new envs
- [ ] Manual smoke test steps in PR description

---

## Quick commands

Generate `requirements.txt`:
```bash
pipenv lock -r > requirements.txt
```

Create `Procfile` and `runtime.txt` (example):
Procfile:
```
web: gunicorn stircraft.wsgi --log-file -
```
runtime.txt:
```
python-3.11.4
```

Collect static (Heroku slug build will also run this):
```bash
python manage.py collectstatic --noinput
```

Heroku quick deploy (after creating app and setting secrets):
```bash
heroku create my-stircraft
git push heroku Testing:main
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=<prod-secret>
heroku addons:create heroku-postgresql:hobby-dev
heroku run python manage.py migrate
heroku run python manage.py collectstatic --noinput
```

---

## Next steps I can do for you

- Scaffold the GitHub issues automatically (I can create markdown files for each ticket to paste into the board)
- Add `requirements.txt`, `Procfile`, and `runtime.txt` now and commit them
- Implement `cocktail_update` and `cocktail_delete` views + tests now

Pick one and I'll start it immediately.
