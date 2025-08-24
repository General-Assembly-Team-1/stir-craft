from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from ..models import List, Cocktail, Profile, Vessel, Ingredient, RecipeComponent


class EnhancedCSSTest(TestCase):
    """Tests for enhanced CSS functionality and styling."""

    def setUp(self):
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(username='css_user', password='pass123')
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        
        # Create test objects
        self.vessel = Vessel.objects.create(name='Test Glass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient', 
            ingredient_type='spirit', 
            alcohol_content=40.0,
            flavor_profile='sweet,citrus'
        )
        
        # Create cocktail
        self.cocktail = Cocktail.objects.create(
            name='CSS Test Cocktail',
            instructions='Test instructions',
            creator=self.user,
            vessel=self.vessel,
            attribution_text='Test attribution',
            attribution_url='https://example.com'
        )
        
        RecipeComponent.objects.create(
            cocktail=self.cocktail, 
            ingredient=self.ingredient, 
            amount=50.0, 
            unit='ml', 
            order=1
        )

    def test_cocktail_css_classes_in_response(self):
        """Test that enhanced CSS classes are present in cocktail detail page."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for enhanced CSS classes
        css_classes = [
            'cocktail-actions',
            'btn-action',
            'btn-favorite',
            'btn-add-to-list',
            'ingredients-table',
            'flavor-tag',
            'attribution-text',
            'attribution-link',
            'instructions-text'
        ]
        
        for css_class in css_classes:
            self.assertContains(response, css_class)

    def test_flavor_tag_css_classes(self):
        """Test that flavor-specific CSS classes are applied correctly."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for specific flavor tag classes based on ingredient flavor profile
        self.assertContains(response, 'flavor-sweet')
        self.assertContains(response, 'flavor-citrus')

    def test_responsive_design_classes(self):
        """Test that responsive design classes are present."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for Bootstrap responsive classes
        responsive_classes = [
            'col-md-',
            'col-lg-',
            'row',
            'container',
            'd-flex',
            'flex-wrap'
        ]
        
        response_content = response.content.decode()
        for css_class in responsive_classes:
            self.assertIn(css_class, response_content)

    def test_cocktail_css_file_loaded(self):
        """Test that cocktail.css file is properly loaded in templates."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that CSS file is linked
        self.assertContains(response, 'cocktail.css')

    def test_action_button_states(self):
        """Test that action buttons have correct states and classes."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check button structure and classes
        self.assertContains(response, 'data-cocktail-id')
        self.assertContains(response, 'data-is-favorited')
        
        # Check for action icons
        self.assertContains(response, 'fa-heart')
        self.assertContains(response, 'fa-plus')

    def test_ingredients_table_structure(self):
        """Test that ingredients table has proper CSS structure."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check table structure
        self.assertContains(response, '<table')
        self.assertContains(response, 'ingredients-table')
        self.assertContains(response, '<th>Ingredient</th>')
        self.assertContains(response, '<th>Amount</th>')
        self.assertContains(response, '<th>Flavor Profile</th>')

    def test_attribution_styling(self):
        """Test that attribution section has proper styling."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check attribution styling
        self.assertContains(response, 'attribution-text')
        self.assertContains(response, 'attribution-link')
        self.assertContains(response, 'Test attribution')
        self.assertContains(response, 'https://example.com')

    def test_toast_container_present(self):
        """Test that toast container for notifications is present."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for toast container
        self.assertContains(response, 'toast-container')

    def test_mobile_responsive_classes(self):
        """Test that mobile-specific responsive classes are present."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for mobile responsive behavior
        response_content = response.content.decode()
        
        # Should have mobile-friendly column classes
        self.assertIn('col-12', response_content)  # Full width on mobile
        self.assertIn('col-md-', response_content)  # Specific widths on larger screens

    def test_hover_effects_css_classes(self):
        """Test that hover effect classes are present for interactive elements."""
        self.client.login(username='css_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for elements that should have hover effects
        self.assertContains(response, 'btn-action')  # Action buttons should have hover
        self.assertContains(response, 'attribution-link')  # Attribution links should have hover


class CSSValidationTest(StaticLiveServerTestCase):
    """Tests for CSS file validation and structure."""

    def test_cocktail_css_file_exists(self):
        """Test that the cocktail.css file exists and is accessible."""
        from django.contrib.staticfiles import finders
        
        css_file = finders.find('css/cocktail.css')
        self.assertIsNotNone(css_file, "cocktail.css file should exist")

    def test_css_contains_required_classes(self):
        """Test that CSS file contains all the required enhanced classes."""
        from django.contrib.staticfiles import finders
        
        css_file = finders.find('css/cocktail.css')
        self.assertIsNotNone(css_file)
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        required_classes = [
            '.attribution-text',
            '.attribution-link',
            '.ingredients-table',
            '.flavor-tag',
            '.flavor-sweet',
            '.flavor-sour',
            '.flavor-bitter',
            '.flavor-citrus',
            '.cocktail-actions',
            '.btn-action',
            '.btn-favorite',
            '.btn-add-to-list',
            '.instructions-text',
            '.toast-container'
        ]
        
        for css_class in required_classes:
            self.assertIn(css_class, css_content, f"CSS should contain {css_class}")

    def test_css_responsive_design(self):
        """Test that CSS contains responsive design rules."""
        from django.contrib.staticfiles import finders
        
        css_file = finders.find('css/cocktail.css')
        self.assertIsNotNone(css_file)
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for responsive media queries
        self.assertIn('@media', css_content, "CSS should contain media queries")
        self.assertIn('max-width', css_content, "CSS should contain responsive breakpoints")

    def test_css_flavor_tag_colors(self):
        """Test that all flavor tag colors are defined."""
        from django.contrib.staticfiles import finders
        
        css_file = finders.find('css/cocktail.css')
        self.assertIsNotNone(css_file)
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        flavor_classes = [
            '.flavor-sweet',
            '.flavor-sour', 
            '.flavor-bitter',
            '.flavor-spicy',
            '.flavor-herbal',
            '.flavor-citrus',
            '.flavor-fruity',
            '.flavor-floral'
        ]
        
        for flavor_class in flavor_classes:
            self.assertIn(flavor_class, css_content, f"CSS should define {flavor_class}")
            
        # Check that colors are defined
        self.assertIn('background-color:', css_content)
        self.assertIn('color:', css_content)

    def test_css_button_hover_effects(self):
        """Test that button hover effects are defined."""
        from django.contrib.staticfiles import finders
        
        css_file = finders.find('css/cocktail.css')
        self.assertIsNotNone(css_file)
        
        with open(css_file, 'r', encoding='utf-8') as f:
            css_content = f.read()
        
        # Check for hover effects
        self.assertIn(':hover', css_content, "CSS should contain hover effects")
        self.assertIn('transition:', css_content, "CSS should contain transition effects")
        self.assertIn('transform:', css_content, "CSS should contain transform effects")
