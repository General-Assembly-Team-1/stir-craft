"""
Admin registration for the stir_craft app.

This file registers the app's models with the Django admin site and provides
lightweight ModelAdmin customizations to improve usability for content editors
and developers. It also defines an inline for `RecipeComponent` so cocktail
ingredients can be edited on the Cocktail admin page.

Keep this file small and clear — heavy admin customizations belong in a
separate admin package/module if they grow.
"""

from django.contrib import admin
from . import models

# Inline for RecipeComponent so ingredients can be edited alongside a Cocktail
class RecipeComponentInline(admin.TabularInline):
	model = models.RecipeComponent
	extra = 0
	fields = ("order", "ingredient", "amount", "unit", "preparation_note")
	autocomplete_fields = ("ingredient",)
	ordering = ("order",)


@admin.register(models.Cocktail)
class CocktailAdmin(admin.ModelAdmin):
	"""Admin for Cocktail model.

	- Shows common fields in list view
	- Supports searching by name and creator
	- Uses an inline to manage RecipeComponent entries
	"""
	list_display = ("name", "creator", "is_alcoholic", "created_at")
	search_fields = ("name", "creator__username")
	list_filter = ("is_alcoholic", "color")
	inlines = (RecipeComponentInline,)
	autocomplete_fields = ("vessel",)


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
	"""Admin for Ingredient model.

	- Displays ingredient metadata and allows quick search/filtering
	- Exposes flavor tags via the form field provided by django-taggit
	"""
	list_display = ("name", "ingredient_type", "alcohol_content", "created_at")
	search_fields = ("name", "description")
	list_filter = ("ingredient_type",)


@admin.register(models.Vessel)
class VesselAdmin(admin.ModelAdmin):
	"""Admin for Vessel model.

	Simple display of vessel properties used in recipes and forms.
	"""
	list_display = ("name", "volume", "material", "stemmed")
	search_fields = ("name", "material")
	list_filter = ("stemmed",)


@admin.register(models.RecipeComponent)
class RecipeComponentAdmin(admin.ModelAdmin):
	"""Admin for RecipeComponent join model.

	Provides a standalone view for recipe components for power-users; typically
	edited inline on the Cocktail admin page instead of here.
	"""
	list_display = ("cocktail", "ingredient", "amount", "unit", "order")
	search_fields = ("ingredient__name", "cocktail__name")
	list_filter = ("unit",)


@admin.register(models.List)
class ListAdmin(admin.ModelAdmin):
	"""Admin for user-created Lists (Favorites, Your Creations, custom lists)."""
	list_display = ("name", "creator", "list_type", "is_editable", "is_deletable", "updated_at")
	search_fields = ("name", "creator__username")
	list_filter = ("list_type", "is_editable", "is_deletable")


@admin.register(models.Profile)
class ProfileAdmin(admin.ModelAdmin):
	"""Admin for Profile model which extends Django's User model."""
	list_display = ("user", "location", "birthdate", "updated_at")
	search_fields = ("user__username", "location")


# If models are added later, register them here following the same pattern.
