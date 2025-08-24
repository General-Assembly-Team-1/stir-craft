# This file contains all the Models for the PostgreSQL database we'll be using in the Stir Craft web/mobile application.  
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from django.core.exceptions import ValidationError
from datetime import date
from decimal import Decimal

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

class Ingredient(models.Model):
    """
    Individual ingredients that can be used in cocktails.
    Examples: Gin, Simple Syrup, Lime Juice, etc.
    
    This model stores all the ingredients that can be used in cocktail recipes.
    Each ingredient has a type, alcohol content, and can be tagged with flavor
    profiles to enable advanced filtering and recipe recommendations.
    """
    
    # Define predefined choices for ingredient categories
    # This ensures data consistency and enables filtering by ingredient type
    INGREDIENT_TYPES = [
        ('spirit', 'Spirit'),           # Base spirits like gin, vodka, whiskey, rum
        ('liqueur', 'Liqueur'),         # Flavored liqueurs, vermouth, amaretto, triple sec
        ('wine', 'Wine'),               # Wine, champagne, sherry, port
        ('beer', 'Beer'),               # Beer, ale, stout
        ('mixer', 'Mixer'),             # Non-alcoholic mixers like juices, water
        ('soda', 'Soda'),               # Carbonated beverages like tonic, coke, seltzer
        ('syrup', 'Syrup'),             # Syrups like simple syrup, grenadine
        ('bitters', 'Bitters'),         # Concentrated flavorings like Angostura
        ('juice', 'Juice'),             # Fresh juices like lime, lemon, orange
        ('dairy', 'Dairy'),             # Cream, milk, egg whites
        ('garnish', 'Garnish'),         # Edible garnishes: lemon wedge, olives, herbs, coffee beans
        ('other', 'Other'),             # Non-edible decorations: umbrellas, flowers, straws
    ]
    
    # Core ingredient information
    name = models.CharField(
        max_length=100, 
        unique=True,  # Prevent duplicate ingredients
        help_text="Name of the ingredient (e.g., 'London Dry Gin')"
    )
    
    ingredient_type = models.CharField(
        max_length=20, 
        choices=INGREDIENT_TYPES,
        help_text="Category of ingredient for filtering and organization"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional detailed description of the ingredient, brand notes, or usage tips"
    )
    
    # Alcohol content with validation
    # This is crucial for calculating cocktail ABV and age verification
    alcohol_content = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Alcohol by volume (ABV) percentage - 0 for non-alcoholic ingredients"
    )
    
    # Use django-taggit for flexible flavor profiling
    # This enables sophisticated recipe matching and recommendations
    # Users can search for "citrusy" or "smoky" cocktails
    flavor_tags = TaggableManager(
        help_text="Flavor notes like citrusy, smoky, sweet, herbal, etc. Used for recipe recommendations",
        blank=True
    )
    
    # Automatic timestamps for tracking when ingredients are added/modified
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this ingredient was first added to the database"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this ingredient was last modified"
    )
    
    def __str__(self):
        """String representation of the ingredient - used in admin and forms."""
        return self.name
    
    def is_alcoholic(self):
        """
        Check if ingredient contains alcohol.
        
        Returns:
            bool: True if alcohol_content > 0, False otherwise
            
        Used for:
        - Age verification warnings
        - Mocktail filtering (non-alcoholic recipes only)
        - Calculating total cocktail ABV
        """
        return self.alcohol_content > 0
    
    class Meta:
        # Default ordering for consistent display in lists and forms
        ordering = ['name']  # Alphabetical order by ingredient name
        
        # Optional: Add verbose names for admin interface
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"


# =============================================================================
# 🍸 VESSEL MODELS
# =============================================================================

class Vessel(models.Model):
    """
    Glassware and serving vessels for cocktails.
    Examples: Martini Glass, Rocks Glass, Coupe, etc.
    
    This model represents different types of drinkware that can be used
    to serve cocktails. Each vessel has physical properties like volume,
    material, and whether it's stemmed, which affects the drinking experience.
    """
    
    # Core vessel information
    name = models.CharField(
        max_length=100,
        help_text="Name of the vessel (e.g., 'Martini Glass', 'Old Fashioned Glass')"
    )
    
    # Physical properties
    volume = models.DecimalField(
        max_digits=10,  # Allows for large volumes with precision
        decimal_places=2,  # Two decimal places for precise measurements
        help_text="Typical capacity of the vessel in milliliters (e.g., '240.00')"
    )
    
    material = models.CharField(
        max_length=100,
        help_text="Material the vessel is made from (e.g., 'Glass', 'Crystal', 'Copper')"
    )
    
    stemmed = models.BooleanField(
        default=False,  # Most glasses are not stemmed
        help_text="Whether the vessel has a stem (affects temperature retention)"
    )
    
    # Timestamp for tracking when vessel was added
    created_on = models.DateTimeField(
        auto_now_add=True,  # Automatically sets timestamp when created
        help_text="When this vessel was added to the database"
    )

    def __str__(self):
        """
        String representation of the vessel.
        Used in admin interface and form dropdowns.
        """
        return self.name
    
    def is_stemmed(self):
        """
        Check if the vessel has a stem.
        
        Returns:
            bool: True if vessel is stemmed, False otherwise
            
        Used for:
        - Serving recommendations (stemmed glasses for chilled cocktails)
        - Temperature control guidance
        - Proper handling instructions
        """
        return self.stemmed
    
    def get_volume_in_oz(self):
        """
        Convert volume from milliliters to fluid ounces.
        
        Returns:
            float: Volume in fluid ounces, rounded to 2 decimal places
            
        Useful for bartenders who work with imperial measurements.
        """
        # 1 fluid ounce = 29.5735 milliliters
        return round(float(self.volume) / 29.5735, 2)
    
    class Meta:
        # Default ordering for consistent display in lists and forms
        ordering = ['name']  # Alphabetical order by vessel name
        
        # Optional: Add verbose names for admin interface
        verbose_name = "Vessel"
        verbose_name_plural = "Vessels"


# =============================================================================
# 🍹 COCKTAIL MODELS
# =============================================================================

class Cocktail(models.Model):
    """
    Main cocktail recipe model containing name, instructions, and metadata.
    Connected to ingredients via RecipeComponent join table.
    """
    
    # Core recipe information
    name = models.CharField(
        max_length=200,  # Maximum length for cocktail name
        help_text="Name of the cocktail (e.g., 'Margarita')"
    )
    description = models.TextField(
        blank=True,  # Description is optional
        help_text="Optional detailed description of the cocktail"
    )
    instructions = models.TextField(
        help_text="Step-by-step preparation instructions"
    )
    
    # Cocktail image (populated from TheCocktailDB or user uploads)
    image = models.ImageField(
        upload_to='cocktails/',
        blank=True,
        null=True,
        help_text="Cocktail image - auto-populated from TheCocktailDB API during seeding"
    )
    
    # Relationships
    creator = models.ForeignKey(
        User,  # Links to the User model
        on_delete=models.CASCADE,  # Deletes cocktail if creator is deleted
        related_name='created_cocktails',  # Allows reverse lookup of cocktails created by a user
        help_text="User who created this cocktail"
    )
    vessel = models.ForeignKey(
        'Vessel',  # Links to the Vessel model
        on_delete=models.SET_NULL,  # Sets vessel to NULL if deleted
        null=True,  # Vessel is optional
        blank=True,  # Allows blank values in forms
        help_text="Glassware or serving vessel for the cocktail"
    )
    ingredients = models.ManyToManyField(
        'Ingredient',  # Links to the Ingredient model
        through='RecipeComponent',  # Specifies the join table
        help_text="Ingredients used in the cocktail"
    )
    forked_from = models.ForeignKey(
        'self',  # Self-referential to Cocktail model
        on_delete=models.SET_NULL,  # Keep the cocktail if original is deleted
        null=True,  # Most cocktails are not forks
        blank=True,  # Optional field
        related_name='forks',  # Allows reverse lookup of forks from original
        help_text="Original cocktail this recipe is based on (if it's a variation)"
    )
    
    # Metadata
    is_alcoholic = models.BooleanField(
        default=True,  # Default value is alcoholic
        help_text="Indicates whether the cocktail contains alcohol"
    )
    
    # Define color choices for consistent filtering
    COLOR_CHOICES = [
        ('Clear', 'Clear'),
        ('White', 'White'),
        ('Yellow', 'Yellow'),
        ('Orange', 'Orange'),
        ('Red', 'Red'),
        ('Pink', 'Pink'),
        ('Purple', 'Purple'),
        ('Blue', 'Blue'),
        ('Green', 'Green'),
        ('Brown', 'Brown'),
        ('Black', 'Black'),
        ('Gold', 'Gold'),
        ('Silver', 'Silver'),
        ('Cream', 'Cream'),
        ('Amber', 'Amber'),
    ]
    
    color = models.CharField(
        max_length=20,  # Maximum length for color description
        choices=COLOR_CHOICES,
        default='Clear',  # Default color when none specified
        blank=True,  # Color is optional for user input
        help_text="Cocktail color for filtering and visual identification"
    )
    image = models.ImageField(
        upload_to='cocktails/',
        blank=True,
        null=True,
        help_text="Cocktail image - auto-populated from TheCocktailDB or user-uploaded"
    )
    
    # Attribution for recipe sourcing
    attribution_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Attribution text for recipe source (e.g., 'Original recipe by...', 'Adapted from...')"
    )
    attribution_url = models.URLField(
        blank=True,
        help_text="URL to the original recipe or source"
    )
    
    # Tagging for vibes and categories
    vibe_tags = TaggableManager(
        help_text="Tags for vibes like tropical, cozy, party, etc.",
        blank=True  # Tags are optional
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,  # Automatically sets timestamp when created
        help_text="Timestamp when the cocktail was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,  # Automatically updates timestamp when modified
        help_text="Timestamp when the cocktail was last updated"
    )
    
    def __str__(self):
        """
        String representation of the cocktail.
        Used in admin interface and debugging.
        """
        return self.name
    
    def get_total_volume(self):
        """
        Calculate total volume of all ingredients.
        Iterates through RecipeComponent objects linked to this cocktail.
        """
        total_volume = sum(
            float(rc.amount) for rc in self.components.all()
            if rc.amount  # Ensures amount is not None
        )
        return total_volume
    
    def get_alcohol_content(self):
        """
        Calculate the approximate alcohol content (ABV) of the cocktail.
        This is a weighted average based on the alcohol content and volume of each ingredient.
        """
        total_alcohol_volume = 0
        total_volume = 0
        
        for component in self.components.all():
            if component.ingredient.alcohol_content > 0:
                # Convert amount to consistent units (assume ml)
                volume = component.amount
                alcohol_volume = volume * (Decimal(str(component.ingredient.alcohol_content)) / Decimal('100'))
                total_alcohol_volume += alcohol_volume
                total_volume += volume
            else:
                total_volume += component.amount
        
        if total_volume > 0:
            percentage = (total_alcohol_volume / total_volume) * Decimal('100')
            return float(round(percentage, 2))
        return 0.0
    
    def get_popularity_stats(self):
        """
        Get popularity statistics for this cocktail.
        Returns a dictionary with various popularity metrics.
        """
        from django.db.models import Count
        
        # Count how many users have this in their favorites
        favorites_count = List.objects.filter(
            list_type='favorites',
            cocktails=self
        ).count()
        
        # Count how many custom lists contain this cocktail
        custom_lists_count = List.objects.filter(
            list_type='custom',
            cocktails=self
        ).count()
        
        # Count total appearances across all lists
        total_lists_count = List.objects.filter(
            cocktails=self
        ).count()
        
        # Get list of custom list names (for display)
        custom_list_names = List.objects.filter(
            list_type='custom',
            cocktails=self
        ).values_list('name', flat=True)[:5]  # Limit to first 5 for display
        
        return {
            'favorites_count': favorites_count,
            'custom_lists_count': custom_lists_count,
            'total_lists_count': total_lists_count,
            'custom_list_names': list(custom_list_names),
            'has_more_lists': custom_lists_count > 5,
        }
    
    def get_image_url(self):
        """
        Get the URL for the cocktail image, with fallback handling.
        
        Returns:
            str: URL to the cocktail image or None if no image exists
        """
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return None
    
    def has_image(self):
        """
        Check if the cocktail has an associated image.
        
        Returns:
            bool: True if cocktail has an image, False otherwise
        """
        return bool(self.image and hasattr(self.image, 'url'))
    
    class Meta:
        ordering = ['-created_at']  # Orders cocktails by creation date (newest first)
        unique_together = ['name', 'creator']  # Ensures unique cocktail names per creator 

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
    
    cocktail = models.ForeignKey(
        'Cocktail',  # Links to the Cocktail model
        on_delete=models.CASCADE,  # Deletes RecipeComponent if cocktail is deleted
        related_name='components',  # Allows reverse lookup of components in a cocktail
        help_text="Cocktail this ingredient belongs to"
    )
    ingredient = models.ForeignKey(
        'Ingredient',  # Links to the Ingredient model
        on_delete=models.CASCADE,  # Deletes RecipeComponent if ingredient is deleted
        help_text="Ingredient used in the cocktail"
    )
    
    amount = models.DecimalField(
        max_digits=5,  # Maximum digits for amount
        decimal_places=2,  # Allows up to two decimal places
        help_text="Amount of ingredient (e.g., '30.00')"
    )
    unit = models.CharField(
        max_length=20,  # Maximum length for unit description
        choices=UNIT_CHOICES,  # Restricts to predefined unit choices
        help_text="Unit of measurement (e.g., 'ml', 'oz')"
    )
    preparation_note = models.CharField(
        max_length=200,  # Maximum length for preparation notes
        blank=True,  # Notes are optional
        help_text="Optional preparation notes (e.g., 'muddled', 'expressed')"
    )
    order = models.PositiveIntegerField(
        default=0,  # Default order is 0 (first)
        help_text="Order of addition (0 = first)"
    )
    
    @property
    def non_alcoholic(self):
        """
        Returns True if this ingredient contains no alcohol (ABV = 0).
        """
        return self.ingredient.alcohol_content == 0
    
    def get_display_amount(self):
        """
        Returns the amount with proper unit conversion and formatting.
        - Converts mL to ounces for display (quarters only)
        - Uses teaspoons for very small amounts
        - Maintains semantic units (dash, splash) for special measurements
        """
        # Non-standard units that should be displayed as-is
        non_standard_units = ['dash', 'splash', 'pinch', 'piece', 'slice', 'wedge', 'sprig']
        
        if self.unit in non_standard_units:
            # Display as whole number for non-standard units
            if self.amount == int(self.amount):
                return f"{int(self.amount)} {self.get_unit_display()}"
            else:
                return f"{self.amount} {self.get_unit_display()}"
        
        # Convert mL to ounces for display (1 oz = 29.5735 mL)
        if self.unit == 'ml':
            oz_amount = float(self.amount) / 29.5735
            
            # For very small amounts (less than 0.33 oz / ~10 mL), use teaspoons
            if oz_amount < 0.33:
                tsp_amount = float(self.amount) / 4.92892  # 1 tsp = 4.92892 mL
                if tsp_amount <= 0.5:
                    return "1/2 tsp"
                elif tsp_amount <= 1:
                    return "1 tsp"
                elif tsp_amount <= 1.5:
                    return "1 1/2 tsp"
                elif tsp_amount <= 2:
                    return "2 tsp"
                else:
                    return f"{tsp_amount:.1f} tsp"
            
            # Round to nearest quarter ounce for larger amounts
            quarter_oz = round(oz_amount * 4) / 4
            
            # Format quarters nicely
            if quarter_oz == int(quarter_oz):
                return f"{int(quarter_oz)} oz"
            elif quarter_oz == int(quarter_oz) + 0.25:
                if int(quarter_oz) == 0:
                    return "1/4 oz"
                else:
                    return f"{int(quarter_oz)} 1/4 oz"
            elif quarter_oz == int(quarter_oz) + 0.5:
                if int(quarter_oz) == 0:
                    return "1/2 oz"
                else:
                    return f"{int(quarter_oz)} 1/2 oz"
            elif quarter_oz == int(quarter_oz) + 0.75:
                if int(quarter_oz) == 0:
                    return "3/4 oz"
                else:
                    return f"{int(quarter_oz)} 3/4 oz"
            else:
                # Fallback to single decimal
                return f"{quarter_oz:.1f} oz"
        
        # For teaspoons stored as tsp, display nicely
        if self.unit == 'tsp':
            amount = float(self.amount)
            if amount == 0.5:
                return "1/2 tsp"
            elif amount == 1.5:
                return "1 1/2 tsp"
            elif amount == int(amount):
                return f"{int(amount)} tsp"
            else:
                return f"{amount} tsp"
        
        # For other standard units, display as-is with proper formatting
        if self.amount == int(self.amount):
            return f"{int(self.amount)} {self.get_unit_display()}"
        else:
            return f"{self.amount} {self.get_unit_display()}"
    
    def get_storage_amount_ml(self):
        """
        Converts the amount to mL for consistent storage.
        Returns the amount in mL regardless of input unit.
        """
        conversion_factors = {
            'oz': 29.5735,
            'ml': 1,
            'tsp': 4.92892,
            'tbsp': 14.7868,
            # Non-standard units are stored as-is (not converted)
            'dash': 1,
            'splash': 1,
            'pinch': 1,
            'piece': 1,
            'slice': 1,
            'wedge': 1,
            'sprig': 1,
        }
        
        factor = conversion_factors.get(self.unit, 1)
        return float(self.amount) * factor
    
    @classmethod
    def create_standardized(cls, cocktail, ingredient, amount, unit, **kwargs):
        """
        Creates a RecipeComponent with standardized unit storage.
        Converts input units to mL for storage when appropriate.
        """
        # Units that should be converted to mL for storage
        convertible_units = ['oz', 'tsp', 'tbsp']
        
        if unit in convertible_units:
            # Convert to mL and store as mL
            conversion_factors = {
                'oz': 29.5735,
                'tsp': 4.92892,
                'tbsp': 14.7868,
            }
            ml_amount = float(amount) * conversion_factors[unit]
            storage_unit = 'ml'
            storage_amount = round(ml_amount, 2)
        else:
            # Store as-is for non-standard units
            storage_unit = unit
            storage_amount = amount
        
        return cls.objects.create(
            cocktail=cocktail,
            ingredient=ingredient,
            amount=storage_amount,
            unit=storage_unit,
            **kwargs
        )
    
    def __str__(self):
        """
        String representation of the RecipeComponent.
        Used in admin interface and debugging.
        """
        return f"{self.amount} {self.unit} {self.ingredient.name} in {self.cocktail.name}"
    
    class Meta:
        ordering = ['order', 'ingredient__name']  # Orders components by addition order and ingredient name
        unique_together = ['cocktail', 'ingredient']  # Prevents duplicate ingredients in a cocktail


# =============================================================================
# 📁 LIST MODELS
# =============================================================================

class List(models.Model):
    """
    User-created collections of cocktails.
    Examples: "Favorites", "Summer Favorites", "Date Night Drinks", "Low-ABV Options"
    
    Special lists:
    - "Your Creations": Auto-generated, edit-locked list containing all user's cocktails
    - "Favorites": Default list for favorited cocktails
    """
    
    # List types for different behaviors
    LIST_TYPES = [
        ('custom', 'Custom List'),
        ('favorites', 'Favorites List'),
        ('creations', 'Your Creations List'),
    ]
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_lists')
    cocktails = models.ManyToManyField('Cocktail', blank=True, related_name='in_lists')
    
    # New fields for special list behavior
    list_type = models.CharField(
        max_length=20, 
        choices=LIST_TYPES, 
        default='custom',
        help_text="Type of list - determines editing permissions and behavior"
    )
    is_editable = models.BooleanField(
        default=True,
        help_text="Whether users can edit this list (False for auto-generated lists)"
    )
    is_deletable = models.BooleanField(
        default=True,
        help_text="Whether users can delete this list (False for system lists)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} by {self.creator.username}"

    def cocktail_count(self):
        """Return number of cocktails in this list."""
        return self.cocktails.count()

    def is_system_list(self):
        """Check if this is a system-managed list."""
        return self.list_type in ['favorites', 'creations']

    def sync_creations_list(self):
        """
        For 'creations' type lists, sync with all cocktails created by the user.
        This ensures the list always contains all user's cocktails.
        """
        if self.list_type == 'creations':
            # Get all cocktails created by this user
            user_cocktails = Cocktail.objects.filter(creator=self.creator)
            # Clear current cocktails and add all user's cocktails
            self.cocktails.set(user_cocktails)

    @staticmethod
    def create_default_lists(user):
        """Create default lists for a new user."""
        # Create "Your Creations" list (edit-locked)
        creations_list, created = List.objects.get_or_create(
            creator=user,
            list_type='creations',
            defaults={
                'name': "Your Creations",
                'description': "All cocktails you've created - automatically updated",
                'is_editable': False,
                'is_deletable': False
            }
        )
        
        # Create "Favorites" list (editable)
        favorites_list, created = List.objects.get_or_create(
            creator=user,
            list_type='favorites',
            defaults={
                'name': "Favorites",
                'description': "Your favorite recipes",
                'is_editable': True,
                'is_deletable': False
            }
        )
        
        return creations_list, favorites_list

    @staticmethod
    def get_or_create_creations_list(user):
        """Get or create the 'Your Creations' list for a user."""
        creations_list, created = List.objects.get_or_create(
            creator=user,
            list_type='creations',
            defaults={
                'name': "Your Creations",
                'description': "All cocktails you've created - automatically updated",
                'is_editable': False,
                'is_deletable': False
            }
        )
        
        if created or True:  # Always sync to ensure it's up to date
            creations_list.sync_creations_list()
        
        return creations_list

    @staticmethod  
    def get_or_create_favorites_list(user):
        """Get or create the 'Favorites' list for a user."""
        favorites_list, created = List.objects.get_or_create(
            creator=user,
            list_type='favorites',
            defaults={
                'name': "Favorites", 
                'description': "Your favorite recipes",
                'is_editable': True,
                'is_deletable': False
            }
        )
        return favorites_list

    class Meta:
        ordering = ['-updated_at']
        # Allow same name for different creators
        unique_together = [
            ['name', 'creator'],  # Each user can have unique list names
        ]
        constraints = [
            # Each user can only have one favorites list and one creations list
            models.UniqueConstraint(
                fields=['creator', 'list_type'],
                condition=models.Q(list_type__in=['favorites', 'creations']),
                name='unique_system_lists_per_user'
            )
        ] 


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


# =============================================================================
# 🔄 DJANGO SIGNALS FOR AUTO-UPDATING LISTS
# =============================================================================

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver(post_save, sender=Cocktail)
def update_creations_list_on_cocktail_save(sender, instance, created, **kwargs):
    """
    Automatically update the user's 'Your Creations' list when they create or update a cocktail.
    """
    creations_list = List.get_or_create_creations_list(instance.creator)
    creations_list.sync_creations_list()

@receiver(post_delete, sender=Cocktail)
def update_creations_list_on_cocktail_delete(sender, instance, **kwargs):
    """
    Automatically update the user's 'Your Creations' list when they delete a cocktail.
    """
    try:
        creations_list = List.objects.get(creator=instance.creator, list_type='creations')
        creations_list.sync_creations_list()
    except List.DoesNotExist:
        pass  # List doesn't exist, nothing to update

@receiver(post_save, sender=User)
def create_default_lists_for_new_user(sender, instance, created, **kwargs):
    """
    Automatically create default lists (Favorites and Your Creations) for new users.
    """
    if created:
        List.create_default_lists(instance)