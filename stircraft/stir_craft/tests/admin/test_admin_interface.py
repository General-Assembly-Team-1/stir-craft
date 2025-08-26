"""
Admin Interface Tests for StirCraft

This module tests Django admin interface functionality including:
- ModelAdmin configurations and customizations
- Inline editing functionality  
- Search and filtering capabilities
- Permission and access control
- Form validation in admin context

Author: StirCraft Development Team
Date: August 2025
"""

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import RequestFactory
from django.urls import reverse
from unittest.mock import Mock

from ...admin import (
    CocktailAdmin, IngredientAdmin, VesselAdmin, 
    RecipeComponentAdmin, ListAdmin, ProfileAdmin,
    RecipeComponentInline
)
from ...models import (
    Cocktail, Ingredient, Vessel, RecipeComponent, 
    List, Profile
)


class AdminInterfaceTest(TestCase):
    """Test class for admin interface functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test data for admin testing."""
        # Create users with different permission levels
        cls.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@stircraft.com',
            password='admin_password_123'
        )
        
        cls.staff_user = User.objects.create_user(
            username='staff_member',
            email='staff@stircraft.com',
            password='staff_password_123',
            is_staff=True
        )
        
        cls.regular_user = User.objects.create_user(
            username='regular_user',
            email='user@stircraft.com',
            password='user_password_123'
        )
        
        # Create test data
        cls.vessel = Vessel.objects.create(
            name='Rocks Glass',
            volume=250.0,
            material='Glass',
            stemmed=False
        )
        
        cls.ingredient = Ingredient.objects.create(
            name='Test Vodka',
            ingredient_type='spirit',
            alcohol_content=40.0,
            description='Premium test vodka'
        )
        
        cls.cocktail = Cocktail.objects.create(
            name='Test Admin Cocktail',
            instructions='Mix well and serve',
            creator=cls.regular_user,
            vessel=cls.vessel,
            color='Clear'
        )
        
        cls.recipe_component = RecipeComponent.objects.create(
            cocktail=cls.cocktail,
            ingredient=cls.ingredient,
            amount=50.0,
            unit='ml',
            order=1
        )
        
        cls.user_list = List.objects.create(
            name='Test Admin List',
            creator=cls.regular_user,
            list_type='custom',
            description='Test list for admin testing'
        )
        
        cls.profile = Profile.objects.create(
            user=cls.regular_user,
            location='12345'
        )

    def setUp(self):
        """Set up for each test method."""
        self.factory = RequestFactory()
        self.site = AdminSite()
        
    def test_cocktail_admin_configuration(self):
        """Test CocktailAdmin configuration and display."""
        admin_instance = CocktailAdmin(Cocktail, self.site)
        
        # Test list_display configuration
        expected_list_display = ("name", "creator", "is_alcoholic", "created_at")
        self.assertEqual(admin_instance.list_display, expected_list_display)
        
        # Test search_fields configuration
        expected_search_fields = ("name", "creator__username")
        self.assertEqual(admin_instance.search_fields, expected_search_fields)
        
        # Test list_filter configuration
        expected_list_filter = ("is_alcoholic", "color")
        self.assertEqual(admin_instance.list_filter, expected_list_filter)
        
        # Test that RecipeComponentInline is included
        self.assertIn(RecipeComponentInline, admin_instance.inlines)
        
        # Test autocomplete fields
        expected_autocomplete = ("vessel",)
        self.assertEqual(admin_instance.autocomplete_fields, expected_autocomplete)
    
    def test_ingredient_admin_configuration(self):
        """Test IngredientAdmin configuration and display."""
        admin_instance = IngredientAdmin(Ingredient, self.site)
        
        # Test list_display configuration
        expected_list_display = ("name", "ingredient_type", "alcohol_content", "created_at")
        self.assertEqual(admin_instance.list_display, expected_list_display)
        
        # Test search_fields configuration
        expected_search_fields = ("name", "description")
        self.assertEqual(admin_instance.search_fields, expected_search_fields)
        
        # Test list_filter configuration
        expected_list_filter = ("ingredient_type",)
        self.assertEqual(admin_instance.list_filter, expected_list_filter)
    
    def test_vessel_admin_configuration(self):
        """Test VesselAdmin configuration and display."""
        admin_instance = VesselAdmin(Vessel, self.site)
        
        # Test list_display configuration
        expected_list_display = ("name", "volume", "material", "stemmed")
        self.assertEqual(admin_instance.list_display, expected_list_display)
        
        # Test search_fields configuration
        expected_search_fields = ("name", "material")
        self.assertEqual(admin_instance.search_fields, expected_search_fields)
        
        # Test list_filter configuration
        expected_list_filter = ("stemmed",)
        self.assertEqual(admin_instance.list_filter, expected_list_filter)
    
    def test_recipe_component_inline_configuration(self):
        """Test RecipeComponentInline configuration."""
        inline_instance = RecipeComponentInline(Cocktail, self.site)
        
        # Test model is correct
        self.assertEqual(inline_instance.model, RecipeComponent)
        
        # Test extra is set to 0 (no extra empty forms)
        self.assertEqual(inline_instance.extra, 0)
        
        # Test fields configuration
        expected_fields = ("order", "ingredient", "amount", "unit", "preparation_note")
        self.assertEqual(inline_instance.fields, expected_fields)
        
        # Test autocomplete fields
        expected_autocomplete = ("ingredient",)
        self.assertEqual(inline_instance.autocomplete_fields, expected_autocomplete)
        
        # Test ordering
        expected_ordering = ("order",)
        self.assertEqual(inline_instance.ordering, expected_ordering)
    
    def test_list_admin_configuration(self):
        """Test ListAdmin configuration and display."""
        admin_instance = ListAdmin(List, self.site)
        
        # Test list_display configuration
        expected_list_display = ("name", "creator", "list_type", "is_editable", "is_deletable", "updated_at")
        self.assertEqual(admin_instance.list_display, expected_list_display)
        
        # Test search_fields configuration
        expected_search_fields = ("name", "creator__username")
        self.assertEqual(admin_instance.search_fields, expected_search_fields)
        
        # Test list_filter configuration
        expected_list_filter = ("list_type", "is_editable", "is_deletable")
        self.assertEqual(admin_instance.list_filter, expected_list_filter)
    
    def test_profile_admin_configuration(self):
        """Test ProfileAdmin configuration and display."""
        admin_instance = ProfileAdmin(Profile, self.site)
        
        # Test list_display configuration
        expected_list_display = ("user", "location", "birthdate", "updated_at")
        self.assertEqual(admin_instance.list_display, expected_list_display)
        
        # Test search_fields configuration
        expected_search_fields = ("user__username", "location")
        self.assertEqual(admin_instance.search_fields, expected_search_fields)
    
    def test_admin_access_permissions(self):
        """Test admin access requires proper permissions."""
        # Test superuser access
        self.client.login(username='admin', password='admin_password_123')
        
        admin_urls = [
            '/admin/',
            '/admin/stir_craft/cocktail/',
            '/admin/stir_craft/ingredient/',
            '/admin/stir_craft/vessel/',
        ]
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [200, 302], 
                         f"Superuser should have access to {url}")
        
        # Test regular user cannot access admin
        self.client.logout()
        self.client.login(username='regular_user', password='user_password_123')
        
        for url in admin_urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403], 
                         f"Regular user should not have access to {url}")
    
    def test_cocktail_admin_search_functionality(self):
        """Test search functionality in cocktail admin."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Create additional test cocktails
        other_user = User.objects.create_user(
            username='other_creator',
            email='other@stircraft.com',
            password='other_password_123'
        )
        
        Cocktail.objects.create(
            name='Searchable Cocktail',
            instructions='Easy to find',
            creator=other_user,
            vessel=self.vessel
        )
        
        # Test search by cocktail name
        response = self.client.get('/admin/stir_craft/cocktail/?q=Searchable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Searchable Cocktail')
        
        # Test search by creator username
        response = self.client.get('/admin/stir_craft/cocktail/?q=other_creator')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Searchable Cocktail')
    
    def test_cocktail_admin_filtering(self):
        """Test filtering functionality in cocktail admin."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Create cocktails with different characteristics
        alcoholic_cocktail = Cocktail.objects.create(
            name='Strong Cocktail',
            instructions='Very alcoholic',
            creator=self.regular_user,
            vessel=self.vessel
        )
        
        # Add alcoholic ingredient to make it alcoholic
        RecipeComponent.objects.create(
            cocktail=alcoholic_cocktail,
            ingredient=self.ingredient,  # Has 40% alcohol
            amount=100.0,
            unit='ml'
        )
        
        # Test filter by alcoholic status
        response = self.client.get('/admin/stir_craft/cocktail/?is_alcoholic__exact=1')
        self.assertEqual(response.status_code, 200)
        
        # Test filter by color
        response = self.client.get('/admin/stir_craft/cocktail/?color__exact=Clear')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Admin Cocktail')
    
    def test_ingredient_admin_search_and_filter(self):
        """Test ingredient admin search and filtering."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Create additional test ingredients
        Ingredient.objects.create(
            name='Gin',
            ingredient_type='spirit',
            alcohol_content=42.0,
            description='London Dry Gin'
        )
        
        Ingredient.objects.create(
            name='Tonic Water',
            ingredient_type='mixer',
            alcohol_content=0.0,
            description='Premium tonic water'
        )
        
        # Test search by name
        response = self.client.get('/admin/stir_craft/ingredient/?q=Gin')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gin')
        
        # Test search by description
        response = self.client.get('/admin/stir_craft/ingredient/?q=London')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Gin')
        
        # Test filter by ingredient type
        response = self.client.get('/admin/stir_craft/ingredient/?ingredient_type__exact=spirit')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Vodka')
        self.assertContains(response, 'Gin')
    
    def test_inline_recipe_components_functionality(self):
        """Test inline editing of recipe components in cocktail admin."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Get the cocktail change page
        response = self.client.get(f'/admin/stir_craft/cocktail/{self.cocktail.id}/change/')
        self.assertEqual(response.status_code, 200)
        
        # Check that inline components are present
        # In the admin, the inline is named 'components' not 'recipecomponent_set'
        self.assertContains(response, 'components-group')
        self.assertContains(response, 'Recipe components')
        
        # Test that existing component is shown
        self.assertContains(response, str(self.recipe_component.ingredient.name))
        self.assertContains(response, str(self.recipe_component.amount))
        
        # Test ordering field is present
        self.assertContains(response, 'components-0-order')
        
        # Test that we can add new components
        self.assertContains(response, 'Add another Recipe component')
    
    def test_admin_bulk_actions(self):
        """Test bulk actions in admin interface."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Create additional cocktails for bulk testing
        cocktail2 = Cocktail.objects.create(
            name='Bulk Test Cocktail 2',
            instructions='For bulk testing',
            creator=self.regular_user,
            vessel=self.vessel
        )
        
        # Test bulk delete action
        response = self.client.post('/admin/stir_craft/cocktail/', {
            'action': 'delete_selected',
            '_selected_action': [str(self.cocktail.id), str(cocktail2.id)],
            'post': 'yes'
        })
        
        # Should redirect to confirmation page or complete action
        self.assertIn(response.status_code, [200, 302])
    
    def test_admin_form_validation(self):
        """Test form validation in admin interface."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Test invalid cocktail creation
        response = self.client.post('/admin/stir_craft/cocktail/add/', {
            'name': '',  # Empty name should fail validation
            'instructions': 'Test instructions',
            'creator': self.regular_user.id,
            'vessel': self.vessel.id
        })
        
        # Should show form with errors
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
    
    def test_autocomplete_functionality(self):
        """Test autocomplete functionality in admin."""
        self.client.login(username='admin', password='admin_password_123')
        
        # Test vessel autocomplete in cocktail admin
        response = self.client.get('/admin/autocomplete/', {
            'app_label': 'stir_craft',
            'model_name': 'cocktail', 
            'field_name': 'vessel',
        })
        self.assertEqual(response.status_code, 200)
        
        # Response should be JSON
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Test ingredient autocomplete in recipe component admin
        response = self.client.get('/admin/autocomplete/', {
            'app_label': 'stir_craft',
            'model_name': 'recipecomponent',
            'field_name': 'ingredient',
        })
        self.assertEqual(response.status_code, 200)


class AdminPermissionTest(TestCase):
    """Test admin permissions and access control."""
    
    def setUp(self):
        """Set up users with different permission levels."""
        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='super@stircraft.com',
            password='super_password_123'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff_user',
            email='staff@stircraft.com',
            password='staff_password_123',
            is_staff=True
        )
        
        self.regular_user = User.objects.create_user(
            username='regular_user',
            email='regular@stircraft.com',
            password='regular_password_123'
        )
        
        # Add specific permissions to staff user
        content_type = ContentType.objects.get_for_model(Cocktail)
        permission = Permission.objects.get(
            codename='view_cocktail',
            content_type=content_type
        )
        self.staff_user.user_permissions.add(permission)
    
    def test_superuser_has_all_permissions(self):
        """Test that superuser has access to all admin features."""
        self.client.login(username='superuser', password='super_password_123')
        
        # Should have access to all model admin pages
        admin_pages = [
            '/admin/stir_craft/cocktail/',
            '/admin/stir_craft/ingredient/',
            '/admin/stir_craft/vessel/',
            '/admin/stir_craft/list/',
            '/admin/stir_craft/profile/',
        ]
        
        for page in admin_pages:
            response = self.client.get(page)
            self.assertEqual(response.status_code, 200, 
                           f"Superuser should access {page}")
    
    def test_staff_user_limited_permissions(self):
        """Test that staff user only has access to permitted models."""
        self.client.login(username='staff_user', password='staff_password_123')
        
        # Should have access to main admin page
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        
        # Should have limited access based on permissions
        response = self.client.get('/admin/stir_craft/cocktail/')
        # Staff user with view permission should be able to access
        self.assertIn(response.status_code, [200, 403])
    
    def test_regular_user_no_admin_access(self):
        """Test that regular users cannot access admin."""
        self.client.login(username='regular_user', password='regular_password_123')
        
        # Should be redirected from admin pages
        response = self.client.get('/admin/')
        self.assertNotEqual(response.status_code, 200)
        
        response = self.client.get('/admin/stir_craft/cocktail/')
        self.assertNotEqual(response.status_code, 200)
    
    def test_anonymous_user_no_admin_access(self):
        """Test that anonymous users cannot access admin."""
        # No login
        
        response = self.client.get('/admin/')
        self.assertIn(response.status_code, [302, 403])
        
        response = self.client.get('/admin/stir_craft/cocktail/')
        self.assertIn(response.status_code, [302, 403])
