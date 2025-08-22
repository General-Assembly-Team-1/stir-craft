# 🚀 StirCraft Developer Guide - START HERE

**Welcome to StirCraft!** This is your entry point to the project. Read this first, then follow the guided path below.

## 📋 Quick Start Checklist

**New to the project? Follow this order:**

### 1. **SETUP** (Required for everyone)
- [ ] Read `QUICK_SETUP.md` - Get the project running locally
- [ ] Read `POSTGRES_SETUP.md` - Database setup (essential for testing)

### 2. **TESTING** (Verify everything works)
- [ ] Run `pipenv run python stircraft/manage.py test stir_craft.tests` to verify everything works
- [ ] Check `TEST_FAILURE_REPORT.md` for current test status (✅ ALL 86 TESTS PASSING)
- [ ] All tests are now passing - no issues to fix!

### 3. **CURRENT STATUS** (August 22, 2025) ✅ **PRODUCTION READY**
- [ ] ✅ **Backend 100% complete** - All views, models, forms implemented
- [ ] ✅ **Frontend 100% complete** - All templates and partials implemented
- [ ] ✅ **Authentication System** - Complete login/logout/signup functionality  
- [ ] ✅ **Deployment Infrastructure** - requirements.txt, Procfile, runtime.txt created
- [ ] ✅ **Test Suite** - ALL 86 tests passing (100% success rate)
- [ ] ✅ **Production Settings** - Static files and security configuration complete
- [ ] 🚀 **Ready for Heroku deployment**

### 3. **DEVELOPMENT** (When you're ready to contribute)
- [ ] Read `DEVELOPMENT_GUIDE.md` - Coding standards and workflow
- [ ] Check `PROJECT_CHANGELOG.md` - Recent changes and context
- [ ] Review `DEPLOYMENT_ROADMAP.md` - Ready for immediate deployment!

### 4. **ADVANCED** (For specific features)
- [ ] `COCKTAIL_FORMS_TECHNICAL_GUIDE.md` - Form system details
- [ ] `TEMPLATE_PARTIALS_GUIDE.md` - Template organization
- [ ] `CSS_ORGANIZATION.md` - Styling system

## 🎯 What You Need to Know

### If you're here to...

**🔧 Fix a bug** → Read setup docs, run tests, then `DEVELOPMENT_GUIDE.md`

**✨ Add a feature** → All of the above + the relevant technical guides

**🧪 Run tests** → `POSTGRES_SETUP.md` + use `../scripts/run_tests.sh`

**📝 Update documentation** → `DEVELOPMENT_GUIDE.md` for standards

**🎨 Work on UI/CSS** → Setup + `CSS_ORGANIZATION.md` + `TEMPLATE_PARTIALS_GUIDE.md`

## � Documentation Structure

```
docs/
├── README.md ← START HERE (this file)
├── QUICK_SETUP.md ← Step 1: Get project running
├── POSTGRES_SETUP.md ← Step 2: Database setup
├── DEVELOPMENT_GUIDE.md ← Step 3: Development workflow
├── TEST_FAILURE_REPORT.md ← Current test status
├── PROJECT_CHANGELOG.md ← What's changed recently
└── Technical Guides/
    ├── COCKTAIL_FORMS_TECHNICAL_GUIDE.md
    ├── TEMPLATE_PARTIALS_GUIDE.md
    ├── CSS_ORGANIZATION.md
    ├── NAMING_CONVENTION_UPDATES.md
    └── TESTING_INFRASTRUCTURE.md

scripts/
├── run_tests.sh ← Easy test running
├── update_test_report.py ← Auto test reporting
├── update_branches.sh ← Git branch management
└── update_branches_team.sh ← Team branch sync
```

## ⚡ Quick Commands

**Project Status (August 21, 2025):**
```bash
# Check current test status (2 failing due to missing templates)
./scripts/run_tests.sh

# See what's ready for deployment
cat docs/DEPLOYMENT_ROADMAP.md
```

**First time setup:**
```bash
# 1. Set up the project
./scripts/run_tests.sh  # This will guide you through any missing setup

# 2. If tests fail with DB errors, run:
sudo -u postgres psql -c "ALTER USER $(whoami) PASSWORD 'stircraft123';"
export DB_PASSWORD=stircraft123
```

**Daily development:**
```bash
# Before coding
./scripts/update_branches_team.sh  # Sync with team changes
./scripts/run_tests.sh             # Verify everything works

# After coding
./scripts/run_tests.sh             # Test your changes
git add . && git commit -m "..."   # Commit if tests pass
```

## 🆘 Getting Help

### Common Issues

**"Tests won't run"** → Check `POSTGRES_SETUP.md`

**"Don't know where to start"** → Follow the checklist above in order

**"Complex form/template issue"** → See the technical guides

**"Git/branch confusion"** → See branch management in `DEVELOPMENT_GUIDE.md`

### Documentation Priority

**MUST READ:** README.md (this), QUICK_SETUP.md, POSTGRES_SETUP.md

**SHOULD READ:** DEVELOPMENT_GUIDE.md, TEST_FAILURE_REPORT.md

**AS NEEDED:** Technical guides for specific features you're working on

---

## 🎉 Ready to Start?

1. **First:** `QUICK_SETUP.md`
2. **Then:** `POSTGRES_SETUP.md` 
3. **Test:** `../scripts/run_tests.sh`
4. **Code:** `DEVELOPMENT_GUIDE.md`

**Questions?** Check the specific guide for your task, or ask the team!
