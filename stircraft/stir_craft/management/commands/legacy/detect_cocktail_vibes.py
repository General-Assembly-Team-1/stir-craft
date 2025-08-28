"""
Management command to detect and set cocktail vibe tags based on their ingredients,
names, and descriptions.

Usage:
    python manage.py detect_cocktail_vibes
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Cocktail, RecipeComponent


class Command(BaseCommand):
    help = 'Detect and set cocktail vibe tags based on their ingredients and characteristics'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Update vibes even if cocktail already has vibe tags',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        # Vibe mapping based on ingredients, names, and characteristics
        vibe_indicators = {
            'tropical': {
                'ingredients': [
                    'pineapple', 'coconut', 'mango', 'passion fruit', 'rum',
                    'banana', 'papaya', 'guava', 'lychee', 'coconut cream',
                    'coconut milk', 'tiki', 'mai tai', 'pina colada'
                ],
                'name_keywords': [
                    'tropical', 'tiki', 'hawaiian', 'caribbean', 'island',
                    'beach', 'paradise', 'bahama', 'miami', 'key west'
                ]
            },
            'cozy': {
                'ingredients': [
                    'cream', 'milk', 'butter', 'cinnamon', 'nutmeg',
                    'vanilla', 'chocolate', 'cocoa', 'coffee', 'espresso',
                    'irish cream', 'bailey', 'kahlua', 'brandy', 'cognac'
                ],
                'name_keywords': [
                    'hot', 'warm', 'toddy', 'coffee', 'irish', 'winter',
                    'cozy', 'creamy', 'comfort'
                ],
                'served_hot': True
            },
            'summer': {
                'ingredients': [
                    'watermelon', 'peach', 'strawberry', 'basil', 'cucumber',
                    'mint', 'lemonade', 'iced tea', 'sangria', 'spritz',
                    'prosecco', 'rosé'
                ],
                'name_keywords': [
                    'summer', 'refreshing', 'cooler', 'spritz', 'sangria',
                    'lemonade', 'frozen', 'iced', 'breeze'
                ]
            },
            'fall': {
                'ingredients': [
                    'apple', 'pumpkin', 'cinnamon', 'nutmeg', 'maple',
                    'fireball', 'whiskey', 'bourbon', 'cranberry',
                    'pomegranate', 'orange', 'clove'
                ],
                'name_keywords': [
                    'fall', 'autumn', 'harvest', 'spice', 'apple',
                    'pumpkin', 'cranberry', 'thanksgiving'
                ]
            },
            'frozen': {
                'ingredients': [
                    'ice', 'frozen', 'slush', 'granita', 'sorbet'
                ],
                'name_keywords': [
                    'frozen', 'slush', 'granita', 'blended', 'smoothie',
                    'ice', 'frosé'
                ],
                'description_keywords': [
                    'blend', 'blender', 'frozen', 'ice', 'slush'
                ]
            },
            'elegant': {
                'ingredients': [
                    'champagne', 'prosecco', 'gin', 'vermouth', 'bitters',
                    'cointreau', 'grand marnier', 'cognac', 'dry vermouth'
                ],
                'name_keywords': [
                    'martini', 'manhattan', 'negroni', 'french', 'classic',
                    'elegant', 'sophisticated', 'royal', 'imperial'
                ]
            },
            'party': {
                'ingredients': [
                    'vodka', 'shots', 'energy drink', 'juice', 'sour mix'
                ],
                'name_keywords': [
                    'shot', 'bomb', 'party', 'dance', 'club', 'wild',
                    'crazy', 'kamikaze', 'slammer'
                ]
            },
            'refreshing': {
                'ingredients': [
                    'mint', 'cucumber', 'lime', 'soda water', 'tonic',
                    'ginger beer', 'sparkling water'
                ],
                'name_keywords': [
                    'mojito', 'mule', 'cooler', 'spritzer', 'fizz',
                    'refreshing', 'light', 'crisp'
                ]
            }
        }
        
        changes_made = 0
        
        with transaction.atomic():
            # Get cocktails to process
            if force:
                cocktails = Cocktail.objects.all()
            else:
                # Only process cocktails with no vibe tags
                cocktails = Cocktail.objects.filter(vibe_tags__isnull=True).distinct()
            
            for cocktail in cocktails:
                # Get ingredient names for this cocktail
                ingredients = [
                    component.ingredient.name.lower() 
                    for component in cocktail.components.all()
                ]
                
                if not ingredients:
                    continue
                
                # Check name and description
                name_text = cocktail.name.lower()
                description_text = (cocktail.description or '').lower()
                instructions_text = (cocktail.instructions or '').lower()
                
                # Detect vibes
                detected_vibes = set()
                
                for vibe, indicators in vibe_indicators.items():
                    vibe_score = 0
                    
                    # Check ingredients
                    if 'ingredients' in indicators:
                        for ingredient in ingredients:
                            if any(vibe_ing in ingredient for vibe_ing in indicators['ingredients']):
                                vibe_score += 2  # Strong indicator
                    
                    # Check name keywords
                    if 'name_keywords' in indicators:
                        for keyword in indicators['name_keywords']:
                            if keyword in name_text:
                                vibe_score += 3  # Very strong indicator
                    
                    # Check description keywords
                    if 'description_keywords' in indicators:
                        for keyword in indicators['description_keywords']:
                            if keyword in description_text or keyword in instructions_text:
                                vibe_score += 2
                    
                    # Special checks
                    if vibe == 'cozy' and indicators.get('served_hot'):
                        # Check if it's a hot drink
                        hot_keywords = ['hot', 'warm', 'toddy', 'coffee', 'tea']
                        if any(keyword in name_text or keyword in instructions_text 
                               for keyword in hot_keywords):
                            vibe_score += 3
                    
                    # Add vibe if score is high enough
                    if vibe_score >= 2:
                        detected_vibes.add(vibe)
                
                # Apply vibes
                if detected_vibes:
                    current_vibes = set(cocktail.vibe_tags.names())
                    new_vibes = detected_vibes - current_vibes
                    
                    if new_vibes or force:
                        if dry_run:
                            self.stdout.write(
                                f'Would add vibes to "{cocktail.name}": {", ".join(sorted(detected_vibes))}'
                            )
                            self.stdout.write(f'  Ingredients: {", ".join(ingredients[:3])}...')
                        else:
                            # Add new vibe tags
                            for vibe in new_vibes:
                                cocktail.vibe_tags.add(vibe)
                            
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Added vibes to "{cocktail.name}": {", ".join(sorted(new_vibes))}'
                                )
                            )
                        changes_made += 1
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would make {changes_made} changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully updated {changes_made} cocktails with vibe tags')
            )
            
            # Show summary of vibe distribution
            self.stdout.write('\n' + '='*50)
            self.stdout.write('VIBE DISTRIBUTION AFTER DETECTION:')
            self.stdout.write('='*50)
            
            from collections import Counter
            vibe_counts = Counter()
            
            for cocktail in Cocktail.objects.all():
                for vibe in cocktail.vibe_tags.names():
                    vibe_counts[vibe] += 1
            
            if vibe_counts:
                for vibe, count in sorted(vibe_counts.items()):
                    self.stdout.write(f'{vibe}: {count} cocktails')
            else:
                self.stdout.write('No vibe tags found')
