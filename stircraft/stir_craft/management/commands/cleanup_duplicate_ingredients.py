"""
Management command to clean up duplicate ingredients in the database.

This command identifies ingredients with the same name (case-insensitive) and 
merges them, keeping the one with the most complete information.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from stir_craft.models import Ingredient, RecipeComponent
from collections import defaultdict


class Command(BaseCommand):
    help = 'Clean up duplicate ingredients in the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--merge',
            action='store_true',
            help='Actually merge duplicates (requires confirmation)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        merge = options['merge']
        
        if not dry_run and not merge:
            self.stdout.write(
                self.style.WARNING(
                    'Use --dry-run to see what would be changed, or --merge to actually merge duplicates'
                )
            )
            return

        # Find duplicate ingredients (case-insensitive)
        duplicates = defaultdict(list)
        for ingredient in Ingredient.objects.all():
            duplicates[ingredient.name.lower()].append(ingredient)
        
        # Filter to only actual duplicates
        actual_duplicates = {name: ingredients for name, ingredients in duplicates.items() 
                           if len(ingredients) > 1}
        
        if not actual_duplicates:
            self.stdout.write(self.style.SUCCESS('No duplicate ingredients found!'))
            return
        
        self.stdout.write(f'Found {len(actual_duplicates)} sets of duplicate ingredients:')
        
        for name_lower, ingredients in actual_duplicates.items():
            self.stdout.write(f'\n"{name_lower}" has {len(ingredients)} duplicates:')
            
            for i, ing in enumerate(ingredients):
                recipe_count = RecipeComponent.objects.filter(ingredient=ing).count()
                self.stdout.write(
                    f'  {i+1}. "{ing.name}" ({ing.get_ingredient_type_display()}) '
                    f'- Used in {recipe_count} recipes'
                    f'{" - Has description" if ing.description else ""}'
                    f'{f" - {ing.flavor_tags.count()} flavor tags" if ing.flavor_tags.count() > 0 else ""}'
                )
            
            if merge:
                # Choose the best ingredient to keep
                best_ingredient = self.choose_best_ingredient(ingredients)
                others = [ing for ing in ingredients if ing.id != best_ingredient.id]
                
                self.stdout.write(f'  → Keeping: "{best_ingredient.name}" (ID: {best_ingredient.id})')
                
                # Merge the others into the best one
                with transaction.atomic():
                    for other in others:
                        # Move all recipe components to the best ingredient
                        RecipeComponent.objects.filter(ingredient=other).update(ingredient=best_ingredient)
                        
                        # Merge flavor tags
                        for tag in other.flavor_tags.all():
                            best_ingredient.flavor_tags.add(tag)
                        
                        # Update description if the best one doesn't have one
                        if not best_ingredient.description and other.description:
                            best_ingredient.description = other.description
                            best_ingredient.save()
                        
                        self.stdout.write(f'  → Deleted: "{other.name}" (ID: {other.id})')
                        other.delete()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('\nThis was a dry run. Use --merge to actually merge duplicates.')
            )
        elif merge:
            self.stdout.write(self.style.SUCCESS('\nDuplicate cleanup completed!'))

    def choose_best_ingredient(self, ingredients):
        """
        Choose the best ingredient to keep based on:
        1. Most complete information (description, tags)
        2. Most usage in recipes
        3. Proper capitalization
        """
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
            score += recipe_count * 2
            
            # Score for proper capitalization (title case)
            if ing.name.istitle():
                score += 3
            
            # Score for being created earlier (prefer original)
            # Newer ingredients get lower score
            score -= (ing.id % 100)  # Simple way to prefer earlier IDs
            
            scored_ingredients.append((score, ing))
        
        # Sort by score descending and return the best
        scored_ingredients.sort(key=lambda x: x[0], reverse=True)
        return scored_ingredients[0][1]
