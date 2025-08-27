"""
Ingredient Processing Utilities

This module provides shared utilities for ingredient-related data processing
across multiple management commands. It consolidates common ingredient operations
to reduce code duplication and ensure consistent behavior.

Key Functions:
- Ingredient classification and categorization
- Alcohol content estimation algorithms
- Duplicate detection and merging
- Name normalization and standardization

Author: StirCraft Development Team
Date: August 2025
Version: 1.0
"""

from typing import Dict, List, Tuple, Optional
from decimal import Decimal
import re
from ..models import Ingredient


class IngredientClassifier:
    """
    Intelligent ingredient classification system.
    
    This class provides methods for automatically categorizing ingredients
    based on their names and properties using pattern matching and
    knowledge-based rules.
    """
    
    # Categorization patterns based on ingredient names
    CATEGORY_PATTERNS = {
        'spirit': [
            r'\b(whiskey|whisky|bourbon|scotch|rye|rum|vodka|gin|tequila|brandy|cognac)\b',
            r'\b(mezcal|absinthe|grappa|schnapps|aquavit|ouzo|sake|soju)\b',
        ],
        'liqueur': [
            r'\b(liqueur|amaretto|baileys|kahlua|cointreau|grand marnier)\b',
            r'\b(sambuca|frangelico|chambord|drambuie|galliano|midori)\b',
            r'\b(triple sec|creme de|schnapps|cordial)\b',
        ],
        'wine': [
            r'\b(wine|champagne|prosecco|cava|sherry|port|vermouth)\b',
            r'\b(madeira|marsala|fino|amontillado|oloroso)\b',
        ],
        'beer': [
            r'\b(beer|ale|lager|stout|porter|pilsner|wheat beer)\b',
            r'\b(ipa|pale ale|amber|bock|hefeweizen)\b',
        ],
        'bitters': [
            r'\b(bitters|angostura|peychaud|orange bitters|aromatic)\b',
            r'\b(campari|aperol|fernet|cynar|amaro)\b',
        ],
        'mixer': [
            r'\b(soda|tonic|ginger ale|club soda|sprite|coke|cola)\b',
            r'\b(juice|nectar|syrup|grenadine|simple syrup)\b',
            r'\b(water|milk|cream|coconut milk|almond milk)\b',
        ],
        'garnish': [
            r'\b(olive|cherry|lemon|lime|orange|mint|basil|rosemary)\b',
            r'\b(twist|peel|wheel|wedge|slice|sprig|leaf)\b',
            r'\b(salt|sugar|rim|celery|pickle|onion)\b',
        ],
    }
    
    # Alcohol content estimation based on ingredient type and name
    ALCOHOL_CONTENT_ESTIMATES = {
        # Spirits (typically 40% ABV)
        'vodka': 40.0, 'gin': 40.0, 'rum': 40.0, 'whiskey': 40.0,
        'bourbon': 45.0, 'scotch': 40.0, 'tequila': 40.0, 'brandy': 40.0,
        
        # Liqueurs (typically 15-30% ABV)
        'amaretto': 28.0, 'kahlua': 20.0, 'baileys': 17.0, 'cointreau': 25.0,
        'triple sec': 25.0, 'grand marnier': 40.0, 'sambuca': 38.0,
        
        # Wines (typically 11-15% ABV)
        'wine': 12.5, 'champagne': 12.0, 'prosecco': 11.0, 'sherry': 15.0,
        'vermouth': 16.0, 'port': 20.0,
        
        # Beers (typically 3-8% ABV)
        'beer': 5.0, 'ale': 5.5, 'lager': 4.5, 'stout': 6.0, 'ipa': 6.5,
        
        # Bitters (typically 35-45% ABV)
        'bitters': 40.0, 'angostura': 44.7, 'campari': 25.0, 'aperol': 11.0,
    }
    
    @classmethod
    def classify_ingredient(cls, ingredient_name: str) -> str:
        """
        Classify an ingredient based on its name using pattern matching.
        
        Algorithm:
        1. Normalize ingredient name (lowercase, remove extra spaces)
        2. Test against each category's regex patterns
        3. Return first matching category
        4. Default to 'other' if no patterns match
        
        Args:
            ingredient_name: Name of the ingredient to classify
            
        Returns:
            str: Category name ('spirit', 'liqueur', 'wine', etc.)
        """
        name_lower = ingredient_name.lower().strip()
        
        for category, patterns in cls.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, name_lower, re.IGNORECASE):
                    return category
        
        return 'other'
    
    @classmethod
    def estimate_alcohol_content(cls, ingredient_name: str, category: str = None) -> Decimal:
        """
        Estimate alcohol content based on ingredient name and category.
        
        Algorithm:
        1. Check for exact name matches in alcohol content database
        2. Use category-based defaults if no exact match
        3. Apply fuzzy matching for common variations
        4. Return 0.0 for non-alcoholic ingredients
        
        Args:
            ingredient_name: Name of the ingredient
            category: Optional ingredient category to refine estimation
            
        Returns:
            Decimal: Estimated alcohol percentage (0.0-100.0)
        """
        name_lower = ingredient_name.lower().strip()
        
        # Check for exact matches first
        for key, abv in cls.ALCOHOL_CONTENT_ESTIMATES.items():
            if key in name_lower:
                return Decimal(str(abv))
        
        # Use category-based estimation
        if not category:
            category = cls.classify_ingredient(ingredient_name)
        
        category_defaults = {
            'spirit': 40.0,
            'liqueur': 25.0,
            'wine': 12.5,
            'beer': 5.0,
            'bitters': 40.0,
            'mixer': 0.0,
            'garnish': 0.0,
            'other': 0.0,
        }
        
        return Decimal(str(category_defaults.get(category, 0.0)))


class IngredientDuplicateDetector:
    """
    Intelligent duplicate detection for ingredients.
    
    This class provides methods for finding and handling duplicate
    ingredients in the database using various matching strategies.
    """
    
    @staticmethod
    def find_duplicates() -> Dict[str, List[Ingredient]]:
        """
        Find potential duplicate ingredients using multiple strategies.
        
        Strategies:
        1. Exact name matches (case-insensitive)
        2. Normalized name matches (removing punctuation, spaces)
        3. Fuzzy matching for common variations
        
        Returns:
            Dict mapping normalized names to lists of potentially duplicate ingredients
        """
        duplicates = {}
        all_ingredients = Ingredient.objects.all()
        
        # Group by normalized name
        for ingredient in all_ingredients:
            normalized_name = IngredientDuplicateDetector.normalize_name(ingredient.name)
            if normalized_name not in duplicates:
                duplicates[normalized_name] = []
            duplicates[normalized_name].append(ingredient)
        
        # Filter to only groups with more than one ingredient
        return {name: ingredients for name, ingredients in duplicates.items() if len(ingredients) > 1}
    
    @staticmethod
    def normalize_name(name: str) -> str:
        """
        Normalize ingredient name for duplicate detection.
        
        Normalization steps:
        1. Convert to lowercase
        2. Remove extra whitespace
        3. Remove common punctuation
        4. Standardize common abbreviations
        
        Args:
            name: Original ingredient name
            
        Returns:
            str: Normalized name for comparison
        """
        normalized = name.lower().strip()
        
        # Remove punctuation and extra spaces
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Standardize common abbreviations
        abbreviations = {
            'oz': 'ounce',
            'ml': 'milliliter',
            'tsp': 'teaspoon',
            'tbsp': 'tablespoon',
            'fl': 'fluid',
        }
        
        for abbrev, full in abbreviations.items():
            normalized = normalized.replace(f' {abbrev} ', f' {full} ')
            normalized = normalized.replace(f' {abbrev}', f' {full}')
        
        return normalized.strip()
    
    @staticmethod
    def merge_ingredients(primary: Ingredient, duplicates: List[Ingredient]) -> None:
        """
        Merge duplicate ingredients into the primary ingredient.
        
        Merge Strategy:
        1. Update all RecipeComponents to use the primary ingredient
        2. Merge tags from all duplicates into primary
        3. Update description if primary has less information
        4. Delete duplicate ingredients
        
        Args:
            primary: Primary ingredient to keep
            duplicates: List of duplicate ingredients to merge into primary
        """
        from ..models import RecipeComponent
        
        for duplicate in duplicates:
            if duplicate.id == primary.id:
                continue
            
            # Update all recipe components to use primary ingredient
            RecipeComponent.objects.filter(ingredient=duplicate).update(ingredient=primary)
            
            # Merge tags
            for tag in duplicate.flavor_tags.all():
                primary.flavor_tags.add(tag)
            
            # Update description if primary has less information
            if len(duplicate.description) > len(primary.description):
                primary.description = duplicate.description
            
            # Update alcohol content if primary is missing it
            if not primary.alcohol_content and duplicate.alcohol_content:
                primary.alcohol_content = duplicate.alcohol_content
            
            # Update ingredient type if primary is 'other'
            if primary.ingredient_type == 'other' and duplicate.ingredient_type != 'other':
                primary.ingredient_type = duplicate.ingredient_type
        
        # Save primary with merged information
        primary.save()
        
        # Delete duplicates
        for duplicate in duplicates:
            if duplicate.id != primary.id:
                duplicate.delete()


class IngredientNormalizer:
    """
    Utilities for normalizing ingredient data.
    
    This class provides methods for standardizing ingredient names,
    units, and other properties for consistency across the database.
    """
    
    @staticmethod
    def standardize_name(name: str) -> str:
        """
        Standardize ingredient name formatting.
        
        Standardization rules:
        1. Proper title case for most words
        2. Keep certain words lowercase (of, and, the, etc.)
        3. Standardize common brand names and terms
        4. Remove unnecessary qualifiers
        
        Args:
            name: Original ingredient name
            
        Returns:
            str: Standardized ingredient name
        """
        # Keep these words lowercase unless they're the first word
        lowercase_words = {'of', 'and', 'the', 'in', 'on', 'at', 'to', 'for', 'with'}
        
        words = name.strip().split()
        standardized_words = []
        
        for i, word in enumerate(words):
            word = word.lower()
            
            # First word is always capitalized
            if i == 0 or word not in lowercase_words:
                word = word.capitalize()
            
            standardized_words.append(word)
        
        return ' '.join(standardized_words)
    
    @staticmethod
    def validate_alcohol_content(alcohol_content: Decimal) -> bool:
        """
        Validate alcohol content value is within reasonable range.
        
        Args:
            alcohol_content: Alcohol percentage to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        return 0 <= alcohol_content <= 100
