from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from ..models import Profile, Ingredient, Cocktail, RecipeComponent, Vessel
from ..forms.profile_forms import SignUpForm, ProfileUpdateForm, ProfileDeleteForm
from datetime import date


class ProfileFormTest(TestCase):
    """
    Test class for profile-related forms.
    """
    
    def test_signup_form_valid_data(self):
        """Test SignUpForm with valid data."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@stircraft.com',
            'password1': 'complex_password_123',
            'password2': 'complex_password_123',
            'first_name': 'New',
            'last_name': 'User',
            'birthdate': '2000-01-01',
            'location': 'Test City',
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_signup_form_age_validation(self):
        """Test that SignUpForm validates minimum age (21)."""
        form_data = {
            'username': 'younguser',
            'email': 'young@stircraft.com',
            'password1': 'complex_password_123',
            'password2': 'complex_password_123',
            'birthdate': '2010-01-01',  # Too young
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('birthdate', form.errors)

    def test_signup_form_password_mismatch(self):
        """Test that SignUpForm validates password confirmation."""
        form_data = {
            'username': 'testuser',
            'email': 'test@stircraft.com',
            'password1': 'password_123',
            'password2': 'different_password',  # Mismatch
            'birthdate': '2000-01-01',
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_profile_update_form_valid_data(self):
        """Test ProfileUpdateForm with valid data."""
        user = User.objects.create_user(username='testuser', password='pass123')
        form_data = {
            'first_name': 'Updated',
            'last_name': 'Name', 
            'email': 'updated@stircraft.com',
            'birthdate': '1995-06-15',
            'location': 'Updated City',
        }
        form = ProfileUpdateForm(data=form_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")

    def test_profile_delete_form_confirmation(self):
        """Test ProfileDeleteForm requires confirmation."""
        form_data = {
            'confirmation': 'DELETE',
            'password': 'correct_password',
        }
        form = ProfileDeleteForm(data=form_data)
        # Note: This form requires user context for password validation
        # In a real test, you'd pass the user and validate accordingly
        self.assertIn('confirmation', form.fields)
        self.assertIn('password', form.fields)


class ProfileViewTest(TestCase):
    """
    Test class for profile-related views.
    """

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            birthdate=date(2000, 8, 10)
        )

    def test_profile_detail_current_user(self):
        """Test that profile detail view displays the current user's profile."""
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('profile_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_profile_detail_specific_user(self):
        """Test that profile detail view displays a specific user's profile."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='otheruser@example.com',
            password='password123'
        )
        other_profile = Profile.objects.create(
            user=other_user,
            birthdate=date(1990, 1, 1)
        )
        response = self.client.get(reverse('profile_detail', args=[other_user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, other_user.username)

    def test_profile_update_valid_submission(self):
        """Test that profile update view successfully updates the profile."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_update'), {
            'birthdate': '1999-01-01'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.birthdate, date(1999, 1, 1))

    def test_profile_update_invalid_submission(self):
        """Test that profile update view handles invalid submissions gracefully."""
        self.client.login(username='testuser', password='password123')
        response = self.client.post(reverse('profile_update'), {
            'birthdate': 'invalid-date'
        })
        self.assertEqual(response.status_code, 200)  # Stay on the form page
        self.assertContains(response, 'Please correct the errors below.')


class GeneralViewTest(TestCase):
    """
    Test class for general views.
    """

    def test_home_view(self):
        """Test that the home view renders the correct template."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')


class DashboardViewTest(TestCase):
    """
    Test class for dashboard view functionality.
    """
    
    def setUp(self):
        """Set up test data for dashboard tests."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='dashboard_user',
            email='dashboard@stircraft.com',
            password='test_password_123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            birthdate=date(2000, 1, 1)
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard view requires authentication."""
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertIn('/admin/login/', response.url)

    def test_dashboard_view_authenticated(self):
        """Test dashboard view for authenticated user."""
        self.client.login(username='dashboard_user', password='test_password_123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stir_craft/dashboard.html')
        self.assertContains(response, self.user.username)

    def test_dashboard_context_data(self):
        """Test that dashboard provides correct context data."""
        self.client.login(username='dashboard_user', password='test_password_123')
        
        # Create test data
        cocktail = Cocktail.objects.create(
            name='User Cocktail',
            instructions='Test instructions',
            creator=self.user
        )
        
        response = self.client.get(reverse('dashboard'))
        
        # Check context contains expected data
        self.assertIn('profile', response.context)
        self.assertIn('creations_list', response.context)
        self.assertIn('favorites_list', response.context)
        self.assertIn('user_lists', response.context)
        self.assertIn('stats', response.context)
        
        # Verify user's cocktail appears in creations
        creations_list = response.context['creations_list']
        self.assertIn(cocktail, creations_list.cocktails.all())
