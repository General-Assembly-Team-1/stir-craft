#!/usr/bin/env python

import os
import sys
import django

# Add the Django project to the path
sys.path.append('/home/macfarley/code/ga/projects/stir-craft/stircraft')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
django.setup()

from stir_craft.models import Cocktail, RecipeComponent, Ingredient, Vessel
from stir_craft.forms.cocktail_forms import RecipeComponentFormSet
from django.contrib.auth.models import User

# Create test data
user = User.objects.create_user('test', 'test@example.com', 'pass')
vessel = Vessel.objects.create(name='Test Glass', material='glass')
ingredient = Ingredient.objects.create(name='Test Ingredient', category='mixer')

cocktail = Cocktail.objects.create(
    name='Test Cocktail',
    creator=user,
    vessel=vessel
)

component = RecipeComponent.objects.create(
    cocktail=cocktail,
    ingredient=ingredient,
    amount=30.0,
    unit='ml'
)

# Create the formset like the view does
formset = RecipeComponentFormSet(instance=cocktail)

print("=== FORMSET MANAGEMENT FORM DATA ===")
print(f"TOTAL_FORMS: {formset.management_form['TOTAL_FORMS'].value()}")
print(f"INITIAL_FORMS: {formset.management_form['INITIAL_FORMS'].value()}")
print(f"MIN_NUM_FORMS: {formset.management_form['MIN_NUM_FORMS'].value()}")
print(f"MAX_NUM_FORMS: {formset.management_form['MAX_NUM_FORMS'].value()}")

print("\n=== FIRST FORM INITIAL DATA ===")
if formset.forms:
    form = formset.forms[0]
    print(f"Form ID: {form.initial.get('id')}")
    print(f"Ingredient: {form.initial.get('ingredient')}")
    print(f"Amount: {form.initial.get('amount')}")
    print(f"Unit: {form.initial.get('unit')}")
    print(f"Order: {form.initial.get('order')}")

print("\n=== WHAT POST DATA SHOULD LOOK LIKE ===")
print("components-TOTAL_FORMS:", formset.management_form['TOTAL_FORMS'].value())
print("components-INITIAL_FORMS:", formset.management_form['INITIAL_FORMS'].value())
print("components-MIN_NUM_FORMS:", formset.management_form['MIN_NUM_FORMS'].value())
print("components-MAX_NUM_FORMS:", formset.management_form['MAX_NUM_FORMS'].value())
print("components-0-id:", component.id)
print("components-0-ingredient:", ingredient.id)
print("components-0-amount: 45")
print("components-0-unit: ml")
print("components-0-order: 1")
