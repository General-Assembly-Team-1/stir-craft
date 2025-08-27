"""
Consolidated Ingredient Maintenance Command

This command consolidates multiple ingredient-related maintenance tasks
into a single, comprehensive command that can fix multiple issues at once.

Usage:
    python manage.py maintain_ingredients --dry-run
    python manage.py maintain_ingredients --fix-duplicates --fix-alcohol --fix-categories
    python manage.py maintain_ingredients --all --verbose
"""

from django.core.management.base import CommandError
from django.db import transaction
from ...utils.command_base import DataMaintenanceCommand
from ...utils.ingredient_utils import (
    IngredientClassifier, 
    IngredientDuplicateDetector, 
    IngredientNormalizer
)
from ...models import Ingredient


class Command(DataMaintenanceCommand):
    help = 'Consolidated ingredient maintenance: duplicates, categories, alcohol content, and normalization'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        # Specific maintenance tasks
        parser.add_argument(
            '--fix-duplicates',
            action='store_true',
            help='Find and merge duplicate ingredients',
        )
        parser.add_argument(
            '--fix-categories',
            action='store_true', 
            help='Fix ingredient categorization based on names',
        )
        parser.add_argument(
            '--fix-alcohol',
            action='store_true',
            help='Fix missing or incorrect alcohol content values',
        )
        parser.add_argument(
            '--normalize-names',
            action='store_true',
            help='Standardize ingredient name formatting',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all maintenance tasks',
        )

    def handle(self, *args, **options):
        """Execute the consolidated ingredient maintenance process."""
        self.setup_command(options)
        
        # Determine which tasks to run
        tasks = []
        if options['all']:
            tasks = ['duplicates', 'categories', 'alcohol', 'names']
        else:
            if options['fix_duplicates']:
                tasks.append('duplicates')
            if options['fix_categories']:
                tasks.append('categories')
            if options['fix_alcohol']:
                tasks.append('alcohol')
            if options['normalize_names']:
                tasks.append('names')
        
        if not tasks:
            raise CommandError("Please specify at least one maintenance task or use --all")
        
        self.log_info(f"Starting ingredient maintenance with tasks: {', '.join(tasks)}")
        
        try:
            # Execute tasks in optimal order
            if 'duplicates' in tasks:
                self._fix_duplicates()
            
            if 'categories' in tasks:
                self._fix_categories()
            
            if 'alcohol' in tasks:
                self._fix_alcohol_content()
            
            if 'names' in tasks:
                self._normalize_names()
            
            self.print_summary()
            
        except Exception as e:
            self.log_error(f"Maintenance failed: {str(e)}")
            raise CommandError(f"Ingredient maintenance failed: {str(e)}")

    def _fix_duplicates(self):
        """Find and merge duplicate ingredients."""
        self.log_info("🔍 Searching for duplicate ingredients...")
        
        duplicates = IngredientDuplicateDetector.find_duplicates()
        
        if not duplicates:
            self.log_success("No duplicate ingredients found")
            return
        
        self.log_warning(f"Found {len(duplicates)} groups of potential duplicates")
        
        for normalized_name, ingredient_list in duplicates.items():
            if len(ingredient_list) <= 1:
                continue
            
            self.log_verbose(f"Processing duplicates for: {normalized_name}")
            
            # Choose primary ingredient (most complete information)
            primary = max(ingredient_list, key=lambda ing: (
                len(ing.description),
                bool(ing.alcohol_content),
                ing.ingredient_type != 'other'
            ))
            
            others = [ing for ing in ingredient_list if ing.id != primary.id]
            
            if self.dry_run:
                self.log_info(f"Would merge {len(others)} duplicates into: {primary.name}")
            else:
                with transaction.atomic():
                    IngredientDuplicateDetector.merge_ingredients(primary, others)
                    self.changes_made += len(others)
                    self.log_success(f"Merged {len(others)} duplicates into: {primary.name}")

    def _fix_categories(self):
        """Fix ingredient categorization."""
        self.log_info("🏷️ Fixing ingredient categories...")
        
        # Find ingredients with 'other' category that could be better classified
        other_ingredients = Ingredient.objects.filter(ingredient_type='other')
        fixed_count = 0
        
        for ingredient in other_ingredients:
            new_category = IngredientClassifier.classify_ingredient(ingredient.name)
            
            if new_category != 'other':
                self.log_verbose(f"Reclassifying '{ingredient.name}': other → {new_category}")
                
                if not self.dry_run:
                    ingredient.ingredient_type = new_category
                    ingredient.save()
                
                fixed_count += 1
                self.changes_made += 1
        
        if fixed_count > 0:
            self.log_success(f"Fixed categorization for {fixed_count} ingredients")
        else:
            self.log_success("All ingredients are properly categorized")

    def _fix_alcohol_content(self):
        """Fix missing or incorrect alcohol content values."""
        self.log_info("🍺 Fixing alcohol content values...")
        
        # Find ingredients missing alcohol content
        ingredients_needing_alcohol = Ingredient.objects.filter(
            alcohol_content__isnull=True
        )
        
        fixed_count = 0
        
        for ingredient in ingredients_needing_alcohol:
            estimated_alcohol = IngredientClassifier.estimate_alcohol_content(
                ingredient.name, 
                ingredient.ingredient_type
            )
            
            if estimated_alcohol > 0:
                self.log_verbose(f"Setting alcohol content for '{ingredient.name}': {estimated_alcohol}%")
                
                if not self.dry_run:
                    ingredient.alcohol_content = estimated_alcohol
                    ingredient.save()
                
                fixed_count += 1
                self.changes_made += 1
        
        if fixed_count > 0:
            self.log_success(f"Fixed alcohol content for {fixed_count} ingredients")
        else:
            self.log_success("All ingredients have proper alcohol content values")

    def _normalize_names(self):
        """Normalize ingredient name formatting."""
        self.log_info("✨ Normalizing ingredient names...")
        
        fixed_count = 0
        
        for ingredient in Ingredient.objects.all():
            standardized_name = IngredientNormalizer.standardize_name(ingredient.name)
            
            if standardized_name != ingredient.name:
                self.log_verbose(f"Normalizing name: '{ingredient.name}' → '{standardized_name}'")
                
                if not self.dry_run:
                    ingredient.name = standardized_name
                    ingredient.save()
                
                fixed_count += 1
                self.changes_made += 1
        
        if fixed_count > 0:
            self.log_success(f"Normalized {fixed_count} ingredient names")
        else:
            self.log_success("All ingredient names are properly formatted")
