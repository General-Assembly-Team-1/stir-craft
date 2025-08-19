"""
Test utilities and helper functions for the StirCraft test suite.

This module provides common functionality that can be shared across
different test modules to reduce code duplication and ensure consistency.
"""

from django.contrib.auth.models import User
from ..models import Ingredient, Cocktail, RecipeComponent, Vessel, Profile
from datetime import date


class TestHelpers:
    """
    Utility class with helper methods for creating test data.
    
    These methods can be used across different test classes to create
    consistent test objects with realistic data.
    """
    
    @staticmethod
    def create_test_user(username="testuser", email="test@stircraft.com", password="testpass123"):
        """
        Helper method to create test users with default values.
        """
        return User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
    
    @staticmethod
    def create_test_profile(user, birthdate=None):
        """
        Helper method to create test profiles.
        """
        if birthdate is None:
            birthdate = date(2000, 1, 1)  # Default to valid age
        
        return Profile.objects.create(
            user=user,
            birthdate=birthdate
        )
    
    @staticmethod
    def create_test_ingredient(name="Test Ingredient", ingredient_type="spirit", alcohol_content=40.0):
        """
        Helper method to create test ingredients with default values.
        Makes tests more readable and reduces code duplication.
        """
        return Ingredient.objects.create(
            name=name,
            ingredient_type=ingredient_type,
            alcohol_content=alcohol_content
        )
    
    @staticmethod
    def create_test_vessel(name="Test Glass", volume=200.0, material="Glass", stemmed=False):
        """
        Helper method to create test vessels with sensible defaults.
        """
        return Vessel.objects.create(
            name=name,
            volume=volume,
            material=material,
            stemmed=stemmed
        )
    
    @staticmethod
    def create_test_cocktail(name="Test Cocktail", creator=None, instructions="Mix and serve"):
        """
        Helper method to create test cocktails with sensible defaults.
        """
        if creator is None:
            creator = TestHelpers.create_test_user()
        
        return Cocktail.objects.create(
            name=name,
            instructions=instructions,
            creator=creator
        )
    
    @staticmethod
    def create_test_recipe_component(cocktail=None, ingredient=None, amount=50.0, unit="ml"):
        """
        Helper method to create test recipe components.
        """
        if cocktail is None:
            cocktail = TestHelpers.create_test_cocktail()
        if ingredient is None:
            ingredient = TestHelpers.create_test_ingredient()
        
        return RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=ingredient,
            amount=amount,
            unit=unit
        )

    @staticmethod
    def create_complete_test_cocktail(name="Complete Test Cocktail", creator=None):
        """
        Helper method to create a complete cocktail with ingredients.
        Returns both the cocktail and a list of its components.
        """
        if creator is None:
            creator = TestHelpers.create_test_user()
        
        cocktail = Cocktail.objects.create(
            name=name,
            instructions="Shake with ice and strain",
            creator=creator,
            is_alcoholic=True
        )
        
        # Add some standard ingredients
        vodka = TestHelpers.create_test_ingredient("Vodka", "spirit", 40.0)
        juice = TestHelpers.create_test_ingredient("Orange Juice", "juice", 0.0)
        
        component1 = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=vodka,
            amount=50.0,
            unit="ml",
            order=1
        )
        
        component2 = RecipeComponent.objects.create(
            cocktail=cocktail,
            ingredient=juice,
            amount=100.0,
            unit="ml",
            order=2
        )
        
        return cocktail, [component1, component2]


class TestConstants:
    """
    Constants used in tests for consistency.
    """
    
    # Valid test dates
    VALID_BIRTHDATE = date(2000, 1, 1)
    INVALID_BIRTHDATE_TOO_YOUNG = date(2010, 1, 1)
    
    # Common ingredient types
    INGREDIENT_TYPES = {
        'SPIRIT': 'spirit',
        'LIQUEUR': 'liqueur',
        'JUICE': 'juice',
        'GARNISH': 'garnish',
        'MIXER': 'mixer'
    }
    
    # Common units
    UNITS = {
        'ML': 'ml',
        'OZ': 'oz',
        'TSP': 'tsp',
        'TBSP': 'tbsp',
        'DASH': 'dash',
        'PIECE': 'piece'
    }
    
    # Test user credentials
    TEST_USER_PASSWORD = 'secure_test_password_123'
    
    # Form validation messages (update these to match your actual form messages)
    FORM_ERROR_MESSAGES = {
        'REQUIRED_FIELD': 'This field is required.',
        'INVALID_EMAIL': 'Enter a valid email address.',
        'PASSWORD_MISMATCH': 'The two password fields didn\'t match.',
        'AGE_VALIDATION': 'You must be at least 21 years old to register.'
    }
