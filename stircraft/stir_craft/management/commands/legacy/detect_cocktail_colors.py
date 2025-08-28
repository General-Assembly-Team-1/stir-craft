"""
Management command to detect and set cocktail colors based on their ingredients.
Uses the same intelligent color detection logic as the seeding command.

Usage:
    python manage.py detect_cocktail_colors
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Cocktail, RecipeComponent


class Command(BaseCommand):
    help = 'Detect and set cocktail colors based on their ingredients'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update colors even if cocktail already has a non-Clear color',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Color mapping based on ingredients (same as seeding command)
        color_ingredients = {
            'red': [
                'cranberry', 'cherry', 'grenadine', 'red wine', 'strawberry',
                'raspberry', 'pomegranate', 'red vermouth', 'campari',
                'aperol', 'cherry juice', 'cranberry juice'
            ],
            'orange': [
                'orange', 'orange juice', 'orange liqueur', 'cointreau',
                'grand marnier', 'triple sec', 'aperol', 'orange bitters',
                'orange peel', 'mandarin', 'tangerine'
            ],
            'yellow': [
                'lemon', 'lemon juice', 'limoncello', 'yellow chartreuse',
                'banana', 'pineapple', 'pineapple juice', 'lemon peel',
                'champagne', 'white wine', 'ginger', 'honey'
            ],
            'green': [
                'lime', 'lime juice', 'green chartreuse', 'midori',
                'apple', 'green apple', 'mint', 'basil', 'cucumber',
                'absinthe', 'green tea', 'matcha'
            ],
            'purple': [
                'grape', 'grape juice', 'blackberry', 'blueberry',
                'violet', 'lavender', 'purple'
            ],
            'pink': [
                'rose', 'pink grapefruit', 'watermelon', 'pink lemonade',
                'rosé', 'pink gin', 'hibiscus'
            ],
            'blue': [
                'blue curacao', 'blue', 'blueberry'
            ],
            'brown': [
                'coffee', 'espresso', 'kahlua', 'chocolate', 'cocoa',
                'cola', 'whiskey', 'bourbon', 'rum', 'brandy'
            ],
            'clear': [
                'vodka', 'gin', 'white rum', 'silver tequila', 'sake',
                'water', 'soda water', 'club soda'
            ]
        }
        
        color_mapping = {
            'red': 'Red',
            'orange': 'Orange', 
            'yellow': 'Yellow',
            'green': 'Green',
            'blue': 'Blue',
            'purple': 'Purple',
            'pink': 'Pink',
            'brown': 'Brown',
            'clear': 'Clear'
        }
        
        changes_made = 0
        
        with transaction.atomic():
            # Get cocktails to process
            if force:
                cocktails = Cocktail.objects.all()
            else:
                cocktails = Cocktail.objects.filter(color='Clear')
            
            for cocktail in cocktails:
                # Get all ingredient names for this cocktail
                ingredients = [
                    component.ingredient.name.lower() 
                    for component in cocktail.components.all()
                ]
                
                if not ingredients:
                    continue
                
                # Check ingredients for color indicators
                detected_colors = set()
                for color, color_ingredients_list in color_ingredients.items():
                    for ingredient in ingredients:
                        if any(color_ing in ingredient for color_ing in color_ingredients_list):
                            detected_colors.add(color)
                
                # Determine the primary color
                old_color = cocktail.color
                new_color = None
                
                # Priority order for color assignment
                primary_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink']
                for color in primary_colors:
                    if color in detected_colors:
                        new_color = color_mapping[color]
                        break
                
                # Handle special cases
                if not new_color:
                    if 'brown' in detected_colors:
                        new_color = 'Brown'
                    else:
                        new_color = 'Clear'
                
                # Only update if color changed
                if new_color != old_color:
                    if dry_run:
                        self.stdout.write(
                            f'Would change "{cocktail.name}" color from "{old_color}" to "{new_color}"'
                        )
                        self.stdout.write(f'  Ingredients: {", ".join(ingredients[:3])}...')
                        self.stdout.write(f'  Detected colors: {", ".join(sorted(detected_colors))}')
                    else:
                        cocktail.color = new_color
                        cocktail.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Changed "{cocktail.name}" color from "{old_color}" to "{new_color}"'
                            )
                        )
                    changes_made += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would make {changes_made} changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {changes_made} cocktail colors')
            )
            
            # Show summary of current colors
            self.stdout.write('\n' + '='*50)
            self.stdout.write('COLOR DISTRIBUTION AFTER DETECTION:')
            self.stdout.write('='*50)
            
            from collections import Counter
            color_counts = Counter()
            for cocktail in Cocktail.objects.all():
                if cocktail.color:
                    color_counts[cocktail.color] += 1
            
            for color, count in sorted(color_counts.items()):
                self.stdout.write(f'{color}: {count} cocktails')
