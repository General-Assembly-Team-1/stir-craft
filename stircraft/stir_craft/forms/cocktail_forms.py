"""
StirCraft Cocktail Forms Module

This module contains all form classes related to cocktail creation, management, and search functionality.
It implements Django's inline formset pattern to handle complex cocktail recipes with multiple ingredients.

Key Features:
- Dynamic ingredient management with inline formsets
- Comprehensive form validation and error handling
- Bootstrap-styled form widgets for professional UI
- Integration with existing models (Cocktail, Ingredient, Vessel, RecipeComponent)
- Advanced search and filtering capabilities

Author: StirCraft Development Team
Date: August 2025
Version: 1.0

Usage Examples:
    # Creating a cocktail with ingredients
    cocktail_form = CocktailForm(user=request.user)
    formset = RecipeComponentFormSet()
    
    # Searching cocktails
    search_form = CocktailSearchForm(request.GET)
    
    # Quick ingredient creation
    ingredient_form = QuickIngredientForm()
"""

from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User
from ..models import Cocktail, Ingredient, Vessel, RecipeComponent


class CocktailForm(forms.ModelForm):
    """
    Main form for creating/updating cocktail recipes.
    Handles basic cocktail information like name, description, instructions, etc.
    
    This form is designed to work in conjunction with RecipeComponentFormSet
    to create complete cocktail recipes with multiple ingredients.
    
    Features:
    - Bootstrap-styled form widgets for professional appearance
    - Dynamic help text based on current user
    - Optional fields for flexible recipe creation
    - Integration with vessel selection and tagging system
    
    Args:
        user (User, optional): Current user for personalized help text
        
    Example:
        form = CocktailForm(user=request.user)
        if form.is_valid():
            cocktail = form.save(commit=False)
            cocktail.creator = request.user
            cocktail.save()
    """
    
    class Meta:
        model = Cocktail
        fields = [
            'name', 'description', 'instructions', 'vessel', 
            'is_alcoholic', 'color', 'vibe_tags'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter cocktail name (e.g., "Classic Margarita")'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Brief description of your cocktail...'
            }),
            'instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Step-by-step preparation instructions...'
            }),
            'vessel': forms.Select(attrs={
                'class': 'form-select',
                'empty_label': 'Select glassware...'
            }),
            'is_alcoholic': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Red, Yellow, Clear'
            }),
            'vibe_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter tags separated by commas (e.g., tropical, cozy, party)'
            }),
        }
        help_texts = {
            'vessel': 'Choose the appropriate glassware for serving',
            'is_alcoholic': 'Uncheck for mocktails and non-alcoholic drinks',
            'vibe_tags': 'Add mood/occasion tags to help others find your cocktail',
        }

    def __init__(self, *args, **kwargs):
        # Remove 'user' from kwargs if it exists (we'll set creator in the view)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filter vessels to only show active ones (if you add an 'active' field later)
        self.fields['vessel'].queryset = Vessel.objects.all().order_by('name')
        
        # Make description optional but encourage it
        self.fields['description'].required = False
        
        # Set dynamic help text
        if self.user:
            self.fields['name'].help_text = f"This will be saved as '{self.user.username}'s [Your Cocktail Name]'"


class RecipeComponentForm(forms.ModelForm):
    """
    Form for individual recipe components (ingredient + amount + unit).
    Used within the RecipeComponentFormSet for handling multiple ingredients.
    
    This form represents a single ingredient in a cocktail recipe, including
    its measurement, unit, preparation notes, and order of addition.
    
    Features:
    - Ingredient selection with grouped/sorted options
    - Precise measurement input with step validation
    - Optional preparation notes for special instructions
    - Order field for proper ingredient sequence
    - Bootstrap styling for consistent UI
    
    Validation:
    - Ensures positive amounts for ingredients
    - Validates unit selection from predefined choices
    - Optional preparation notes for flexibility
    
    Example:
        # Usually used within a formset, not directly
        formset = RecipeComponentFormSet(instance=cocktail)
        for form in formset:
            if form.is_valid():
                component = form.save(commit=False)
                component.cocktail = cocktail
                component.save()
    """
    
    class Meta:
        model = RecipeComponent
        fields = ['ingredient', 'amount', 'unit', 'preparation_note', 'order']
        widgets = {
            'ingredient': forms.Select(attrs={
                'class': 'form-select ingredient-select',
                'data-placeholder': 'Choose ingredient...'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.25',  # Allow quarter measurements
                'min': '0',
                'placeholder': '1.5'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select'
            }),
            'preparation_note': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: muddled, expressed, etc.'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'min': '0',
                'step': '1'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Order ingredients alphabetically and group by type for better UX
        ingredients = Ingredient.objects.select_related().order_by('ingredient_type', 'name')
        self.fields['ingredient'].queryset = ingredients
        
        # Make preparation_note optional
        self.fields['preparation_note'].required = False
        
        # Set reasonable defaults for order field
        self.fields['order'].help_text = "Order of addition (0 = first, 1 = second, etc.)"


# Create the formset for handling multiple recipe components
# This is the key to managing multiple ingredients in a single form submission
RecipeComponentFormSet = inlineformset_factory(
    parent_model=Cocktail,           # The main model (cocktail)
    model=RecipeComponent,           # The related model (ingredient + measurements)
    form=RecipeComponentForm,        # The form class for each ingredient
    fields=['ingredient', 'amount', 'unit', 'preparation_note', 'order'],
    extra=3,                        # Show 3 empty ingredient forms initially
    min_num=1,                      # Require at least 1 ingredient (cocktails need ingredients!)
    max_num=15,                     # Limit to reasonable number of ingredients
    can_delete=True,                # Allow removing ingredients
    validate_min=True,              # Validate minimum number
    validate_max=True,              # Validate maximum number
)

"""
RecipeComponentFormSet Usage Notes:

This formset is the core of the cocktail creation system. It allows users to:
1. Add multiple ingredients to a single cocktail
2. Specify exact measurements and units for each ingredient
3. Add preparation notes (e.g., "muddled", "expressed")
4. Control the order of ingredient addition
5. Remove ingredients they don't want

Key Features:
- Minimum 1 ingredient required (cocktails need ingredients!)
- Maximum 15 ingredients (prevents abuse and keeps recipes reasonable)
- Dynamic add/remove functionality (handled by JavaScript in templates)
- Proper validation of all ingredient data
- Integration with existing Cocktail and Ingredient models

In Views:
    formset = RecipeComponentFormSet(request.POST or None, instance=cocktail)
    if cocktail_form.is_valid() and formset.is_valid():
        # Save cocktail first
        cocktail = cocktail_form.save()
        # Then save all ingredients
        formset.instance = cocktail
        formset.save()

In Templates:
    {{ formset.management_form }}  {# Required for formset management #}
    {% for form in formset %}
        {# Render each ingredient form #}
        {{ form.ingredient }}
        {{ form.amount }} {{ form.unit }}
        {{ form.preparation_note }}
    {% endfor %}
"""


# =============================================================================
# 🧂 QUICK INGREDIENT CREATION FORM
# =============================================================================

class QuickIngredientForm(forms.ModelForm):
    """
    Simplified form for quickly adding new ingredients while creating cocktails.
    Can be used in a modal or inline with the main cocktail form.
    """
    
    class Meta:
        model = Ingredient
        fields = ['name', 'ingredient_type', 'alcohol_content', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., London Dry Gin'
            }),
            'ingredient_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'alcohol_content': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '100',
                'step': '0.1',
                'placeholder': '40.0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Optional: Brand, tasting notes, etc.'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False
        

# =============================================================================
# 🍸 QUICK VESSEL CREATION FORM  
# =============================================================================

class QuickVesselForm(forms.ModelForm):
    """
    Simplified form for quickly adding new vessels while creating cocktails.
    """
    
    class Meta:
        model = Vessel
        fields = ['name', 'volume', 'material', 'stemmed']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Martini Glass'
            }),
            'volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01',
                'placeholder': '240.00'
            }),
            'material': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Glass, Crystal, Copper'
            }),
            'stemmed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }


# =============================================================================
# 🔍 SEARCH AND FILTER FORMS
# =============================================================================

class CocktailSearchForm(forms.Form):
    """
    Form for searching and filtering cocktails.
    Used in list views and search pages.
    """
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search cocktails by name or ingredient...',
            'autocomplete': 'off'
        })
    )
    
    ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.all().order_by('name'),
        required=False,
        empty_label="Any ingredient",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    vessel = forms.ModelChoiceField(
        queryset=Vessel.objects.all().order_by('name'),
        required=False,
        empty_label="Any glassware",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    is_alcoholic = forms.ChoiceField(
        choices=[
            ('', 'All drinks'),
            ('True', 'Alcoholic only'),
            ('False', 'Non-alcoholic only')
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    color = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by color...'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest first'),
            ('created_at', 'Oldest first'),
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('creator__username', 'Creator A-Z'),
        ],
        required=False,
        initial='-created_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )


# =============================================================================
# 🏷️ BULK TAGGING FORM
# =============================================================================

class BulkTagForm(forms.Form):
    """
    Form for bulk adding tags to multiple cocktails.
    Useful for organizing existing recipes.
    """
    
    cocktails = forms.ModelMultipleChoiceField(
        queryset=Cocktail.objects.none(),  # Will be set in view
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        })
    )
    
    tags_to_add = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tags to add (comma-separated)'
        })
    )
    
    tags_to_remove = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tags to remove (comma-separated)'
        })
    )

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['cocktails'].queryset = Cocktail.objects.filter(creator=user)
