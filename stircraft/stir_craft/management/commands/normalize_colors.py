"""
Management command to normalize cocktail colors to the predefined choices.
This command maps existing free-text colors to the standardized color choices.

Usage:
    python manage.py normalize_colors
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Cocktail


class Command(BaseCommand):
    help = 'Normalize cocktail colors to predefined choices'

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
        
        # Define color mapping rules - map various text colors to standard choices
        color_mappings = {
            # Clear variations
            'clear': 'Clear',
            'transparent': 'Clear',
            'colorless': 'Clear',
            
            # White variations
            'white': 'White',
            'milky': 'White',
            'cloudy': 'White',
            
            # Yellow variations
            'yellow': 'Yellow',
            'golden': 'Gold',
            'gold': 'Gold',
            'lemon': 'Yellow',
            'pale yellow': 'Yellow',
            
            # Orange variations
            'orange': 'Orange',
            'peach': 'Orange',
            'coral': 'Orange',
            'amber': 'Amber',
            
            # Red variations
            'red': 'Red',
            'crimson': 'Red',
            'ruby': 'Red',
            'cherry': 'Red',
            'burgundy': 'Red',
            'maroon': 'Red',
            
            # Pink variations
            'pink': 'Pink',
            'rose': 'Pink',
            'blush': 'Pink',
            'salmon': 'Pink',
            'magenta': 'Pink',
            
            # Purple variations
            'purple': 'Purple',
            'violet': 'Purple',
            'lavender': 'Purple',
            'plum': 'Purple',
            
            # Blue variations
            'blue': 'Blue',
            'navy': 'Blue',
            'azure': 'Blue',
            'sky blue': 'Blue',
            'turquoise': 'Blue',
            
            # Green variations
            'green': 'Green',
            'lime': 'Green',
            'mint': 'Green',
            'emerald': 'Green',
            'olive': 'Green',
            
            # Brown variations
            'brown': 'Brown',
            'chocolate': 'Brown',
            'coffee': 'Brown',
            'tan': 'Brown',
            'caramel': 'Brown',
            
            # Black variations
            'black': 'Black',
            'dark': 'Black',
            'charcoal': 'Black',
            
            # Cream variations
            'cream': 'Cream',
            'beige': 'Cream',
            'ivory': 'Cream',
            'off-white': 'Cream',
            
            # Silver variations
            'silver': 'Silver',
            'grey': 'Silver',
            'gray': 'Silver',
        }
        
        changes_made = 0
        
        with transaction.atomic():
            # Get all cocktails with colors that need normalization
            cocktails = Cocktail.objects.all()
            
            for cocktail in cocktails:
                if not cocktail.color or not cocktail.color.strip():
                    # Set empty colors to Clear
                    old_color = cocktail.color or '(empty)'
                    new_color = 'Clear'
                    
                    if dry_run:
                        self.stdout.write(
                            f'Would change "{cocktail.name}" color from "{old_color}" to "{new_color}"'
                        )
                    else:
                        cocktail.color = new_color
                        cocktail.save()
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'Changed "{cocktail.name}" color from "{old_color}" to "{new_color}"'
                            )
                        )
                    changes_made += 1
                    continue
                
                # Check if color needs mapping
                color_lower = cocktail.color.lower().strip()
                
                if color_lower in color_mappings:
                    old_color = cocktail.color
                    new_color = color_mappings[color_lower]
                    
                    if old_color != new_color:
                        if dry_run:
                            self.stdout.write(
                                f'Would change "{cocktail.name}" color from "{old_color}" to "{new_color}"'
                            )
                        else:
                            cocktail.color = new_color
                            cocktail.save()
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Changed "{cocktail.name}" color from "{old_color}" to "{new_color}"'
                                )
                            )
                        changes_made += 1
                
                # Check if current color is already a valid choice
                elif cocktail.color not in dict(Cocktail.COLOR_CHOICES):
                    # Color doesn't match any mapping or valid choice, flag for review
                    self.stdout.write(
                        self.style.WARNING(
                            f'REVIEW NEEDED: "{cocktail.name}" has unmapped color "{cocktail.color}"'
                        )
                    )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f'DRY RUN: Would make {changes_made} changes')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully normalized {changes_made} cocktail colors')
            )
            
            # Show summary of current colors
            self.stdout.write('\n' + '='*50)
            self.stdout.write('COLOR DISTRIBUTION AFTER NORMALIZATION:')
            self.stdout.write('='*50)
            
            from collections import Counter
            color_counts = Counter()
            for cocktail in Cocktail.objects.all():
                if cocktail.color:
                    color_counts[cocktail.color] += 1
            
            for color, count in sorted(color_counts.items()):
                self.stdout.write(f'{color}: {count} cocktails')
            
            # Show any remaining unmapped colors
            unmapped_colors = []
            for cocktail in Cocktail.objects.all():
                if cocktail.color and cocktail.color not in dict(Cocktail.COLOR_CHOICES):
                    unmapped_colors.append(cocktail.color)
            
            if unmapped_colors:
                self.stdout.write('\n' + self.style.WARNING('UNMAPPED COLORS REMAINING:'))
                unique_unmapped = set(unmapped_colors)
                for color in sorted(unique_unmapped):
                    count = unmapped_colors.count(color)
                    self.stdout.write(f'  "{color}": {count} cocktail(s)')
