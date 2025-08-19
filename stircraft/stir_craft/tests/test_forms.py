from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Ingredient, Cocktail, RecipeComponent, Vessel
from ..forms.cocktail_forms import CocktailForm, RecipeComponentForm, RecipeComponentFormSet, CocktailSearchForm
from datetime import date


class CocktailFormTest(TestCase):
    """
    Test class for CocktailForm functionality.
    
    Tests the main cocktail creation form including validation,
    field behavior, and integration with the User model.
    """
    
    def setUp(self):
        """Set up test data for cocktail form tests."""
        self.user = User.objects.create_user(
            username='cocktail_creator',
            email='creator@stircraft.com',
            password='test_password_123'
        )
        self.vessel = Vessel.objects.create(
            name='Martini Glass',
            volume=180.0,
            material='Glass',
            stemmed=True
        )

    def test_cocktail_form_valid_data(self):
        """Test CocktailForm with valid data."""
        form_data = {
            'name': 'Classic Margarita',
            'description': 'A refreshing tequila-based cocktail',
            'instructions': 'Shake with ice and strain into glass',
            'vessel': self.vessel.id,
            'is_alcoholic': True,
            'color': 'Yellow',
            'vibe_tags': 'tropical, citrusy, refreshing'
        }
        form = CocktailForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_cocktail_form_required_fields(self):
        """Test that required fields are properly validated."""
        # Test with missing name (required field)
        form_data = {
            'description': 'A test cocktail',
            'instructions': '',  # Missing required instructions
        }
        form = CocktailForm(data=form_data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('instructions', form.errors)

    def test_cocktail_form_optional_fields(self):
        """Test that optional fields work correctly."""
        form_data = {
            'name': 'Simple Cocktail',
            'instructions': 'Mix and serve',
            # description, vessel, color, vibe_tags are optional
        }
        form = CocktailForm(data=form_data, user=self.user)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_cocktail_form_user_context(self):
        """Test that form behaves correctly with user context."""
        form = CocktailForm(user=self.user)
        # Check that vessel queryset is properly set
        self.assertIn(self.vessel, form.fields['vessel'].queryset)
        # Check that help text includes user reference
        self.assertIn(self.user.username, form.fields['name'].help_text)


class RecipeComponentFormTest(TestCase):
    """
    Test class for RecipeComponentForm functionality.
    
    Tests the individual ingredient form used within the formset.
    """
    
    def setUp(self):
        """Set up test data for recipe component form tests."""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.cocktail = Cocktail.objects.create(
            name='Test Cocktail',
            instructions='Test instructions',
            creator=self.user
        )
        self.ingredient = Ingredient.objects.create(
            name='Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )

    def test_recipe_component_form_valid_data(self):
        """Test RecipeComponentForm with valid data."""
        form_data = {
            'ingredient': self.ingredient.id,
            'amount': 50.0,
            'unit': 'ml',
            'preparation_note': 'Chilled',
            'order': 1
        }
        form = RecipeComponentForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_recipe_component_form_required_fields(self):
        """Test that required fields are validated."""
        form_data = {
            # Missing ingredient, amount, unit (all required)
            'preparation_note': 'Optional note',
            'order': 1
        }
        form = RecipeComponentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ingredient', form.errors)
        self.assertIn('amount', form.errors)
        self.assertIn('unit', form.errors)

    def test_recipe_component_form_amount_validation(self):
        """Test amount field validation."""
        form_data = {
            'ingredient': self.ingredient.id,
            'amount': -10.0,  # Negative amount should be invalid
            'unit': 'ml',
            'order': 1
        }
        form = RecipeComponentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_recipe_component_form_unit_choices(self):
        """Test that unit field accepts valid choices."""
        valid_units = ['oz', 'ml', 'tsp', 'tbsp', 'dash', 'splash', 'pinch', 'piece', 'slice', 'wedge', 'sprig']
        
        for unit in valid_units:
            form_data = {
                'ingredient': self.ingredient.id,
                'amount': 30.0,
                'unit': unit,
                'order': 1
            }
            form = RecipeComponentForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Unit '{unit}' should be valid. Errors: {form.errors}")


class RecipeComponentFormsetTest(TestCase):
    """
    Test class for RecipeComponentFormSet functionality.
    
    Tests the formset that manages multiple ingredients in a cocktail.
    """
    
    def setUp(self):
        """Set up test data for formset tests."""
        self.user = User.objects.create_user(username='testuser', password='pass123')
        self.cocktail = Cocktail.objects.create(
            name='Test Cocktail',
            instructions='Test instructions',
            creator=self.user
        )
        self.vodka = Ingredient.objects.create(
            name='Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        self.juice = Ingredient.objects.create(
            name='Orange Juice',
            ingredient_type='juice',
            alcohol_content=0.0
        )

    def test_formset_minimum_forms(self):
        """Test that formset requires minimum number of forms."""
        # Empty formset should be invalid (min_num=1)
        formset_data = {
            'components-TOTAL_FORMS': '1',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            # No actual form data
        }
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        self.assertFalse(formset.is_valid())

    def test_formset_valid_data(self):
        """Test formset with valid ingredient data."""
        formset_data = {
            'components-TOTAL_FORMS': '2',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            
            'components-0-ingredient': self.vodka.id,
            'components-0-amount': '50.0',
            'components-0-unit': 'ml',
            'components-0-preparation_note': '',
            'components-0-order': '1',
            
            'components-1-ingredient': self.juice.id,
            'components-1-amount': '100.0',
            'components-1-unit': 'ml',
            'components-1-preparation_note': 'Fresh squeezed',
            'components-1-order': '2',
        }
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        self.assertTrue(formset.is_valid(), f"Formset errors: {formset.errors}")

    def test_formset_maximum_forms(self):
        """Test that formset enforces maximum number of forms."""
        # Create formset data with more than max_num (15) forms
        formset_data = {
            'components-TOTAL_FORMS': '16',  # More than max_num=15
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
        }
        # Add 16 ingredient forms
        for i in range(16):
            formset_data.update({
                f'components-{i}-ingredient': self.vodka.id,
                f'components-{i}-amount': '30.0',
                f'components-{i}-unit': 'ml',
                f'components-{i}-order': str(i + 1),
            })
        
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        self.assertFalse(formset.is_valid())

    def test_formset_deletion(self):
        """Test formset deletion functionality."""
        # Create a cocktail with existing ingredients
        component = RecipeComponent.objects.create(
            cocktail=self.cocktail,
            ingredient=self.vodka,
            amount=50.0,
            unit='ml',
            order=1
        )
        
        formset_data = {
            'components-TOTAL_FORMS': '1',
            'components-INITIAL_FORMS': '1',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            
            'components-0-id': component.id,
            'components-0-ingredient': self.vodka.id,
            'components-0-amount': '50.0',
            'components-0-unit': 'ml',
            'components-0-order': '1',
            'components-0-DELETE': 'on',  # Mark for deletion
        }
        
        formset = RecipeComponentFormSet(data=formset_data, instance=self.cocktail)
        # Note: This will fail validation because min_num=1 and we're deleting the only form
        self.assertFalse(formset.is_valid())


class CocktailSearchFormTest(TestCase):
    """
    Test class for CocktailSearchForm functionality.
    
    Tests the search and filter form used in cocktail browsing.
    """
    
    def setUp(self):
        """Set up test data for search form tests."""
        self.ingredient = Ingredient.objects.create(
            name='Gin',
            ingredient_type='spirit',
            alcohol_content=40.0
        )
        self.vessel = Vessel.objects.create(
            name='Coupe Glass',
            volume=150.0,
            material='Glass'
        )

    def test_search_form_empty_data(self):
        """Test search form with no data (should be valid)."""
        form = CocktailSearchForm(data={})
        self.assertTrue(form.is_valid())

    def test_search_form_text_search(self):
        """Test search form with text query."""
        form_data = {
            'query': 'margarita',
            'sort_by': '-created_at'
        }
        form = CocktailSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_filters(self):
        """Test search form with various filters."""
        form_data = {
            'ingredient': self.ingredient.id,
            'vessel': self.vessel.id,
            'is_alcoholic': 'True',
            'color': 'red',
            'sort_by': 'name'
        }
        form = CocktailSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_search_form_sort_options(self):
        """Test all sort options are valid."""
        sort_options = ['-created_at', 'created_at', 'name', '-name', 'creator__username']
        
        for sort_option in sort_options:
            form_data = {'sort_by': sort_option}
            form = CocktailSearchForm(data=form_data)
            self.assertTrue(form.is_valid(), f"Sort option '{sort_option}' should be valid")
