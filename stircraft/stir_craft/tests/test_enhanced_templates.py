from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template import Context, Template
from django.template.loader import render_to_string
from ..models import List, Cocktail, Profile, Vessel, Ingredient, RecipeComponent


class EnhancedTemplateTest(TestCase):
    """Tests for enhanced template functionality including partials and components."""

    def setUp(self):
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(username='template_user', password='pass123')
        self.profile, _ = Profile.objects.get_or_create(user=self.user)
        
        # Create test objects
        self.vessel = Vessel.objects.create(name='Coupe Glass', volume=180, material='Glass')
        self.ingredient1 = Ingredient.objects.create(
            name='Gin', 
            ingredient_type='spirit', 
            alcohol_content=40.0
        )
        self.ingredient1.flavor_tags.add('herbal', 'citrus')
        
        self.ingredient2 = Ingredient.objects.create(
            name='Simple Syrup', 
            ingredient_type='syrup', 
            alcohol_content=0.0
        )
        self.ingredient2.flavor_tags.add('sweet')
        
        self.ingredient3 = Ingredient.objects.create(
            name='Lemon Juice', 
            ingredient_type='juice', 
            alcohol_content=0.0
        )
        self.ingredient3.flavor_tags.add('sour', 'citrus')
        
        # Create a cocktail with flavor profiles
        self.cocktail = Cocktail.objects.create(
            name='Enhanced Gin Sour',
            instructions='Shake with ice, double strain into coupe',
            creator=self.user,
            vessel=self.vessel
        )
        
        # Add recipe components
        RecipeComponent.objects.create(
            cocktail=self.cocktail, 
            ingredient=self.ingredient1, 
            amount=60.0, 
            unit='ml', 
            order=1
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail, 
            ingredient=self.ingredient2, 
            amount=15.0, 
            unit='ml', 
            order=2
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail, 
            ingredient=self.ingredient3, 
            amount=25.0, 
            unit='ml', 
            order=3
        )
        
        # Create a list
        self.cocktail_list = List.objects.create(
            name='Test List',
            description='List for testing enhanced templates',
            creator=self.user,
            list_type='custom'
        )
        self.cocktail_list.cocktails.add(self.cocktail)

    def test_ingredients_table_partial_renders(self):
        """Test that the enhanced ingredients table partial renders correctly."""
        context = {
            'cocktail': self.cocktail,
            'recipe_components': self.cocktail.recipecomponent_set.all()
        }
        
        rendered = render_to_string(
            'partials/shared/_ingredients_table.html', 
            context
        )
        
        # Check that table structure is present
        self.assertIn('<table', rendered)
        self.assertIn('ingredients-table', rendered)
        self.assertIn('<th>Ingredient</th>', rendered)
        self.assertIn('<th>Amount</th>', rendered)
        self.assertIn('<th>Flavor Profile</th>', rendered)
        
        # Check that ingredients are present
        self.assertIn('Gin', rendered)
        self.assertIn('60.0 ml', rendered)
        self.assertIn('Simple Syrup', rendered)
        self.assertIn('15.0 ml', rendered)
        self.assertIn('Lemon Juice', rendered)
        self.assertIn('25.0 ml', rendered)
        
        # Check flavor tags are rendered
        self.assertIn('flavor-tag', rendered)
        self.assertIn('herbal', rendered)
        self.assertIn('citrus', rendered)
        self.assertIn('sweet', rendered)
        self.assertIn('sour', rendered)

    def test_cocktail_header_partial_renders(self):
        """Test that the enhanced cocktail header partial renders correctly."""
        context = {
            'cocktail': self.cocktail,
            'user': self.user
        }
        
        rendered = render_to_string(
            'partials/cocktails/_cocktail_header.html', 
            context
        )
        
        # Check cocktail name and details
        self.assertIn('Enhanced Gin Sour', rendered)
        self.assertIn('Coupe Glass', rendered)

    def test_enhanced_actions_partial_renders(self):
        """Test that the enhanced actions partial renders correctly."""
        self.client.login(username='template_user', password='pass123')
        
        context = {
            'cocktail': self.cocktail,
            'user': self.user,
            'request': self.client.request().wsgi_request
        }
        
        rendered = render_to_string(
            'partials/cocktails/_enhanced_actions.html', 
            context
        )
        
        # Check action buttons are present
        self.assertIn('cocktail-actions', rendered)
        self.assertIn('btn-favorite', rendered)
        self.assertIn('btn-add-to-list', rendered)
        
        # Check for edit button (should be present for owner)
        self.assertIn('btn-edit', rendered)
        self.assertIn('Edit Cocktail', rendered)

    def test_enhanced_actions_partial_for_non_owner(self):
        """Test enhanced actions partial for non-owner user."""
        other_user = User.objects.create_user(username='other_user', password='pass123')
        self.client.login(username='other_user', password='pass123')
        
        context = {
            'cocktail': self.cocktail,
            'user': other_user,
            'request': self.client.request().wsgi_request
        }
        
        rendered = render_to_string(
            'partials/cocktails/_enhanced_actions.html', 
            context
        )
        
        # Check action buttons are present
        self.assertIn('btn-favorite', rendered)
        self.assertIn('btn-add-to-list', rendered)
        
        # Check edit button is NOT present for non-owner
        self.assertNotIn('btn-edit', rendered)
        self.assertNotIn('Edit Cocktail', rendered)

    def test_flavor_tag_rendering(self):
        """Test that flavor tags are rendered with correct CSS classes."""
        context = {
            'cocktail': self.cocktail,
            'recipe_components': self.cocktail.recipecomponent_set.all()
        }
        
        rendered = render_to_string(
            'partials/shared/_ingredients_table.html', 
            context
        )
        
        # Check specific flavor tag classes
        self.assertIn('flavor-herbal', rendered)
        self.assertIn('flavor-citrus', rendered)
        self.assertIn('flavor-sweet', rendered)
        self.assertIn('flavor-sour', rendered)

    def test_cocktail_detail_template_integration(self):
        """Test that the cocktail detail template properly integrates all partials."""
        self.client.login(username='template_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check that partials are included
        self.assertContains(response, 'ingredients-table')
        self.assertContains(response, 'cocktail-actions')
        self.assertContains(response, 'Enhanced Gin Sour')
        
        # Check flavor tags
        self.assertContains(response, 'flavor-tag')
        self.assertContains(response, 'herbal')
        self.assertContains(response, 'citrus')

    def test_profile_template_enhanced_lists(self):
        """Test that profile template shows enhanced list information."""
        self.client.login(username='template_user', password='pass123')
        url = reverse('profile_detail')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check enhanced profile content
        self.assertContains(response, 'Test List')
        self.assertContains(response, 'cocktails created')
        self.assertContains(response, 'lists-overview-card')

    def test_empty_state_partials(self):
        """Test that empty state partials render correctly."""
        # Create a user with no cocktails
        empty_user = User.objects.create_user(username='empty_user', password='pass123')
        empty_list = List.objects.create(
            name='Empty List',
            description='A list with no cocktails',
            creator=empty_user,
            list_type='custom'
        )
        
        context = {
            'list': empty_list,
            'cocktails': empty_list.cocktails.all()  # Empty queryset
        }
        
        rendered = render_to_string(
            'partials/shared/_empty_list_state.html', 
            context
        )
        
        # Check empty state content
        self.assertIn('No cocktails', rendered)
        self.assertIn('empty-state', rendered)

    def test_instructions_rendering_in_detail(self):
        """Test that cocktail instructions are properly formatted."""
        self.client.login(username='template_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check instructions are rendered
        self.assertContains(response, 'Shake with ice, double strain into coupe')
        self.assertContains(response, 'instructions-text')

    def test_responsive_design_classes(self):
        """Test that responsive design classes are present in templates."""
        self.client.login(username='template_user', password='pass123')
        url = reverse('cocktail_detail', kwargs={'cocktail_id': self.cocktail.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Check for Bootstrap responsive classes
        self.assertContains(response, 'col-md-')
        self.assertContains(response, 'row')
        self.assertContains(response, 'container')

    def test_attribution_handling_without_url(self):
        """Test attribution rendering when URL is not provided."""
        # Create cocktail with attribution text but no URL
        cocktail_no_url = Cocktail.objects.create(
            name='No URL Cocktail',
            instructions='Simple instructions',
            creator=self.user,
            vessel=self.vessel,
            attribution_text='From memory'
            # No attribution_url
        )
        
        context = {
            'cocktail': cocktail_no_url,
            'user': self.user
        }
        
        rendered = render_to_string(
            'partials/cocktails/_cocktail_header.html', 
            context
        )
        
        # Should show attribution text but no link
        self.assertIn('From memory', rendered)
        self.assertNotIn('<a', rendered)  # No link should be present

    def test_attribution_handling_without_text(self):
        """Test attribution rendering when neither text nor URL is provided."""
        cocktail_no_attribution = Cocktail.objects.create(
            name='No Attribution Cocktail',
            instructions='Simple instructions',
            creator=self.user,
            vessel=self.vessel
            # No attribution fields
        )
        
        context = {
            'cocktail': cocktail_no_attribution,
            'user': self.user
        }
        
        rendered = render_to_string(
            'partials/cocktails/_cocktail_header.html', 
            context
        )
        
        # Should not show attribution section at all
        self.assertNotIn('attribution-text', rendered)
        self.assertNotIn('attribution-link', rendered)
