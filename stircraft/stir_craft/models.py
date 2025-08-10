# This file contains all the Models for the PostgreSQL database we'll be using in the Stir Craft web/mobile application.  
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from django.core.exceptions import ValidationError
from datetime import date

# =============================================================================
# 👤 USER & PROFILE MODELS
# =============================================================================

class Profile(models.Model):
    """
    Extended user profile model with additional user information.
    One-to-one relationship with Django's built-in User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True, help_text="Enter your birthdate (must be 21 or older)")
    location = models.CharField(max_length=10, blank=True, help_text="Enter your zip code")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

    def clean(self):
        """Ensure user is 21 or older."""
        if self.birthdate:
            today = date.today()
            age = today.year - self.birthdate.year - ((today.month, today.day) < (self.birthdate.month, self.birthdate.day))
            if age < 21:
                raise ValidationError("You must be at least 21 years old to join.")


# =============================================================================
# 🧂 INGREDIENT MODELS
# =============================================================================

# TODO: Implement Ingredient model
# class Ingredient(models.Model):
#     """
#     Individual ingredients that can be used in cocktails.
#     Examples: Gin, Simple Syrup, Lime Juice, etc.
#     """
#     INGREDIENT_TYPES = [
#         ('spirit', 'Spirit'),
#         ('liqueur', 'Liqueur'),
#         ('mixer', 'Mixer'),
#         ('syrup', 'Syrup'),
#         ('bitters', 'Bitters'),
#         ('juice', 'Juice'),
#         ('garnish', 'Garnish'),
#         ('other', 'Other'),
#     ]
#     
#     name = models.CharField(max_length=100, unique=True)
#     ingredient_type = models.CharField(max_length=20, choices=INGREDIENT_TYPES)
#     description = models.TextField(blank=True)
#     alcohol_content = models.FloatField(
#         default=0.0,
#         validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
#         help_text="Alcohol by volume (ABV) percentage"
#     )
#     
#     # Use django-taggit for flavor profiles
#     flavor_tags = TaggableManager(
#         help_text="Flavor notes like citrusy, smoky, sweet, etc.",
#         blank=True
#     )
#     
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return self.name
#     
#     def is_alcoholic(self):
#         """Check if ingredient contains alcohol."""
#         return self.alcohol_content > 0
#     
#     class Meta:
#         ordering = ['name']


# =============================================================================
# 🍸 VESSEL MODELS
# =============================================================================

# TODO: Implement Vessel model
# class Vessel(models.Model):
#     """
#     Glassware and serving vessels for cocktails.
#     Examples: Martini Glass, Rocks Glass, Coupe, etc.
#     """
#     name = models.CharField(max_length=100, unique=True)
#     description = models.TextField(blank=True)
#     capacity_ml = models.IntegerField(
#         null=True, 
#         blank=True,
#         help_text="Typical capacity in milliliters"
#     )
#     image = models.ImageField(upload_to='vessels/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     
#     def __str__(self):
#         return self.name
#     
#     class Meta:
#         ordering = ['name']


# =============================================================================
# 🍹 COCKTAIL MODELS
# =============================================================================

# TODO: Implement Cocktail model
# class Cocktail(models.Model):
#     """
#     Main cocktail recipe model containing name, instructions, and metadata.
#     Connected to ingredients via RecipeComponent join table.
#     """
#     DIFFICULTY_CHOICES = [
#         ('easy', 'Easy'),
#         ('medium', 'Medium'),
#         ('hard', 'Hard'),
#     ]
#     
#     name = models.CharField(max_length=200)
#     description = models.TextField(blank=True)
#     instructions = models.TextField(help_text="Step-by-step preparation instructions")
#     
#     # Relationships
#     creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_cocktails')
#     vessel = models.ForeignKey('Vessel', on_delete=models.SET_NULL, null=True, blank=True)
#     ingredients = models.ManyToManyField('Ingredient', through='RecipeComponent')
#     
#     # Metadata
#     difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='easy')
#     prep_time_minutes = models.IntegerField(default=5, help_text="Preparation time in minutes")
#     is_alcoholic = models.BooleanField(default=True)
#     color = models.CharField(max_length=20, blank=True, help_text="Cocktail color for filtering")
#     
#     # Tagging for vibes and categories
#     vibe_tags = TaggableManager(
#         help_text="Vibes like tropical, cozy, party, etc.",
#         blank=True
#     )
#     
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return self.name
#     
#     def get_total_volume(self):
#         """Calculate total volume of all ingredients."""
#         # Implementation will sum all RecipeComponent amounts
#         pass
#     
#     def get_alcohol_content(self):
#         """Calculate estimated ABV of the cocktail."""
#         # Implementation will calculate weighted average ABV
#         pass
#     
#     class Meta:
#         ordering = ['-created_at']
#         unique_together = ['name', 'creator']  # Allow same name for different creators


class RecipeComponent(models.Model):
    """
    Join table connecting Cocktails to Ingredients with amount/unit information.
    Enables precise recipe measurements and optional preparation notes.
    """
    UNIT_CHOICES = [
        ('oz', 'Ounces'),
        ('ml', 'Milliliters'),
        ('tsp', 'Teaspoon'),
        ('tbsp', 'Tablespoon'),
        ('dash', 'Dash'),
        ('splash', 'Splash'),
        ('pinch', 'Pinch'),
        ('piece', 'Piece'),
        ('slice', 'Slice'),
        ('wedge', 'Wedge'),
        ('sprig', 'Sprig'),
    ]
    
    cocktail = models.ForeignKey('Cocktail', on_delete=models.CASCADE, related_name='components')
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)
    
    amount = models.DecimalField(max_digits=5, decimal_places=2, help_text="Amount of ingredient")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    preparation_note = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Optional preparation notes (e.g., 'muddled', 'expressed')"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order of addition (0 = first)"
    )
    
    @property
    def non_alcoholic(self):
        """Returns True if this ingredient contains no alcohol (ABV = 0)."""
        return self.ingredient.alcohol_content == 0
    
    def __str__(self):
        return f"{self.amount} {self.unit} {self.ingredient.name} in {self.cocktail.name}"
    
    class Meta:
        ordering = ['order', 'ingredient__name']
        unique_together = ['cocktail', 'ingredient']  # Prevent duplicate ingredients


# =============================================================================
# 📁 LIST MODELS
# =============================================================================

# TODO: Implement List model
# class List(models.Model):
#     """
#     User-created collections of cocktails.
#     Examples: "Summer Favorites", "Date Night Drinks", "Low-ABV Options"
#     """
#     VISIBILITY_CHOICES = [
#         ('private', 'Private'),
#         ('public', 'Public'),
#         ('friends', 'Friends Only'),
#     ]
#     
#     name = models.CharField(max_length=100)
#     description = models.TextField(blank=True)
#     creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_lists')
#     cocktails = models.ManyToManyField('Cocktail', blank=True, related_name='in_lists')
#     
#     visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='private')
#     is_featured = models.BooleanField(default=False, help_text="Admin-curated featured list")
#     
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     
#     def __str__(self):
#         return f"{self.name} by {self.creator.username}"
#     
#     def cocktail_count(self):
#         """Return number of cocktails in this list."""
#         return self.cocktails.count()
#     
#     class Meta:
#         ordering = ['-updated_at']
#         unique_together = ['name', 'creator']  # Allow same name for different creators


# =============================================================================
# 🏆 FUTURE MODELS (Stretch Goals)
# =============================================================================

# TODO: Future - Rating/Review system
# class CocktailRating(models.Model):
#     """User ratings and reviews for cocktails."""
#     cocktail = models.ForeignKey('Cocktail', on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
#     review = models.TextField(blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

# TODO: Future - User following system
# class UserFollow(models.Model):
#     """User following relationships."""
#     follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
#     following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
#     created_at = models.DateTimeField(auto_now_add=True)

# TODO: Future - Recipe forking/remixing
# class CocktailFork(models.Model):
#     """Track when users remix/fork existing recipes."""
#     original = models.ForeignKey('Cocktail', on_delete=models.CASCADE, related_name='forks')
#     forked = models.ForeignKey('Cocktail', on_delete=models.CASCADE, related_name='forked_from')
#     created_at = models.DateTimeField(auto_now_add=True)