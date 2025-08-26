"""
Enhanced ingredient management command that handles:
1. Duplicate detection and merging with fuzzy matching
2. Smart categorization based on comprehensive rules
3. Specific fixes for common issues (Orange peel vs Orange juice, Tonic Water vs tonic water, etc.)
4. Duplicate prevention utilities

Usage:
    python manage.py fix_ingredients --dry-run
    python manage.py fix_ingredients --apply
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Ingredient, RecipeComponent
from collections import defaultdict
import re
from difflib import SequenceMatcher


class Command(BaseCommand):
    help = 'Comprehensive ingredient cleanup: duplicates, categorization, and data quality fixes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply all changes (use after reviewing --dry-run)',
        )
        parser.add_argument(
            '--duplicates-only',
            action='store_true',
            help='Only process duplicates, skip recategorization',
        )
        parser.add_argument(
            '--categorize-only',
            action='store_true',
            help='Only recategorize, skip duplicate cleanup',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        apply_changes = options['apply']
        duplicates_only = options['duplicates_only']
        categorize_only = options['categorize_only']
        
        if not dry_run and not apply_changes:
            self.stdout.write(
                self.style.WARNING(
                    'Use --dry-run to see changes, or --apply to make changes'
                )
            )
            return
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        changes_made = 0
        
        # Step 1: Handle duplicates (unless categorize-only)
        if not categorize_only:
            changes_made += self.process_duplicates(dry_run)
        
        # Step 2: Smart recategorization (unless duplicates-only)
        if not duplicates_only:
            changes_made += self.recategorize_ingredients(dry_run)
        
        # Step 3: Fix specific issues
        if not duplicates_only:
            changes_made += self.fix_specific_issues(dry_run)
        
        # Final summary
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'\nDRY RUN COMPLETE: Would make {changes_made} total changes')
            )
            self.stdout.write('Review the changes above, then run with --apply to execute them.')
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nCOMPLETE: Made {changes_made} total changes to ingredients')
            )
            self.show_category_summary()

    def similarity(self, a, b):
        """Calculate similarity between two strings (0-1, where 1 is identical)"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def normalize_name(self, name):
        """Normalize ingredient name for comparison"""
        # Convert to lowercase, strip whitespace, remove extra spaces
        normalized = re.sub(r'\s+', ' ', name.lower().strip())
        # Remove common variations
        normalized = normalized.replace('&', 'and')
        return normalized

    def process_duplicates(self, dry_run):
        """Enhanced duplicate detection with fuzzy matching"""
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('STEP 1: DUPLICATE DETECTION AND MERGING'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        changes_made = 0
        
        # Group ingredients by normalized names
        ingredient_groups = defaultdict(list)
        for ingredient in Ingredient.objects.all():
            normalized = self.normalize_name(ingredient.name)
            ingredient_groups[normalized].append(ingredient)
        
        # Find exact duplicates first
        exact_duplicates = {name: ingredients for name, ingredients in ingredient_groups.items() 
                           if len(ingredients) > 1}
        
        if exact_duplicates:
            self.stdout.write(f'\nFound {len(exact_duplicates)} sets of exact duplicates:')
            
            for name_normalized, ingredients in exact_duplicates.items():
                self.stdout.write(f'\n"{name_normalized}" has {len(ingredients)} duplicates:')
                
                # Score and choose best ingredient
                best_ingredient = self.choose_best_ingredient(ingredients)
                others = [ing for ing in ingredients if ing.id != best_ingredient.id]
                
                self.stdout.write(f'  → Keeping: "{best_ingredient.name}" (ID: {best_ingredient.id})')
                
                for other in others:
                    recipe_count = RecipeComponent.objects.filter(ingredient=other).count()
                    self.stdout.write(f'  → Merging: "{other.name}" (used in {recipe_count} recipes)')
                    
                    if not dry_run:
                        with transaction.atomic():
                            # Move all recipe components
                            RecipeComponent.objects.filter(ingredient=other).update(ingredient=best_ingredient)
                            
                            # Merge flavor tags
                            for tag in other.flavor_tags.all():
                                best_ingredient.flavor_tags.add(tag)
                            
                            # Merge descriptions if needed
                            if not best_ingredient.description and other.description:
                                best_ingredient.description = other.description
                                best_ingredient.save()
                            
                            other.delete()
                    
                    changes_made += 1
        
        # Look for fuzzy duplicates (similar but not exact)
        all_ingredients = list(Ingredient.objects.all())
        fuzzy_duplicates_found = []
        
        for i, ing1 in enumerate(all_ingredients):
            for ing2 in all_ingredients[i+1:]:
                similarity = self.similarity(ing1.name, ing2.name)
                if similarity > 0.85:  # 85% similarity threshold
                    fuzzy_duplicates_found.append((ing1, ing2, similarity))
        
        if fuzzy_duplicates_found:
            self.stdout.write(f'\nFound {len(fuzzy_duplicates_found)} potential fuzzy duplicates:')
            for ing1, ing2, similarity in fuzzy_duplicates_found:
                self.stdout.write(f'  "{ing1.name}" ≈ "{ing2.name}" ({similarity:.2%} similar)')
                self.stdout.write(f'    → Manual review recommended')
        
        return changes_made

    def recategorize_ingredients(self, dry_run):
        """Enhanced ingredient categorization with comprehensive rules"""
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('STEP 2: SMART RECATEGORIZATION'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        changes_made = 0
        
        # Enhanced categorization rules with priority order
        categorization_rules = {
            'bitters': [
                # Bitters should be checked first (most specific)
                r'bitters?$', r'bitter\s+truth', r'angostura', r'peychaud'
            ],
            'spirit': [
                # Base spirits
                r'whiskey|whisky|bourbon|rye|scotch', r'crown\s+royal', r'wild\s+turkey',
                r'brandy|cognac|armagnac|calvados', r'applejack',
                r'rum(?!\s+extract)', r'bacardi', r'captain\s+morgan',
                r'gin(?!\s+ale)', r'hendricks', r'tanqueray',
                r'vodka', r'absolut', r'grey\s+goose', r'smirnoff',
                r'tequila|mezcal', r'patron', r'jose\s+cuervo',
                r'everclear', r'grain\s+alcohol', r'neutral\s+spirit'
            ],
            'liqueur': [
                # Liqueurs and fortified wines
                r'crème?\s+de|creme\s+de', r'amaretto', r'cointreau', r'grand\s+marnier',
                r'kahlúa|kahlua', r'baileys?', r'sambuca', r'galliano', r'chartreuse',
                r'bénédictine|benedictine', r'drambuie', r'frangelico', r'midori',
                r'triple\s+sec', r'curaçao|curacao', r'campari', r'aperol',
                r'vermouth', r'dry\s+vermouth', r'sweet\s+vermouth', r'dubonnet',
                r'fernet', r'cynar', r'averna', r'jägermeister|jagermeister',
                r'limoncello', r'southern\s+comfort', r'goldschläger|goldschlager',
                r'irish\s+cream', r'pernod', r'ouzo', r'pisang\s+ambon'
            ],
            'wine': [
                r'wine(?!\s+vinegar)', r'champagne', r'prosecco', r'cava', r'sherry',
                r'port(?!\s+wine)', r'madeira', r'marsala', r'sake', r'riesling',
                r'chardonnay', r'pinot', r'cabernet', r'merlot'
            ],
            'beer': [
                r'^beer$', r'ale(?!\s+ginger)', r'lager', r'stout', r'porter',
                r'corona(?!\s+extra)', r'guinness', r'heineken'
            ],
            'soda': [
                # Carbonated beverages
                r'tonic\s+water', r'club\s+soda', r'soda\s+water', r'seltzer',
                r'sparkling\s+water', r'ginger\s+ale', r'ginger\s+beer',
                r'cola|coke', r'pepsi', r'sprite', r'7-?up', r'mountain\s+dew',
                r'root\s+beer', r'cream\s+soda', r'surge', r'zima'
            ],
            'juice': [
                # Fruit and vegetable juices
                r'juice(?!\s+concentrate)', r'nectar', r'cranberry', r'apple(?!\s+brandy)',
                r'orange(?=\s+juice)', r'lemon(?=\s+juice)', r'lime(?=\s+juice)',
                r'grapefruit', r'pineapple(?=\s+juice)', r'tomato(?=\s+juice)'
            ],
            'syrup': [
                # Syrups and sweeteners
                r'syrup', r'grenadine', r'simple\s+syrup', r'honey', r'agave',
                r'maple', r'corn\s+syrup', r'orgeat', r'falernum'
            ],
            'dairy': [
                # Dairy and egg products
                r'cream(?!\s+soda)', r'milk(?!\s+punch)', r'egg\s+white', r'egg$',
                r'half\s+and\s+half', r'condensed\s+milk', r'coconut\s+cream',
                r'ice\s*cream', r'yogurt', r'buttermilk'
            ],
            'garnish': [
                # Garnishes and aromatics
                r'peel(?!\s+juice)', r'zest', r'twist', r'wheel', r'wedge',
                r'cherry(?!\s+juice)', r'olive', r'onion(?!\s+juice)', r'pearl\s+onion',
                r'mint(?!\s+syrup)', r'basil', r'rosemary', r'thyme', r'sage',
                r'celery', r'pickle', r'cornichon', r'capers',
                r'salt(?!\s+water)', r'sugar(?!\s+syrup)', r'cinnamon', r'nutmeg',
                r'coffee\s+bean', r'peppercorn', r'star\s+anise', r'cardamom',
                r'paprika', r'chili', r'jalapeño|jalapeno'
            ],
            'mixer': [
                # Non-carbonated mixers
                r'water(?!\s+tonic)', r'coconut\s+water', r'energy\s+drink',
                r'kool-?aid', r'sweet\s+and\s+sour', r'sour\s+mix', r'bloody\s+mary\s+mix'
            ]
        }
        
        # Apply categorization rules
        for new_category, patterns in categorization_rules.items():
            for pattern in patterns:
                regex = re.compile(pattern, re.IGNORECASE)
                
                # Find ingredients that match this pattern
                matching_ingredients = []
                for ingredient in Ingredient.objects.exclude(ingredient_type=new_category):
                    if regex.search(ingredient.name):
                        matching_ingredients.append(ingredient)
                
                for ingredient in matching_ingredients:
                    old_category = ingredient.get_ingredient_type_display()
                    new_category_display = dict(Ingredient.INGREDIENT_TYPES)[new_category]
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would change "{ingredient.name}" from {old_category} to {new_category_display}'
                        )
                    else:
                        ingredient.ingredient_type = new_category
                        ingredient.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Changed "{ingredient.name}" from {old_category} to {new_category_display}'
                            )
                        )
                    changes_made += 1
        
        return changes_made

    def fix_specific_issues(self, dry_run):
        """Fix specific categorization issues mentioned in the user's request"""
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 60))
        self.stdout.write(self.style.SUCCESS('STEP 3: SPECIFIC ISSUE FIXES'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        changes_made = 0
        
        # Specific fixes for common issues
        specific_fixes = [
            # Orange peel vs orange juice
            ('Orange peel', 'garnish', 'Contains "peel" - should be garnish'),
            ('Orange zest', 'garnish', 'Contains "zest" - should be garnish'),
            ('Orange twist', 'garnish', 'Contains "twist" - should be garnish'),
            
            # Bitters categorization
            ('Orange Bitters', 'bitters', 'Should be bitters, not juice'),
            ('Orange bitters', 'bitters', 'Should be bitters, not juice'),
            ('Angostura bitters', 'bitters', 'Should be bitters'),
            
            # Soda water variations
            ('Tonic Water', 'soda', 'Tonic water is a soda'),
            ('Tonic water', 'soda', 'Tonic water is a soda'),
            ('Club soda', 'soda', 'Club soda is a soda'),
            ('Soda Water', 'soda', 'Soda water is a soda'),
            ('Soda water', 'soda', 'Soda water is a soda'),
        ]
        
        for ingredient_name, correct_category, reason in specific_fixes:
            try:
                ingredient = Ingredient.objects.get(name=ingredient_name)
                if ingredient.ingredient_type != correct_category:
                    old_category = ingredient.get_ingredient_type_display()
                    new_category_display = dict(Ingredient.INGREDIENT_TYPES)[correct_category]
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would fix "{ingredient_name}": {old_category} → {new_category_display} ({reason})'
                        )
                    else:
                        ingredient.ingredient_type = correct_category
                        ingredient.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Fixed "{ingredient_name}": {old_category} → {new_category_display} ({reason})'
                            )
                        )
                    changes_made += 1
            except Ingredient.DoesNotExist:
                pass  # Ingredient doesn't exist, skip
        
        return changes_made

    def choose_best_ingredient(self, ingredients):
        """Choose the best ingredient to keep when merging duplicates"""
        scored_ingredients = []
        
        for ing in ingredients:
            score = 0
            
            # Score for having description
            if ing.description:
                score += 10
            
            # Score for having flavor tags
            score += ing.flavor_tags.count() * 5
            
            # Score for usage in recipes
            recipe_count = RecipeComponent.objects.filter(ingredient=ing).count()
            score += recipe_count * 3
            
            # Score for proper capitalization
            if ing.name.istitle() or ing.name[0].isupper():
                score += 5
            
            # Score for non-'other' category (prefer categorized ingredients)
            if ing.ingredient_type != 'other':
                score += 8
            
            # Prefer ingredients with higher alcohol content info (if applicable)
            if ing.alcohol_content > 0:
                score += 3
            
            scored_ingredients.append((score, ing))
        
        # Sort by score descending and return the best
        scored_ingredients.sort(key=lambda x: x[0], reverse=True)
        return scored_ingredients[0][1]

    def show_category_summary(self):
        """Show summary of ingredient categories after changes"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write('INGREDIENT CATEGORIES SUMMARY:')
        self.stdout.write('='*60)
        
        from collections import Counter
        ingredient_counts = Counter()
        for ingredient in Ingredient.objects.all():
            ingredient_counts[ingredient.get_ingredient_type_display()] += 1
        
        total_ingredients = sum(ingredient_counts.values())
        
        for category, count in sorted(ingredient_counts.items()):
            percentage = (count / total_ingredients) * 100
            self.stdout.write(f'{category:15}: {count:3} ingredients ({percentage:5.1f}%)')
        
        self.stdout.write(f'{"TOTAL":15}: {total_ingredients:3} ingredients')

    @staticmethod
    def suggest_category(ingredient_name):
        """
        Static method to suggest a category for a new ingredient.
        Can be used in forms or other parts of the application.
        """
        name_lower = ingredient_name.lower()
        
        # Bitters (check first - most specific)
        if re.search(r'bitters?$|bitter\s+truth|angostura|peychaud', name_lower):
            return 'bitters'
        
        # Spirits
        spirit_patterns = [
            r'whiskey|whisky|bourbon|rye|scotch', r'brandy|cognac', r'rum(?!\s+extract)',
            r'gin(?!\s+ale)', r'vodka', r'tequila|mezcal', r'everclear'
        ]
        if any(re.search(pattern, name_lower) for pattern in spirit_patterns):
            return 'spirit'
        
        # Liqueurs
        liqueur_patterns = [
            r'crème?\s+de|creme\s+de', r'amaretto', r'cointreau', r'grand\s+marnier',
            r'kahlúa|kahlua', r'triple\s+sec', r'vermouth', r'campari', r'chartreuse'
        ]
        if any(re.search(pattern, name_lower) for pattern in liqueur_patterns):
            return 'liqueur'
        
        # Sodas
        soda_patterns = [
            r'tonic\s+water', r'club\s+soda', r'soda\s+water', r'ginger\s+ale',
            r'cola|coke', r'sprite', r'7-?up', r'root\s+beer'
        ]
        if any(re.search(pattern, name_lower) for pattern in soda_patterns):
            return 'soda'
        
        # Juices
        if re.search(r'juice|nectar', name_lower):
            return 'juice'
        
        # Syrups
        if re.search(r'syrup|grenadine|honey|agave', name_lower):
            return 'syrup'
        
        # Garnishes
        garnish_patterns = [
            r'peel|zest|twist|wheel|wedge', r'cherry|olive|onion', r'mint|basil',
            r'salt|sugar|cinnamon|nutmeg'
        ]
        if any(re.search(pattern, name_lower) for pattern in garnish_patterns):
            return 'garnish'
        
        # Dairy
        if re.search(r'cream|milk|egg', name_lower):
            return 'dairy'
        
        # Default
        return 'other'

    @staticmethod
    def check_for_duplicates(ingredient_name):
        """
        Static method to check for potential duplicates before creating an ingredient.
        Returns list of similar existing ingredients.
        """
        normalized_new = re.sub(r'\s+', ' ', ingredient_name.lower().strip())
        similar_ingredients = []
        
        for existing in Ingredient.objects.all():
            normalized_existing = re.sub(r'\s+', ' ', existing.name.lower().strip())
            
            # Check for exact match (case-insensitive)
            if normalized_new == normalized_existing:
                similar_ingredients.append((existing, 1.0, 'Exact match'))
            
            # Check for high similarity
            else:
                similarity = SequenceMatcher(None, normalized_new, normalized_existing).ratio()
                if similarity > 0.8:
                    similar_ingredients.append((existing, similarity, 'Very similar'))
                elif similarity > 0.6:
                    similar_ingredients.append((existing, similarity, 'Similar'))
        
        # Sort by similarity (highest first)
        similar_ingredients.sort(key=lambda x: x[1], reverse=True)
        return similar_ingredients
