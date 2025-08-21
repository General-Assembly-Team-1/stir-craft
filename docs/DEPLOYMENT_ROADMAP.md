# StirCraft — Deployment Roadmap (Heroku-focused)

**Last Updated: August 21, 2025**

This roadmap tracks the progress toward deploying StirCraft to Heroku. Major backend functionality is now complete, with remaining work focused on templates, auth implementation, and deployment infrastructure.

---

## Current Status Summary

✅ **Completed:** Cocktail CRUD views, List management views, Forms, URL routing, Navigation, Basic templates  
🟡 **In Progress:** Missing templates for list management  
❌ **Blocked:** Auth views (commented out), Deployment infrastructure  

---

## Quick plan

- ✅ ~~Finish Cocktail CRUD (update/delete + templates + tests)~~ **COMPLETE**
- 🟡 Complete missing templates for list management views
- ❌ Implement minimal auth (sign-up/sign-in) so creator permissions work
- ❌ Implement Ingredients views used by the UX
- ❌ Prepare Heroku infra (requirements, Procfile, staticfiles, production settings)
- ❌ Add CI (tests on PRs) and optional Heroku deploy workflow

---

## Milestones

1. ✅ Cocktail CRUD (MVP) — **COMPLETE**
2. 🟡 Lists & Templates — **80% Complete (views done, templates missing)**
3. ❌ Auth & Permissions — **Templates exist, views commented out**
4. ❌ Ingredient Management — **Stubbed but not implemented**
5. ❌ Heroku Deployment & Infra — **Not started**
6. ❌ CI / CD & QA — **Basic tests exist**
7. ❌ Polish: media, accessibility, monitoring — **Future work**

---

## 🚨 CRITICAL BLOCKERS (Must fix before deployment)

### Issue: Missing Templates for List Views
- **Priority:** HIGH — Views will crash with TemplateDoesNotExist
- **Missing templates:**
  - `stir_craft/list_update.html`
  - `stir_craft/user_lists.html` 
  - `stir_craft/list_confirm_delete.html`
  - `stir_craft/quick_add_modal.html`
  - `stir_craft/list_feed.html`
  - `403.html` (error page)
- **Estimate:** 3-4 hours
- **Status:** Views implemented, forms created, just need templates

### Issue: Auth Views Activation
- **Priority:** HIGH — Users cannot sign up or log in
- **Problem:** Sign-up/sign-in views are commented out in `stir_craft/urls.py`
- **Templates exist:** `registration/login.html`, `registration/signup.html`
- **Estimate:** 2-3 hours to implement views and test
- **Status:** Need to uncomment and implement the auth view functions

---

## ✅ Milestone 1 — Cocktail CRUD (COMPLETE)

**Status: COMPLETE** — All cocktail CRUD operations implemented and working.

### Completed Features:
- ✅ **Cocktail Update View** — Implemented in `stir_craft/views.py:377`
- ✅ **Cocktail Delete View** — Implemented in `stir_craft/views.py:435`
- ✅ **Template Reuse** — Update view reuses `cocktail_create.html`
- ✅ **Permission Checks** — Creator-only edit/delete enforced
- ✅ **Forms & Validation** — `CocktailForm` and `RecipeComponentFormSet` working
- ✅ **URL Routing** — All cocktail routes registered and named

### Remaining Work:
- 🟡 **Verify edit/delete buttons** appear on cocktail detail page for creators
- 🟡 **Add comprehensive tests** for edge cases and validation

---

## 🟡 Milestone 2 — Lists & Templates (80% Complete)

**Status: Backend complete, frontend templates missing**

### Completed Features:
- ✅ **All List Views** — CRUD operations implemented (`list_detail`, `list_create`, `list_update`, `list_delete`)
- ✅ **AJAX Endpoints** — Add/remove from lists, toggle favorites with JSON responses
- ✅ **List Forms** — Complete form suite in `stir_craft/forms/list_forms.py`
- ✅ **URL Routing** — All list routes registered
- ✅ **User Lists Management** — View user's lists, create/manage lists
- ✅ **List Feed** — Browse public lists

### Missing Templates (BLOCKERS):
- ❌ `stir_craft/list_update.html`
- ❌ `stir_craft/user_lists.html`
- ❌ `stir_craft/list_confirm_delete.html`
- ❌ `stir_craft/quick_add_modal.html`
- ❌ `stir_craft/list_feed.html`

### Working Templates:
- ✅ `stir_craft/list_detail.html` — Exists
- ✅ `stir_craft/list_form.html` — Exists

---

## ❌ Milestone 3 — Auth & Permissions (Templates exist, views missing)

**Status: Blocked** — Templates exist but auth views are commented out

### Issue: Auth — Sign-up & Sign-in Views
- **Problem:** Views are commented out in `stir_craft/urls.py` lines 10-11
- **Templates:** Already exist at `registration/login.html`, `registration/signup.html`
- **Required:** Implement `sign_up` and `sign_in` views in `stir_craft/views.py`
- **Acceptance criteria:** New users can register, are logged in automatically, and redirected to dashboard
- **Estimate:** 3-4h

### Issue: Auth — Password reset (Low priority)
- **Status:** Not implemented
- **Estimate:** 2-3h

---

## ❌ Milestone 4 — Ingredient Management (Stubbed)

**Status: Not implemented** — Views exist but are commented out

### Issue: Ingredients — Index & detail views
- **Problem:** Views are commented out in `stir_craft/views.py` lines 98, 106, 114
- **Templates:** `ingredient_index.html`, `ingredient_detail.html` exist
- **Required:** Implement ingredient views and URL routing
- **Estimate:** 4-5h

---

## ❌ Milestone 5 — Heroku Deployment & Infra (Not started)

**Status: Critical for deployment** — No deployment files exist

### Missing Files (HIGH PRIORITY):
- ❌ `requirements.txt` — Generate from Pipfile.lock
- ❌ `Procfile` — Add gunicorn web process
- ❌ `runtime.txt` — Specify Python version
- ❌ Static files config — Add STATIC_ROOT, install whitenoise
- ❌ Production settings — Environment-based config

### Infrastructure Tasks:
1. **Generate requirements.txt** (15min): `pipenv lock -r > requirements.txt`
2. **Create Procfile** (5min): `web: gunicorn stircraft.wsgi --log-file -`
3. **Add runtime.txt** (5min): `python-3.11.4`
4. **Configure static files** (1-2h): Install whitenoise, set STATIC_ROOT
5. **Production settings** (2-3h): Environment variables, security settings

**Total Estimate:** 4-5 hours

---

## ⏰ UPDATED TIME ESTIMATES

### To Minimum Viable Deployment: **12-16 hours**

1. **Critical Templates** (3-4 hours) — Create 6 missing templates
2. **Auth Implementation** (3-4 hours) — Uncomment and implement auth views  
3. **Deployment Infrastructure** (4-6 hours) — Requirements, Procfile, static files, production settings
4. **Testing & QA** (2-3 hours) — Smoke testing, fix critical bugs

### To Full Feature Complete: **Additional 8-12 hours**
- Ingredient views (4-5 hours)
- Comprehensive test suite (4-6 hours)  
- CI/CD pipeline (2-3 hours)

---

## 🎯 RECOMMENDED NEXT STEPS

**Phase 1 (Immediate - 1-2 days):**
1. Create missing list templates
2. Uncomment and implement auth views
3. Add infrastructure files (requirements.txt, Procfile, etc.)

**Phase 2 (Deployment ready - 3-5 days):**
4. Configure production settings
5. Test deployment to Heroku
6. Smoke test all critical flows

**Phase 3 (Polish - 1-2 weeks):**
7. Implement ingredient views
8. Add comprehensive tests
9. Set up CI/CD

---

## 📊 PROGRESS TRACKING

**Overall Progress: ~65% Complete**

- ✅ **Backend Logic:** 90% (views, forms, models, URL routing)
- 🟡 **Frontend Templates:** 70% (core templates done, list management missing)
- ❌ **Authentication:** 30% (templates exist, views need implementation)
- ❌ **Deployment Infrastructure:** 0% (not started)
- 🟡 **Testing:** 40% (basic tests exist, need comprehensive coverage)

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
