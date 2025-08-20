# Test Failure Report — stir_craft (run on 2025-08-20)

This document captures the results of the most recent test run and recommended next steps.

## Quick summary
- Command: `pipenv run python stircraft/manage.py test stir_craft` (with `DB_PASSWORD=stircraft123`)
- Tests executed: 57
- Failures: 9
- Errors: 7

## Blocking errors (fix these first)
1. TemplateSyntaxError: Invalid filter `mul`
   - Probable cause: templates call a custom filter named `mul` but the tag library is not loaded or missing.
   - Impact: view/template rendering fails across multiple pages.

2. TemplateDoesNotExist: `stir_craft/home.html`, `stir_craft/profile_detail.html`, `stir_craft/profile_update.html`
   - Probable cause: expected templates are missing from `templates/stir_craft/` or Django's template dirs are misconfigured for tests.
   - Impact: views that render these templates error out and tests fail.

3. IntegrityError: duplicate key violates unique constraint on `stir_craft_list(name, creator_id)`
   - Probable cause: `List.create_default_lists` (or a user-created signal) creates duplicate lists — not idempotent. Use `get_or_create()` or guard against duplicates.
   - Impact: test run aborts during DB operations.

## Functional failures (fix after blockers)
1. Redirects to `/admin/login/` instead of `/accounts/login/` (test expects `/accounts/login/`).
   - Probable cause: `LOGIN_URL` or auth URL configuration differs from test expectation.

2. `cocktail_create` page assertions: tests look for `'cocktail_form'` token but template markup changed (now uses `id="cocktail-form"`).
   - Probable cause: minor template changes; either update tests or reintroduce expected markers.

3. `RecipeComponentForm` accepts negative `amount` values though tests expect rejection.
   - Probable cause: missing `clean_amount()` or validators enforcing positive amounts.

4. Query-count / performance tests exceed expected queries (example: 16 vs expected 6).
   - Probable cause: missing `select_related` / `prefetch_related` for components, ingredient, and taggit tags; tag accesses are firing per-cocktail.

5. Profile form/field mismatches (e.g., `confirmation` vs `username_confirmation`, location max_length mismatch).
   - Probable cause: form fields renamed or model field constraints tightened; tests need updating or forms reverted.

## Prioritized action plan (recommended order)
1. Fix `mul` template filter error (high priority). Search templates for `|mul` usage. Either restore/load the custom filter library or replace the usage with server-side calculation.
2. Add or restore missing templates under `templates/stir_craft/` or adjust template paths in settings so tests can find them.
3. Make `List.create_default_lists` idempotent (use `get_or_create()` or swallow IntegrityError when appropriate). Also check signals that may double-create lists.
4. Add form validation for `RecipeComponent.amount` to enforce positive values (validator or `clean_` method).
5. Fix `LOGIN_URL` mismatch or update tests to accept current auth redirect.
6. Add `select_related` / `prefetch_related` (and taggit-friendly prefetch) in the cocktail list/detail views to reduce DB queries and re-run the performance tests.
7. Align tests with any intentional form/field renames (or revert the renames) — update tests for `username_confirmation` and adjust test inputs that exceed field constraints.

## Quick re-run commands (from repo root, zsh)
```bash
export DB_PASSWORD="stircraft123"
pipenv run python stircraft/manage.py test stir_craft.tests.test_profile_views.GeneralViewTest.test_home_view -v 2
pipenv run python stircraft/manage.py test stir_craft.tests.test_integration.CocktailPerformanceTest.test_cocktail_index_query_efficiency -v 2
pipenv run python stircraft/manage.py test stir_craft -v 2
```

## Estimated effort (rough)
- Template filter fix: 15–30 minutes
- Restore/add missing templates: 5–20 minutes
- Idempotent List creation: 10–20 minutes
- Form validation: 5–15 minutes
- Prefetch/query tuning: 20–60 minutes
- Test alignment updates: 5–15 minutes

## Notes
- Fixing the template filter and missing templates will unblock the largest number of errors. After that, address DB idempotency and form validations, then performance tuning.
- I can implement the fixes in the order above and re-run targeted tests after each change; tell me which item to start with.
