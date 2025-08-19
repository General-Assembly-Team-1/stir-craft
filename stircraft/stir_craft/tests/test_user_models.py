from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from ..models import Profile, List, Cocktail
from datetime import date


class ProfileModelTest(TestCase):
    """
    Test class for Profile model functionality.
    """
    
    def setUp(self):
        self.user = User.objects.create(username="testuser")

    def test_profile_age_validation(self):
        """Test that ValidationError is raised for users under 21."""
        profile = Profile(user=self.user, birthdate=date(2010, 8, 10))
        with self.assertRaises(ValidationError):
            profile.clean()

    def test_profile_valid_age(self):
        """Test that no ValidationError is raised for users 21 or older."""
        profile = Profile(user=self.user, birthdate=date(2000, 8, 10))
        try:
            profile.clean()
        except ValidationError:
            self.fail("ValidationError raised for valid age.")


class ListModelTest(TestCase):
    """
    Test class for List model functionality including enhanced features.
    """
    
    def setUp(self):
        self.test_user = User.objects.create_user(
            username='list_test_user',
            email='listtest@stircraft.com',
            password='test_password_123'
        )
    
    def test_list_creation(self):
        """Test basic list creation."""
        test_list = List.objects.create(
            name="My Custom List",
            creator=self.test_user,
            list_type='custom',
            is_editable=True,
            is_deletable=True
        )
        self.assertEqual(test_list.name, "My Custom List")
        self.assertEqual(test_list.creator, self.test_user)
        self.assertEqual(test_list.list_type, 'custom')
        self.assertTrue(test_list.is_editable)
        self.assertTrue(test_list.is_deletable)

    def test_auto_managed_lists_creation(self):
        """Test creation of auto-managed lists (favorites and creations)."""
        favorites = List.get_or_create_favorites_list(self.test_user)
        self.assertEqual(favorites.list_type, 'favorites')
        self.assertEqual(favorites.creator, self.test_user)
        self.assertTrue(favorites.is_editable)
        self.assertFalse(favorites.is_deletable)
        
        creations = List.get_or_create_creations_list(self.test_user)
        self.assertEqual(creations.list_type, 'creations')
        self.assertEqual(creations.creator, self.test_user)
        self.assertFalse(creations.is_editable)
        self.assertFalse(creations.is_deletable)

    def test_default_lists_creation(self):
        """Test that default lists are created for new users."""
        new_user = User.objects.create_user(
            username='new_user',
            email='new@stircraft.com',
            password='password123'
        )
        
        List.create_default_lists(new_user)
        
        favorites = List.objects.get(creator=new_user, list_type='favorites')
        creations = List.objects.get(creator=new_user, list_type='creations')
        
        self.assertEqual(favorites.name, 'Favorites')
        self.assertEqual(creations.name, 'Your Creations')

    def test_creations_list_sync(self):
        """Test that creations list automatically syncs with user's cocktails."""
        creations_list = List.get_or_create_creations_list(self.test_user)
        
        # Create a cocktail
        cocktail = Cocktail.objects.create(
            name='Test Sync Cocktail',
            instructions='Test instructions',
            creator=self.test_user
        )
        
        # Manually sync (in production this happens via signals)
        creations_list.sync_creations_list()
        
        # Verify cocktail was added to creations list
        self.assertIn(cocktail, creations_list.cocktails.all())

    def test_list_unique_constraints(self):
        """Test that list unique constraints work correctly."""
        # Create first list
        List.objects.create(
            name="Test List",
            creator=self.test_user,
            list_type='custom'
        )
        
        # Try to create duplicate (same name, same creator)
        with self.assertRaises(IntegrityError):
            List.objects.create(
                name="Test List",
                creator=self.test_user,
                list_type='custom'
            )

    def test_list_type_constraints(self):
        """Test that users can only have one list of each auto-managed type."""
        # Create favorites list
        List.objects.create(
            name="Favorites",
            creator=self.test_user,
            list_type='favorites'
        )
        
        # Try to create another favorites list
        with self.assertRaises(IntegrityError):
            List.objects.create(
                name="More Favorites",
                creator=self.test_user,
                list_type='favorites'
            )
