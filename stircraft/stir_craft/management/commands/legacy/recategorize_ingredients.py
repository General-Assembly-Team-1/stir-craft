"""
Management command to recategorize ingredients based on their names.
This command fixes ingredients that were misclassified as 'other' and places them
in the correct categories.

Usage:
    python manage.py recategorize_ingredients
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Ingredient


class Command(BaseCommand):
    help = 'Recategorize ingredients that were misclassified'

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
        
        # Define categorization rules
        categorization_rules = {
            'spirit': [
                # Whiskeys
                'whiskey', 'whisky', 'bourbon', 'rye', 'scotch', 'crown royal',
                # Brandies
                'brandy', 'cognac', 'armagnac', 'calvados', 'applejack',
                # Rums
                'rum', 'bacardi',
                # Gins
                'gin',
                # Vodkas
                'vodka', 'absolut',
                # Tequilas
                'tequila', 'mezcal',
                # Others
                'everclear', 'grain alcohol',
            ],
            'liqueur': [
                'creme de', 'crème de', 'amaretto', 'cointreau', 'grand marnier',
                'kahlua', 'baileys', 'sambuca', 'galliano', 'chartreuse',
                'benedictine', 'drambuie', 'frangelico', 'midori', 'peach schnapps',
                'triple sec', 'curacao', 'campari', 'aperol', 'st-germain',
                'vermouth', 'dry vermouth', 'sweet vermouth', 'dubonnet',
                'fernet', 'cynar', 'averna', 'jägermeister', 'limoncello',
            ],
            'wine': [
                'wine', 'champagne', 'prosecco', 'cava', 'sherry', 'port',
                'madeira', 'marsala', 'sake', 'riesling', 'chardonnay',
            ],
            'beer': [
                'beer', 'ale', 'lager', 'stout', 'porter', 'corona', 'guinness',
            ],
            'soda': [
                'tonic', 'soda', 'cola', 'coke', 'pepsi', 'sprite', '7up',
                'ginger ale', 'club soda', 'seltzer', 'sparkling water',
                'ginger beer', 'root beer',
            ],
            'dairy': [
                'cream', 'milk', 'egg white', 'egg', 'heavy cream', 'half and half',
                'condensed milk', 'coconut cream',
            ],
            'garnish': [
                'lemon', 'lime', 'orange', 'cherry', 'olive', 'onion',
                'mint', 'basil', 'rosemary', 'thyme', 'celery', 'pickle',
                'salt', 'sugar', 'cinnamon', 'nutmeg', 'coffee bean',
                'peppercorn', 'twist', 'wheel', 'wedge', 'peel',
                'maraschino cherry', 'cocktail onion',
            ],
        }
        
        changes_made = 0
        
        with transaction.atomic():
            for new_category, keywords in categorization_rules.items():
                for keyword in keywords:
                    # Find ingredients that contain this keyword (case-insensitive)
                    ingredients = Ingredient.objects.filter(
                        name__icontains=keyword,
                        ingredient_type='other'
                    )
                    
                    for ingredient in ingredients:
                        old_category = ingredient.ingredient_type
                        ingredient.ingredient_type = new_category
                        
                        if dry_run:
                            self.stdout.write(
                                f'Would change "{ingredient.name}" from {old_category} to {new_category}'
                            )
                        else:
                            ingredient.save()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Changed "{ingredient.name}" from {old_category} to {new_category}'
                                )
                            )
                        changes_made += 1
        
        # Handle special cases that need manual review
        special_cases = Ingredient.objects.filter(
            ingredient_type='other',
            name__in=[
                'Blackberries', 'Cocoa powder', 'Espresso', 'Honey',
                'Vanilla', 'Chocolate', 'Mint leaves', 'Cucumber',
            ]
        )
        
        for ingredient in special_cases:
            # Categorize fruits and vegetables as garnish
            if any(word in ingredient.name.lower() for word in ['berries', 'cucumber', 'mint']):
                category = 'garnish'
            # Categorize powders and syrups
            elif any(word in ingredient.name.lower() for word in ['powder', 'honey', 'vanilla']):
                category = 'syrup'
            # Coffee and chocolate
            elif any(word in ingredient.name.lower() for word in ['espresso', 'chocolate', 'cocoa']):
                category = 'garnish'
            else:
                continue
                
            if dry_run:
                self.stdout.write(
                    f'Would change "{ingredient.name}" from other to {category}'
                )
            else:
                ingredient.ingredient_type = category
                ingredient.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Changed "{ingredient.name}" from other to {category}'
                    )
                )
            changes_made += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would make {changes_made} changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully recategorized {changes_made} ingredients')
            )
            
            # Show summary of current categories
            self.stdout.write('\n' + '='*50)
            self.stdout.write('INGREDIENT CATEGORIES SUMMARY:')
            self.stdout.write('='*50)
            
            from collections import Counter
            ingredient_counts = Counter()
            for ingredient in Ingredient.objects.all():
                ingredient_counts[ingredient.get_ingredient_type_display()] += 1
            
            for category, count in sorted(ingredient_counts.items()):
                self.stdout.write(f'{category}: {count} ingredients')
