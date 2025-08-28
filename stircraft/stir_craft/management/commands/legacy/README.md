# Legacy Management Commands

These are the original individual management commands that have been
consolidated into the new organized structure. They are kept here
for reference and backup purposes.

## Legacy Commands:
- `check_cocktail_images.py` → Now: `data_maintenance/maintain_images.py`
- `clean_vibe_tags.py` → Now: `data_maintenance/maintain_tags.py`
- `cleanup_duplicate_ingredients.py` → Now: `data_maintenance/maintain_ingredients.py`
- `detect_cocktail_colors.py` → Now: `data_analysis/analyze_cocktails.py`
- `detect_cocktail_vibes.py` → Now: `data_analysis/analyze_cocktails.py`
- `fix_alcohol_content.py` → Now: `data_maintenance/maintain_ingredients.py`
- `fix_ingredients.py` → Now: `data_maintenance/maintain_ingredients.py`
- `normalize_colors.py` → Now: `data_maintenance/maintain_tags.py`
- `recategorize_ingredients.py` → Now: `data_maintenance/maintain_ingredients.py`
- `seed_from_thecocktaildb.py` → Now: `data_import/import_cocktaildb.py`
- `show_unit_examples.py` → Now: `data_analysis/analyze_cocktails.py`
- `standardize_units.py` → Now: `data_maintenance/maintain_units.py`

## New Master Command:
Use `python manage.py stircraft` for all operations with workflows and chaining.
