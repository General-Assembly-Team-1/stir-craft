"""
Management command to fix alcohol content for alcoholic ingredients.
Sets proper ABV values for spirits, liqueurs, beers, and wines that have missing or incorrect data.

Usage:
    python manage.py fix_alcohol_content
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Ingredient


class Command(BaseCommand):
    help = 'Fix alcohol content for alcoholic ingredients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Define specific ABV values for known ingredients
        specific_abv_values = {
            # High-proof spirits
            '151 proof rum': 75.5,  # 151 proof = 75.5% ABV
            'everclear': 95.0,      # Everclear is 95% ABV
            'overproof rum': 63.0,   # Typical overproof
            
            # Whiskeys and Bourbons
            'wild turkey': 40.5,     # Wild Turkey 81 proof = 40.5%
            'crown royal': 40.0,     # Standard Crown Royal
            'bourbon': 40.0,         # Standard bourbon
            'whiskey': 40.0,         # Standard whiskey
            'whisky': 40.0,          # Standard whisky
            'scotch': 40.0,          # Standard Scotch
            'blended scotch': 40.0,   # Standard blended Scotch
            'blended whiskey': 40.0,  # Standard blended whiskey
            'rye whiskey': 40.0,     # Standard rye
            'islay single malt scotch': 43.0,  # Typical Islay strength
            
            # Rums
            'rum': 40.0,             # Standard rum
            'dark rum': 40.0,        # Standard dark rum
            'light rum': 40.0,       # Standard light rum
            
            # Vodkas
            'vodka': 40.0,           # Standard vodka
            'absolut vodka': 40.0,   # Absolut is 40%
            
            # Gins
            'gin': 40.0,             # Standard gin
            'sloe gin': 25.0,        # Sloe gin is lower
            
            # Tequila
            'tequila': 40.0,         # Standard tequila
            
            # Brandies
            'brandy': 40.0,          # Standard brandy
            'cognac': 40.0,          # Standard cognac
            'apricot brandy': 35.0,  # Fruit brandies often lower
            'blackberry brandy': 35.0,  # Fruit brandies often lower
            'applejack': 40.0,       # Apple brandy
            
            # Liqueurs (generally lower ABV)
            'amaretto': 24.0,        # Typical amaretto
            'kahlua': 20.0,          # Coffee liqueur
            'baileys irish cream': 17.0,  # Cream liqueur
            'sambuca': 38.0,         # Anise liqueur
            'galliano': 42.5,        # Herbal liqueur
            'cointreau': 40.0,       # Premium orange liqueur
            'grand marnier': 40.0,   # Cognac-based orange liqueur
            'triple sec': 30.0,      # Orange liqueur
            'blue curacao': 25.0,    # Colored liqueur
            'curacao': 25.0,         # Orange liqueur
            'midori': 20.0,          # Melon liqueur
            'peach schnapps': 23.0,  # Fruit schnapps
            'creme de': 25.0,        # Generic crème liqueurs
            'crème de': 25.0,        # Generic crème liqueurs
            'chartreuse': 55.0,      # Very high proof herbal liqueur
            'green chartreuse': 55.0,  # Green Chartreuse
            'yellow chartreuse': 40.0,  # Yellow Chartreuse
            'campari': 25.0,         # Bitter liqueur
            'aperol': 11.0,          # Lower proof aperitif
            'vermouth': 18.0,        # Fortified wine
            'dry vermouth': 18.0,    # Dry vermouth
            'sweet vermouth': 18.0,  # Sweet vermouth
            'red vermouth': 18.0,    # Red vermouth
            'dubonnet': 19.0,        # Fortified wine aperitif
            'fernet': 39.0,          # Bitter herbal liqueur
            'jägermeister': 35.0,    # Herbal liqueur
            'limoncello': 30.0,      # Lemon liqueur
            
            # Wines
            'wine': 12.5,            # Average wine
            'red wine': 13.5,        # Red wine average
            'white wine': 12.0,      # White wine average
            'champagne': 12.0,       # Champagne
            'prosecco': 11.0,        # Prosecco
            'sherry': 17.0,          # Fortified wine
            'port': 20.0,            # Fortified wine
            'madeira': 18.0,         # Fortified wine
            'marsala': 17.0,         # Fortified wine
            'sake': 15.0,            # Rice wine
            
            # Beers
            'beer': 5.0,             # Average beer
            'ale': 5.5,              # Ale
            'lager': 4.5,            # Lager
            'stout': 6.0,            # Stout
            'porter': 5.5,           # Porter
            'corona': 4.6,           # Corona beer
            'guinness': 4.2,         # Guinness stout
        }
        
        # Default ABV values by category
        category_defaults = {
            'spirit': 40.0,          # Most spirits are 40% ABV
            'liqueur': 25.0,         # Most liqueurs are 20-30% ABV
            'wine': 12.5,            # Most wines are 10-15% ABV
            'beer': 5.0,             # Most beers are 4-6% ABV
        }
        
        changes_made = 0
        
        with transaction.atomic():
            # Get all alcoholic ingredients that need fixing
            alcoholic_types = ['spirit', 'liqueur', 'wine', 'beer']
            ingredients = Ingredient.objects.filter(ingredient_type__in=alcoholic_types)
            
            for ingredient in ingredients:
                old_abv = ingredient.alcohol_content or 0
                new_abv = None
                reason = ""
                
                # Check for specific ABV values first
                name_lower = ingredient.name.lower()
                for key, abv in specific_abv_values.items():
                    if key.lower() in name_lower:
                        new_abv = abv
                        reason = f"specific value for '{key}'"
                        break
                
                # If no specific value found, use category default
                if new_abv is None:
                    if ingredient.ingredient_type in category_defaults:
                        new_abv = category_defaults[ingredient.ingredient_type]
                        reason = f"category default for {ingredient.ingredient_type}"
                
                # Only update if ABV is 0 or significantly different
                if new_abv and (old_abv == 0 or abs(old_abv - new_abv) > 5):
                    if dry_run:
                        self.stdout.write(
                            f'Would change "{ingredient.name}" ABV from {old_abv}% to {new_abv}% ({reason})'
                        )
                    else:
                        ingredient.alcohol_content = new_abv
                        ingredient.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Changed "{ingredient.name}" ABV from {old_abv}% to {new_abv}% ({reason})'
                            )
                        )
                    changes_made += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would make {changes_made} changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {changes_made} ingredient ABV values')
            )
            
            # Show summary of ABV ranges by category
            self.stdout.write('\n' + '='*50)
            self.stdout.write('ABV SUMMARY BY CATEGORY:')
            self.stdout.write('='*50)
            
            for category in alcoholic_types:
                ingredients_in_category = Ingredient.objects.filter(ingredient_type=category)
                if ingredients_in_category.exists():
                    abvs = [ing.alcohol_content for ing in ingredients_in_category if ing.alcohol_content]
                    if abvs:
                        min_abv = min(abvs)
                        max_abv = max(abvs)
                        avg_abv = sum(abvs) / len(abvs)
                        self.stdout.write(
                            f'{category.title()}: {len(abvs)} ingredients, '
                            f'ABV range {min_abv:.1f}%-{max_abv:.1f}% (avg: {avg_abv:.1f}%)'
                        )
            
            # Show any remaining zero ABV alcoholic ingredients
            zero_abv_alcoholic = Ingredient.objects.filter(
                ingredient_type__in=alcoholic_types,
                alcohol_content=0
            )
            if zero_abv_alcoholic.exists():
                self.stdout.write('\n' + self.style.WARNING('REMAINING ZERO ABV INGREDIENTS:'))
                for ing in zero_abv_alcoholic:
                    self.stdout.write(f'  {ing.name} ({ing.ingredient_type})')

    def get_abv_from_name(self, name):
        """Extract ABV from ingredient name if possible."""
        name_lower = name.lower()
        
        # Look for proof indicators
        if '151 proof' in name_lower:
            return 75.5  # 151 proof = 75.5% ABV
        elif '100 proof' in name_lower:
            return 50.0  # 100 proof = 50% ABV
        elif 'overproof' in name_lower:
            return 63.0  # Typical overproof
        elif 'navy strength' in name_lower:
            return 57.0  # Navy strength gin
        
        return None
