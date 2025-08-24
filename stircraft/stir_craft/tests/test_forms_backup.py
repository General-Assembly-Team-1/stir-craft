from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Ingredient, Cocktail, RecipeComponent, Vessel
from ..forms.cocktail_forms import CocktailForm, RecipeComponentForm, RecipeComponentFormSet, CocktailSearchForm, QuickIngredientForm
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


class QuickIngredientFormTest(TestCase):
    """
    Test class for QuickIngredientForm functionality.
    
    Tests the quick ingredient creation form including duplicate detection,
    validation, and enhanced error messages.
    """
    
    def setUp(self):
        """Set up test data for quick ingredient form tests."""
        # Create existing ingredients for duplicate testing
        self.existing_ingredient = Ingredient.objects.create(
            name='Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0,
            description='Premium vodka',
        )
        # Add some flavor tags
        self.existing_ingredient.flavor_tags.add('neutral', 'clean')
        
        self.case_variant = Ingredient.objects.create(
            name='Lime Juice',
            ingredient_type='juice',
            alcohol_content=0.0,
        )

    def test_quick_ingredient_form_valid_data(self):
        """Test QuickIngredientForm with valid data."""
        form_data = {
            'name': 'London Dry Gin',
            'ingredient_type': 'spirit',
            'alcohol_content': 42.0,
            'description': 'Classic London Dry style gin',
            'flavor_tags': 'juniper, citrusy, herbal'
        }
        form = QuickIngredientForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_quick_ingredient_form_required_fields(self):
        """Test that required fields are properly validated."""
        form_data = {
            'description': 'Missing required fields',
            'flavor_tags': 'test'
        }
        form = QuickIngredientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('ingredient_type', form.errors)
        self.assertIn('alcohol_content', form.errors)

    def test_duplicate_ingredient_exact_match(self):
        """Test that exact duplicate ingredient names are detected."""
        form_data = {
            'name': 'Vodka',  # Exact match with existing ingredient
            'ingredient_type': 'spirit',
            'alcohol_content': 40.0,
        }
        form = QuickIngredientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Check that error message includes category information
        error_message = form.errors['name'][0]
        self.assertIn('already exists', error_message)
        self.assertIn('Spirit category', error_message)
        self.assertIn('Try searching', error_message)

    def test_duplicate_ingredient_case_insensitive(self):
        """Test that case-insensitive duplicates are detected."""
        form_data = {
            'name': 'vodka',  # Different case than existing 'Vodka'
            'ingredient_type': 'spirit',
            'alcohol_content': 40.0,
        }
        form = QuickIngredientForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
        # Check for case-insensitive detection message
        error_message = form.errors['name'][0]
        self.assertIn('already exists', error_message)
        self.assertIn('Did you mean', error_message)

    def test_flavor_tags_field(self):
        """Test flavor tags field functionality."""
        form_data = {
            'name': 'Flavored Gin',
            'ingredient_type': 'spirit',
            'alcohol_content': 40.0,
            'flavor_tags': 'botanical, citrusy, herbal, floral'
        }
        form = QuickIngredientForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        # Test saving and retrieving tags
        ingredient = form.save()
        tag_names = [tag.name for tag in ingredient.flavor_tags.all()]
        expected_tags = ['botanical', 'citrusy', 'herbal', 'floral']
        for tag in expected_tags:
            self.assertIn(tag, tag_names)

    def test_form_field_widgets(self):
        """Test that form fields have correct widget classes."""
        form = QuickIngredientForm()
        
        # Check that form fields have Bootstrap classes
        self.assertEqual(form.fields['name'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['ingredient_type'].widget.attrs['class'], 'form-select')
        self.assertEqual(form.fields['alcohol_content'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['flavor_tags'].widget.attrs['class'], 'form-control')


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
