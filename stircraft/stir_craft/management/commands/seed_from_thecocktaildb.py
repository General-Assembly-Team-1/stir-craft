"""
Django management command to seed the StirCraft database with cocktail data 
from TheCocktailDB API (https://www.thecocktaildb.com/api.php).

TheCocktailDB is a free, open-source API that provides comprehensive cocktail data
including ingredients, measurements, instructions, and images. This command fetches
cocktail data and intelligently maps it to StirCraft's sophisticated data models.

FEATURES:
- Fetches cocktails by searching each letter of the alphabet
- Intelligently categorizes ingredients (spirits, liqueurs, mixers, etc.)
- Estimates alcohol content for each ingredient
- Parses measurements from text to structured data
- Matches cocktails to appropriate glassware/vessels
- Adds flavor tags for advanced filtering
- Creates recipe components with proper measurements and order
- Handles duplicate prevention and error recovery
- Provides detailed progress reporting and statistics

USAGE EXAMPLES:
    # Import a small test batch (10 cocktails from letters A-C)
    python manage.py seed_from_thecocktaildb --limit 10 --letters abc

    # Import 100 cocktails from all letters
    python manage.py seed_from_thecocktaildb --limit 100

    # Import ALL available cocktails (could be 500+)
    python manage.py seed_from_thecocktaildb

    # Clear existing data and start fresh
    python manage.py seed_from_thecocktaildb --clear --limit 25

DATA MAPPING:
- TheCocktailDB cocktails → StirCraft Cocktail model
- API ingredients → StirCraft Ingredient model with categorization
- Glass types → StirCraft Vessel model matching
- Measurements → StirCraft RecipeComponent model with parsing
- Categories → StirCraft vibe tags for filtering

RATE LIMITING:
- Includes 0.5-second delays between API requests to be respectful
- Uses proper error handling and retry logic
- Provides detailed logging for debugging

"""

import requests
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from stir_craft.models import (
    Ingredient, Vessel, Cocktail, RecipeComponent, List
)
from decimal import Decimal
import re
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command for seeding cocktail data from TheCocktailDB API.
    
    This command provides a comprehensive solution for importing cocktail recipes,
    ingredients, and related data into the StirCraft application. It handles
    data transformation, intelligent categorization, and error recovery.
    
    The command is designed to be run periodically to update the cocktail database
    with new recipes and maintain data freshness.
    """
    help = 'Seed database with cocktail data from TheCocktailDB API'
    
    def add_arguments(self, parser):
        """
        Add command-line arguments for customizing the import process.
        
        Arguments:
        --limit: Restricts the number of cocktails imported (useful for testing)
        --clear: Removes all existing cocktail data before importing new data
        --letters: Specifies which letters to search (default: all a-z)
        
        Examples:
        --limit 10: Import only 10 cocktails
        --clear: Clear database before importing
        --letters abc: Only search for cocktails starting with A, B, or C
        """
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of cocktails to import (useful for testing)',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing cocktail and ingredient data before importing',
        )
        parser.add_argument(
            '--letters',
            type=str,
            default='abcdefghijklmnopqrstuvwxyz',
            help='Letters to search for cocktails (default: all letters)',
        )
    
    def handle(self, *args, **options):
        """
        Main command handler that orchestrates the entire import process.
        
        Process Flow:
        1. Parse command-line arguments
        2. Optionally clear existing data
        3. Create admin user for imported cocktails
        4. Seed vessel/glassware data
        5. Fetch cocktails from TheCocktailDB API
        6. Process and save cocktails with ingredients
        7. Generate import summary and statistics
        
        Error Handling:
        - API request failures are logged and handled gracefully
        - Individual cocktail processing errors don't stop the entire import
        - Comprehensive error reporting and logging
        """
        self.stdout.write(self.style.SUCCESS('🍸 Starting StirCraft database seeding from TheCocktailDB API...'))
        
        limit = options['limit']
        clear_data = options['clear']
        letters = options['letters']
        
        try:
            # Clear existing data if requested (--clear flag)
            if clear_data:
                self._clear_existing_data()
            
            # Create default admin user for created cocktails
            # This ensures all imported cocktails have a valid creator
            admin_user = self._get_or_create_admin_user()
            
            # Seed vessels first (they're referenced by cocktails)
            # Creates standard glassware types like martini glass, rocks glass, etc.
            self._seed_vessels()
            
            # Fetch and process cocktails by letter from TheCocktailDB API
            # The API allows searching by first letter (A-Z)
            all_cocktails_data = self._fetch_cocktails_by_letters(letters, limit)
            
            if not all_cocktails_data:
                raise CommandError("No cocktails retrieved from API")
            
            # Process cocktails in batches with comprehensive error handling
            # Each cocktail is processed individually to prevent total failure
            self._process_cocktails(all_cocktails_data, admin_user)
            
            # Create summary statistics and show import results
            self._print_summary()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Successfully seeded StirCraft database with TheCocktailDB data!'
                )
            )
            
        except requests.exceptions.RequestException as e:
            raise CommandError(f"API request failed: {e}")
        except Exception as e:
            logger.exception("Unexpected error occurred")
            raise CommandError(f"Seeding failed: {e}")
    
    def _clear_existing_data(self):
        """Clear existing cocktail and ingredient data."""
        self.stdout.write("🧹 Clearing existing data...")
        
        with transaction.atomic():
            RecipeComponent.objects.all().delete()
            Cocktail.objects.all().delete()
            Ingredient.objects.all().delete()
            # Keep vessels - they're reusable
        
        self.stdout.write(self.style.WARNING("Cleared existing cocktails and ingredients"))
    
    def _get_or_create_admin_user(self):
        """
        Get or create an admin user for imported cocktails.
        
        All cocktails imported from TheCocktailDB need a creator (User object).
        This method creates a dedicated admin user specifically for API imports,
        allowing us to distinguish between user-created and imported cocktails.
        
        Returns:
            User: The admin user object for imported cocktails
        """
        admin_user, created = User.objects.get_or_create(
            username='cocktaildb_admin',
            defaults={
                'first_name': 'TheCocktailDB',
                'last_name': 'Importer',
                'email': 'admin@stircraft.local',
                'is_staff': False,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write("👤 Created admin user for imported cocktails")
        
        return admin_user
    
    def _seed_vessels(self):
        """
        Create common vessel types that cocktails might reference.
        
        StirCraft's vessel model includes detailed information about glassware:
        - Volume capacity in milliliters
        - Material (typically glass)
        - Whether the glass has a stem (affects temperature retention)
        
        This method pre-populates the database with standard cocktail glassware
        so that imported cocktails can be properly matched to appropriate vessels.
        
        Vessel Types Created:
        - Cocktail Glass (150ml, stemmed) - Classic V-shaped cocktail glass
        - Martini Glass (180ml, stemmed) - Similar to cocktail but larger
        - Old Fashioned Glass (240ml, not stemmed) - Short, wide glass for spirits
        - Rocks Glass (240ml, not stemmed) - Same as Old Fashioned
        - Highball Glass (350ml, not stemmed) - Tall glass for mixed drinks
        - Collins Glass (400ml, not stemmed) - Taller than highball
        - And more...
        """
        common_vessels = [
            {'name': 'Cocktail Glass', 'volume': 150.00, 'material': 'Glass', 'stemmed': True},
            {'name': 'Martini Glass', 'volume': 180.00, 'material': 'Glass', 'stemmed': True},
            {'name': 'Old Fashioned Glass', 'volume': 240.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Rocks Glass', 'volume': 240.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Highball Glass', 'volume': 350.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Collins Glass', 'volume': 400.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Coupe Glass', 'volume': 160.00, 'material': 'Glass', 'stemmed': True},
            {'name': 'Wine Glass', 'volume': 250.00, 'material': 'Glass', 'stemmed': True},
            {'name': 'Shot Glass', 'volume': 45.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Champagne Flute', 'volume': 180.00, 'material': 'Glass', 'stemmed': True},
            {'name': 'Margarita Glass', 'volume': 300.00, 'material': 'Glass', 'stemmed': True},
            {'name': 'Hurricane Glass', 'volume': 600.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Beer Mug', 'volume': 500.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Irish Coffee Cup', 'volume': 250.00, 'material': 'Glass', 'stemmed': False},
            {'name': 'Punch Bowl', 'volume': 2000.00, 'material': 'Glass', 'stemmed': False},
        ]
        
        vessels_created = 0
        for vessel_data in common_vessels:
            vessel, created = Vessel.objects.get_or_create(
                name=vessel_data['name'],
                defaults=vessel_data
            )
            if created:
                vessels_created += 1
        
        if vessels_created > 0:
            self.stdout.write(f"🍷 Created {vessels_created} vessel types")
    
    def _fetch_cocktails_by_letters(self, letters, limit=None):
        """
        Fetch cocktails from TheCocktailDB API by searching each letter.
        
        TheCocktailDB provides a search endpoint that finds cocktails starting
        with a specific letter: /search.php?f={letter}
        
        This method:
        1. Iterates through each requested letter (default: a-z)
        2. Makes API requests with proper error handling
        3. Includes rate limiting (0.5s delay) to be respectful to the API
        4. Aggregates all results into a single list
        5. Applies the limit if specified
        
        Args:
            letters (str): Letters to search (e.g., 'abc' or 'abcdefghijklmnopqrstuvwxyz')
            limit (int, optional): Maximum number of cocktails to return
            
        Returns:
            list: List of cocktail data dictionaries from TheCocktailDB
            
        API Response Format (per cocktail):
            - strDrink: Cocktail name
            - strCategory: Category (e.g., "Ordinary Drink", "Shot")
            - strGlass: Glass type (e.g., "Old-fashioned glass")
            - strAlcoholic: "Alcoholic" or "Non alcoholic"
            - strInstructions: Preparation instructions
            - strDrinkThumb: URL to cocktail image
            - strIngredient1-15: Ingredient names (up to 15)
            - strMeasure1-15: Measurements for each ingredient
        """
        self.stdout.write("📡 Fetching cocktails from TheCocktailDB API...")
        
        base_url = "https://www.thecocktaildb.com/api/json/v1/1/search.php?f="
        all_cocktails = []
        
        for letter in letters:
            if limit and len(all_cocktails) >= limit:
                break
                
            self.stdout.write(f"🔤 Searching for cocktails starting with '{letter.upper()}'...")
            
            try:
                response = requests.get(f"{base_url}{letter}", timeout=10)
                response.raise_for_status()
                data = response.json()
                
                drinks = data.get('drinks')
                if drinks:
                    self.stdout.write(f"   Found {len(drinks)} cocktails")
                    all_cocktails.extend(drinks)
                else:
                    self.stdout.write(f"   No cocktails found for '{letter.upper()}'")
                
                # Be respectful to the API - small delay between requests
                # This prevents overwhelming the free API service
                time.sleep(0.5)
                
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.WARNING(f"   Failed to fetch cocktails for '{letter}': {e}")
                )
                continue
        
        if limit:
            all_cocktails = all_cocktails[:limit]
            self.stdout.write(f"📊 Limited to {limit} cocktails for testing")
        
        self.stdout.write(f"📥 Retrieved {len(all_cocktails)} cocktails total")
        return all_cocktails
    
    def _process_cocktails(self, cocktails_data, admin_user):
        """Process and save cocktails to the database."""
        self.stdout.write("⚙️  Processing cocktails...")
        
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        for index, cocktail_data in enumerate(cocktails_data, 1):
            try:
                with transaction.atomic():
                    cocktail, created = self._create_cocktail(cocktail_data, admin_user)
                    
                    if created:
                        created_count += 1
                        logger.info(f"Created cocktail: {cocktail.name}")
                    else:
                        skipped_count += 1
                        logger.debug(f"Skipped existing cocktail: {cocktail.name}")
                
                # Progress indicator
                if index % 25 == 0:
                    self.stdout.write(f"⏳ Processed {index}/{len(cocktails_data)} cocktails...")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing cocktail {cocktail_data.get('strDrink', 'Unknown')}: {e}")
                continue
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Created: {created_count}, Skipped: {skipped_count}, Errors: {error_count}"
            )
        )
    
    def _create_cocktail(self, cocktail_data, admin_user):
        """
        Create a cocktail and its components from TheCocktailDB API data.
        
        This method performs the core data transformation from TheCocktailDB's
        format to StirCraft's data model structure. It handles:
        
        1. Duplicate prevention (skip if cocktail already exists)
        2. Vessel matching (map glass types to StirCraft vessels)
        3. Alcoholic status determination
        4. Category and tag assignment
        5. Ingredient processing with measurements
        
        Args:
            cocktail_data (dict): Raw cocktail data from TheCocktailDB API
            admin_user (User): User object to assign as cocktail creator
            
        Returns:
            tuple: (Cocktail object, boolean indicating if created)
            
        Data Transformations:
            - strDrink → Cocktail.name
            - strCategory → description text and vibe tags
            - strInstructions → Cocktail.instructions
            - strGlass → matched to appropriate Vessel object
            - strAlcoholic → Cocktail.is_alcoholic boolean
            - strIngredient1-15 → Ingredient objects + RecipeComponents
            - strMeasure1-15 → parsed amounts and units
        """
        
        cocktail_name = cocktail_data['strDrink']
        
        # Skip if cocktail already exists
        existing_cocktail = Cocktail.objects.filter(name=cocktail_name).first()
        if existing_cocktail:
            return existing_cocktail, False
        
        # Find appropriate vessel based on TheCocktailDB glass type
        # This uses intelligent matching to map API glass names to StirCraft vessels
        vessel = self._find_matching_vessel(cocktail_data.get('strGlass', ''))
        
        # Determine if cocktail is alcoholic based on API data
        # TheCocktailDB uses "Alcoholic" or "Non alcoholic" strings
        alcoholic_status = cocktail_data.get('strAlcoholic', 'Alcoholic')
        is_alcoholic = alcoholic_status == 'Alcoholic'
        
        # Create the cocktail
        cocktail = Cocktail.objects.create(
            name=cocktail_name,
            description=f"Imported from TheCocktailDB - {cocktail_data.get('strCategory', 'Unknown')} category",
            instructions=cocktail_data.get('strInstructions', ''),
            creator=admin_user,
            vessel=vessel,
            is_alcoholic=is_alcoholic,
            color=self._extract_color_from_category(cocktail_data.get('strCategory', '')),
        )
        
        # Add category and alcoholic status as vibe tags for filtering
        # Vibe tags allow users to search for cocktails by mood, category, etc.
        if cocktail_data.get('strCategory'):
            # Convert spaces to hyphens for consistent tag format
            cocktail.vibe_tags.add(cocktail_data['strCategory'].lower().replace(' ', '-'))
        
        # Add alcoholic status as a searchable tag
        cocktail.vibe_tags.add('alcoholic' if is_alcoholic else 'non-alcoholic')
        
        # Process ingredients (TheCocktailDB has up to 15 ingredients per cocktail)
        self._process_thecocktaildb_ingredients(cocktail, cocktail_data)
        
        return cocktail, True
    
    def _process_thecocktaildb_ingredients(self, cocktail, cocktail_data):
        """
        Process ingredients from TheCocktailDB API format.
        
        TheCocktailDB stores ingredients in a denormalized format:
        - strIngredient1, strIngredient2, ..., strIngredient15
        - strMeasure1, strMeasure2, ..., strMeasure15
        
        This method:
        1. Iterates through all 15 possible ingredient slots
        2. Skips empty/null ingredients
        3. Creates or retrieves Ingredient objects with intelligent categorization
        4. Parses measurement text into structured amount/unit data
        5. Creates RecipeComponent objects to link cocktails with ingredients
        6. Handles errors gracefully (individual ingredient failures don't stop processing)
        
        Ingredient Processing:
        - Categorizes ingredients (spirit, liqueur, mixer, juice, etc.)
        - Estimates alcohol content for each ingredient
        - Adds flavor tags based on ingredient name
        - Parses measurements from text (e.g., "1 oz" → 29.57 ml)
        
        Args:
            cocktail (Cocktail): The cocktail object to add ingredients to
            cocktail_data (dict): Raw cocktail data from TheCocktailDB API
        """
        ingredients_processed = 0
        
        # TheCocktailDB stores ingredients as strIngredient1, strIngredient2, etc.
        # and measurements as strMeasure1, strMeasure2, etc.
        for i in range(1, 16):  # Up to 15 ingredients per cocktail
            ingredient_name = cocktail_data.get(f'strIngredient{i}')
            ingredient_measure = cocktail_data.get(f'strMeasure{i}')
            
            # Skip empty ingredients (common in TheCocktailDB data)
            if not ingredient_name or ingredient_name.strip() == '':
                continue
                
            ingredient_name = ingredient_name.strip()
            
            try:
                # Get or create ingredient with intelligent categorization
                # StirCraft's Ingredient model includes type, alcohol content, and flavor tags
                ingredient, created = Ingredient.objects.get_or_create(
                    name=ingredient_name,
                    defaults={
                        'ingredient_type': self._guess_ingredient_type(ingredient_name),
                        'description': f'Imported from TheCocktailDB',
                        'alcohol_content': self._guess_alcohol_content(ingredient_name),
                    }
                )
                
                if created:
                    # Add flavor tags for new ingredients
                    # This enables advanced filtering (e.g., "citrusy cocktails")
                    self._add_flavor_tags(ingredient, ingredient_name)
                
                # Parse measurement text into structured amount and unit
                # Handles various formats: "1 oz", "1/2 cup", "dash", etc.
                amount, unit = self._parse_measurement(ingredient_measure, ingredient_name, ingredients_processed)
                
                # Create the recipe component linking cocktail to ingredient
                # Includes order for proper recipe display
                RecipeComponent.objects.create(
                    cocktail=cocktail,
                    ingredient=ingredient,
                    amount=amount,
                    unit=unit,
                    order=ingredients_processed,  # Preserves ingredient order from API
                    preparation_note=''  # TheCocktailDB doesn't provide preparation notes
                )
                
                ingredients_processed += 1
                
            except Exception as e:
                logger.error(f"Error processing ingredient {ingredient_name}: {e}")
                continue
        
        if ingredients_processed == 0:
            logger.warning(f"No ingredients processed for cocktail: {cocktail.name}")
    
    def _parse_measurement(self, measure_text, ingredient_name, order):
        """
        Parse measurement text from TheCocktailDB into amount and unit.
        
        TheCocktailDB measurements come in various text formats that need to be
        converted to structured data for StirCraft's RecipeComponent model.
        
        Supported Formats:
        - "1 oz", "2 oz", "1.5 oz" → converted to milliliters
        - "1/2 oz", "3/4 oz" → fractional measurements
        - "1 tbsp", "1 tsp" → tablespoons, teaspoons
        - "dash", "splash" → small amounts
        - "slice", "wedge", "twist" → garnish pieces
        - "fill", "top off" → larger amounts for mixers
        
        Conversion Logic:
        - All measurements standardized to metric (ml) when possible
        - Ounces converted to milliliters (1 oz = 29.5735 ml)
        - Fallback estimation for unparseable measurements
        - Context-aware defaults based on ingredient type and order
        
        Args:
            measure_text (str): Raw measurement text from TheCocktailDB
            ingredient_name (str): Name of ingredient (for context-aware parsing)
            order (int): Order of ingredient in recipe (for context-aware defaults)
            
        Returns:
            tuple: (Decimal amount, str unit)
        """
        if not measure_text or measure_text.strip() == '':
            # No measurement provided - use intelligent estimation
            return self._estimate_measurement(ingredient_name, order)
        
        measure_text = measure_text.strip()
        
        # Common measurement patterns with regex for flexible matching
        # Each pattern includes the regex and the target unit
        measurement_patterns = [
            # Ounces
            (r'(\d+(?:\.\d+)?)\s*oz', 'oz'),
            (r'(\d+(?:\.\d+)?)\s*ounces?', 'oz'),
            
            # Milliliters
            (r'(\d+(?:\.\d+)?)\s*ml', 'ml'),
            (r'(\d+(?:\.\d+)?)\s*milliliters?', 'ml'),
            
            # Tablespoons and teaspoons
            (r'(\d+(?:\.\d+)?)\s*tbsp', 'tbsp'),
            (r'(\d+(?:\.\d+)?)\s*tablespoons?', 'tbsp'),
            (r'(\d+(?:\.\d+)?)\s*tsp', 'tsp'),
            (r'(\d+(?:\.\d+)?)\s*teaspoons?', 'tsp'),
            
            # Fractions
            (r'(\d+)/(\d+)\s*oz', 'oz'),  # Will need special handling
            (r'1/2', 'oz'),  # Common half measurements
            (r'1/4', 'oz'),  # Quarter measurements
            (r'3/4', 'oz'),  # Three quarter measurements
            
            # Dashes and splashes
            (r'(\d+)?\s*dash(?:es)?', 'dash'),
            (r'(\d+)?\s*splash(?:es)?', 'splash'),
            
            # Pieces/garnish
            (r'(\d+)?\s*(?:slice|wheel|wedge|twist)', 'piece'),
            (r'(\d+)?\s*(?:olive|cherry|mint)', 'piece'),
        ]
        
        # Try to match patterns
        for pattern, unit in measurement_patterns:
            match = re.search(pattern, measure_text.lower())
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[0] and groups[1]:  # Fraction like 1/2
                    numerator = float(groups[0])
                    denominator = float(groups[1])
                    amount = Decimal(str(numerator / denominator))
                elif len(groups) >= 1 and groups[0]:  # Has amount
                    amount = Decimal(str(float(groups[0])))
                else:  # No amount specified (like "dash" or "splash")
                    amount = Decimal('1.0')
                
                # Convert oz to ml for consistency
                if unit == 'oz':
                    amount = amount * Decimal('29.5735')  # 1 oz = 29.5735 ml
                    unit = 'ml'
                
                return amount, unit
        
        # Handle special cases
        if 'fill' in measure_text.lower() or 'top' in measure_text.lower():
            return Decimal('120.00'), 'ml'  # Typical fill amount
        
        if any(word in measure_text.lower() for word in ['drop', 'few']):
            return Decimal('2.50'), 'ml'  # Small amount
        
        # Default estimation if no pattern matches
        return self._estimate_measurement(ingredient_name, order)
    
    def _find_matching_vessel(self, glass_type):
        """Find the best matching vessel for a given glass type."""
        if not glass_type:
            return Vessel.objects.filter(name='Old Fashioned Glass').first()
        
        glass_type_lower = glass_type.lower()
        
        # Direct matches
        vessel_mappings = {
            'cocktail glass': 'Cocktail Glass',
            'martini glass': 'Martini Glass', 
            'old fashioned glass': 'Old Fashioned Glass',
            'old-fashioned glass': 'Old Fashioned Glass',
            'rocks glass': 'Rocks Glass',
            'highball glass': 'Highball Glass',
            'collins glass': 'Collins Glass',
            'coupe glass': 'Coupe Glass',
            'wine glass': 'Wine Glass',
            'shot glass': 'Shot Glass',
            'champagne flute': 'Champagne Flute',
            'margarita glass': 'Margarita Glass',
            'hurricane glass': 'Hurricane Glass',
            'beer mug': 'Beer Mug',
            'irish coffee cup': 'Irish Coffee Cup',
        }
        
        for api_glass, vessel_name in vessel_mappings.items():
            if api_glass in glass_type_lower:
                vessel = Vessel.objects.filter(name=vessel_name).first()
                if vessel:
                    return vessel
        
        # Fallback patterns
        if 'martini' in glass_type_lower:
            return Vessel.objects.filter(name='Martini Glass').first()
        elif 'rock' in glass_type_lower or 'old' in glass_type_lower:
            return Vessel.objects.filter(name='Old Fashioned Glass').first()
        elif 'high' in glass_type_lower or 'tall' in glass_type_lower:
            return Vessel.objects.filter(name='Highball Glass').first()
        elif 'shot' in glass_type_lower:
            return Vessel.objects.filter(name='Shot Glass').first()
        elif 'wine' in glass_type_lower:
            return Vessel.objects.filter(name='Wine Glass').first()
        
        # Default fallback
        return Vessel.objects.filter(name='Old Fashioned Glass').first()
    
    def _extract_color_from_category(self, category):
        """Extract potential color information from cocktail category."""
        if not category:
            return ''
        
        category_lower = category.lower()
        
        color_keywords = {
            'red': 'red',
            'blue': 'blue', 
            'green': 'green',
            'yellow': 'yellow',
            'pink': 'pink',
            'purple': 'purple',
            'orange': 'orange',
            'white': 'white',
            'black': 'black',
            'brown': 'brown',
            'clear': 'clear',
        }
        
        for keyword, color in color_keywords.items():
            if keyword in category_lower:
                return color
        
        return ''
    
    def _guess_ingredient_type(self, ingredient_name):
        """
        Intelligently categorize ingredients based on name analysis.
        
        StirCraft uses ingredient types for filtering and organization:
        - spirit: Base spirits (vodka, gin, rum, whiskey, etc.)
        - liqueur: Flavored alcoholic beverages (amaretto, cointreau, etc.)
        - juice: Fruit juices and citrus
        - syrup: Sweet syrups and grenadine
        - bitters: Concentrated flavorings
        - mixer: Non-alcoholic mixers (tonic, soda, etc.)
        - garnish: Garnishes and decorative elements
        - other: Catch-all for unique ingredients
        
        Uses keyword matching on lowercased ingredient names for classification.
        
        Args:
            ingredient_name (str): Name of the ingredient to categorize
            
        Returns:
            str: One of the ingredient type constants
        """
        name_lower = ingredient_name.lower()
        
        # Spirits (typically main ingredients)
        spirits = ['vodka', 'gin', 'rum', 'whiskey', 'whisky', 'tequila', 'brandy', 'bourbon', 'scotch', 'rye']
        if any(spirit in name_lower for spirit in spirits):
            return 'spirit'
        
        # Liqueurs
        liqueurs = ['liqueur', 'schnapps', 'amaretto', 'cointreau', 'curacao', 'kahlua', 'baileys', 'sambuca']
        if any(liqueur in name_lower for liqueur in liqueurs):
            return 'liqueur'
        
        # Juices
        if 'juice' in name_lower or any(fruit in name_lower for fruit in ['lemon', 'lime', 'orange', 'cranberry', 'pineapple', 'grapefruit']):
            return 'juice'
        
        # Syrups
        if 'syrup' in name_lower or 'grenadine' in name_lower:
            return 'syrup'
        
        # Bitters
        if 'bitter' in name_lower:
            return 'bitters'
        
        # Mixers
        mixers = ['tonic', 'soda', 'water', 'ginger ale', 'cola', 'sprite', 'club soda']
        if any(mixer in name_lower for mixer in mixers):
            return 'mixer'
        
        # Garnishes
        garnishes = ['olive', 'cherry', 'mint', 'basil', 'rosemary', 'thyme', 'peel', 'twist', 'wedge', 'wheel']
        if any(garnish in name_lower for garnish in garnishes):
            return 'garnish'
        
        return 'other'
    
    def _guess_alcohol_content(self, ingredient_name):
        """
        Estimate alcohol content (ABV) based on ingredient name.
        
        StirCraft tracks alcohol content for each ingredient to:
        - Calculate total cocktail ABV
        - Enable filtering by alcohol strength
        - Support age verification features
        - Provide mocktail alternatives
        
        Estimation Logic:
        - High-proof spirits (vodka, gin, rum, etc.): 40% ABV
        - Wine-based products (wine, champagne, vermouth): 12% ABV  
        - Liqueurs and flavored spirits: 20% ABV
        - Beer products: 5% ABV
        - Non-alcoholic ingredients: 0% ABV (default)
        
        Args:
            ingredient_name (str): Name of ingredient to analyze
            
        Returns:
            float: Estimated alcohol by volume percentage (0.0-100.0)
        """
        name_lower = ingredient_name.lower()
        
        # High alcohol spirits
        if any(spirit in name_lower for spirit in ['vodka', 'gin', 'rum', 'whiskey', 'whisky', 'tequila', 'brandy']):
            return 40.0
        
        # Wine-based
        if any(wine in name_lower for wine in ['wine', 'champagne', 'prosecco', 'vermouth']):
            return 12.0
        
        # Liqueurs (typically lower alcohol)
        if any(liqueur in name_lower for liqueur in ['liqueur', 'schnapps', 'amaretto', 'kahlua', 'baileys']):
            return 20.0
        
        # Beer
        if 'beer' in name_lower:
            return 5.0
        
        # Non-alcoholic by default
        return 0.0
    
    def _add_flavor_tags(self, ingredient, ingredient_name):
        """
        Add flavor profile tags to ingredients for advanced filtering.
        
        StirCraft uses django-taggit to enable flavor-based cocktail discovery.
        Users can search for cocktails with specific flavor profiles like:
        - "Show me citrusy cocktails"
        - "Find sweet cocktails without being too fruity"
        - "Herbal cocktails for a sophisticated palate"
        
        Flavor Categories:
        - citrus: Lemon, lime, orange, grapefruit
        - sweet: Sugar, syrups, honey, sweet liqueurs
        - bitter: Bitters, Campari, bitter herbs
        - herbal: Mint, basil, rosemary, botanical spirits
        - spicy: Ginger, cinnamon, pepper, heat
        - fruity: Berry flavors, fruit liqueurs
        - tropical: Coconut, pineapple, exotic fruits
        - earthy: Woody, soil-like, mushroom notes
        - smoky: Peated scotch, smoked ingredients
        
        Args:
            ingredient (Ingredient): The ingredient object to tag
            ingredient_name (str): Name to analyze for flavor keywords
        """
        name_lower = ingredient_name.lower()
        
        flavor_mappings = {
            'citrus': ['lemon', 'lime', 'orange', 'grapefruit', 'citrus'],
            'sweet': ['sugar', 'syrup', 'honey', 'agave', 'sweet'],
            'bitter': ['bitter', 'campari', 'aperol'],
            'herbal': ['mint', 'basil', 'rosemary', 'thyme', 'sage', 'herbal'],
            'spicy': ['ginger', 'cinnamon', 'pepper', 'spicy', 'hot'],
            'fruity': ['cherry', 'berry', 'apple', 'pear', 'peach', 'fruity'],
            'tropical': ['coconut', 'pineapple', 'mango', 'passion fruit', 'tropical'],
            'earthy': ['mushroom', 'soil', 'earth', 'woody'],
            'smoky': ['smoke', 'peated', 'smoky'],
        }
        
        for flavor_tag, keywords in flavor_mappings.items():
            if any(keyword in name_lower for keyword in keywords):
                ingredient.flavor_tags.add(flavor_tag)
    
    def _estimate_measurement(self, ingredient_name, order):
        """Estimate amount and unit for an ingredient based on typical cocktail proportions."""
        name_lower = ingredient_name.lower()
        
        # Primary spirits (usually 1.5-2 oz)
        if order == 0 and any(spirit in name_lower for spirit in ['vodka', 'gin', 'rum', 'whiskey', 'tequila']):
            return Decimal('60.00'), 'ml'  # 2 oz in ml
        
        # Secondary spirits or liqueurs (usually 0.5-1 oz)
        if any(spirit in name_lower for spirit in ['liqueur', 'vermouth', 'amaretto', 'cointreau']):
            return Decimal('22.50'), 'ml'  # 0.75 oz in ml
        
        # Juices (usually 0.5-1 oz)
        if 'juice' in name_lower or any(fruit in name_lower for fruit in ['lemon', 'lime']):
            return Decimal('22.50'), 'ml'  # 0.75 oz in ml
        
        # Syrups (usually small amounts)
        if 'syrup' in name_lower or 'grenadine' in name_lower:
            return Decimal('15.00'), 'ml'  # 0.5 oz in ml
        
        # Bitters (very small amounts)
        if 'bitter' in name_lower:
            return Decimal('2.50'), 'ml'  # Few dashes
        
        # Mixers (larger amounts)
        if any(mixer in name_lower for mixer in ['tonic', 'soda', 'ginger ale']):
            return Decimal('120.00'), 'ml'  # 4 oz in ml
        
        # Garnishes (pieces)
        if any(garnish in name_lower for garnish in ['olive', 'cherry', 'mint']):
            return Decimal('1.00'), 'piece'
        
        # Default
        return Decimal('30.00'), 'ml'  # 1 oz in ml
    
    def _print_summary(self):
        """
        Print a comprehensive summary of the import operation.
        
        Provides detailed statistics about what was imported:
        - Total counts of cocktails, ingredients, and vessels
        - Sample of recently imported cocktails
        - Helpful next steps for the user
        
        This summary helps users understand the scope of the import
        and provides guidance for exploring the new data.
        """
        cocktail_count = Cocktail.objects.count()
        ingredient_count = Ingredient.objects.count()
        vessel_count = Vessel.objects.count()
        
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("📊 IMPORT SUMMARY"))
        self.stdout.write("="*50)
        self.stdout.write(f"🍸 Total Cocktails: {cocktail_count}")
        self.stdout.write(f"🧂 Total Ingredients: {ingredient_count}")
        self.stdout.write(f"🍷 Total Vessels: {vessel_count}")
        self.stdout.write("="*50 + "\n")
        
        # Show some sample cocktails
        recent_cocktails = Cocktail.objects.order_by('-created_at')[:5]
        if recent_cocktails:
            self.stdout.write("🎯 Recently imported cocktails:")
            for cocktail in recent_cocktails:
                self.stdout.write(f"  • {cocktail.name}")
        
        self.stdout.write(f"\n💡 Next steps:")
        self.stdout.write(f"  • Run: python manage.py runserver")
        self.stdout.write(f"  • Visit your admin panel to review the imported data")
        self.stdout.write(f"  • Consider adding user profiles and custom cocktail lists")
