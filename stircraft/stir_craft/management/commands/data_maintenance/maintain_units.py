"""
Consolidated Unit Maintenance Command

This command handles all unit-related maintenance tasks including standardization,
conversion, validation, and consistency checks across the recipe database.

Mathematical Framework:
Implements precise unit conversion algorithms with international standards
for consistent measurement representation throughout the application.

Usage:
    python manage.py maintain_units --dry-run
    python manage.py maintain_units --standardize --validate
    python manage.py maintain_units --all --verbose
"""

from django.core.management.base import CommandError
from django.db import transaction
from decimal import Decimal, InvalidOperation
from ...utils.command_base import DataMaintenanceCommand
from ...models import RecipeComponent


class Command(DataMaintenanceCommand):
    help = 'Consolidated unit maintenance: standardization, validation, and conversion'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        parser.add_argument(
            '--standardize',
            action='store_true',
            help='Convert all units to standardized metric (ml) format',
        )
        parser.add_argument(
            '--validate',
            action='store_true',
            help='Validate unit consistency and detect anomalies',
        )
        parser.add_argument(
            '--fix-amounts',
            action='store_true',
            help='Fix obviously incorrect amount values',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all unit maintenance tasks',
        )

    def handle(self, *args, **options):
        """Execute the consolidated unit maintenance process."""
        self.setup_command(options)
        
        # Determine which tasks to run
        tasks = []
        if options['all']:
            tasks = ['standardize', 'validate', 'fix_amounts']
        else:
            if options['standardize']:
                tasks.append('standardize')
            if options['validate']:
                tasks.append('validate')
            if options['fix_amounts']:
                tasks.append('fix_amounts')
        
        if not tasks:
            raise CommandError("Please specify at least one maintenance task or use --all")
        
        self.log_info(f"Starting unit maintenance with tasks: {', '.join(tasks)}")
        
        try:
            if 'standardize' in tasks:
                self._standardize_units()
            
            if 'validate' in tasks:
                self._validate_units()
            
            if 'fix_amounts' in tasks:
                self._fix_amounts()
            
            self.print_summary()
            
        except Exception as e:
            self.log_error(f"Unit maintenance failed: {str(e)}")
            raise CommandError(f"Unit maintenance failed: {str(e)}")

    def _standardize_units(self):
        """
        Convert all measurements to standardized metric units (milliliters).
        
        Algorithm:
        1. Identify components using non-standard units
        2. Apply precise conversion factors
        3. Update database with converted values
        4. Maintain referential integrity
        
        Conversion Factors (High Precision):
        - 1 fluid ounce = 29.5735 milliliters (US standard)
        - 1 teaspoon = 4.92892 milliliters (US standard)
        - 1 tablespoon = 14.7868 milliliters (US standard)
        - 1 cup = 236.588 milliliters (US standard)
        """
        self.log_info("📏 Standardizing measurement units to metric...")
        
        # High-precision conversion factors
        conversion_factors = {
            'oz': 29.5735,      # US fluid ounce to milliliters
            'fl oz': 29.5735,   # Explicit fluid ounce
            'tsp': 4.92892,     # US teaspoon to milliliters
            'tbsp': 14.7868,    # US tablespoon to milliliters
            'cup': 236.588,     # US cup to milliliters
            'pint': 473.176,    # US pint to milliliters
            'quart': 946.353,   # US quart to milliliters
        }
        
        total_converted = 0
        
        for unit, factor in conversion_factors.items():
            components = RecipeComponent.objects.filter(unit__iexact=unit)
            count = components.count()
            
            if count > 0:
                self.log_info(f"   Converting {count} components from '{unit}' to 'ml'")
                self.log_verbose(f"   Using conversion factor: {factor} ml per {unit}")
                
                with transaction.atomic():
                    for component in components:
                        try:
                            old_amount = component.amount
                            # Apply conversion with precision rounding
                            new_amount = round(float(old_amount) * factor, 2)
                            
                            self.log_verbose(
                                f"   {component.cocktail.name}: {old_amount} {unit} → {new_amount} ml"
                            )
                            
                            if not self.dry_run:
                                component.amount = Decimal(str(new_amount))
                                component.unit = 'ml'
                                component.save()
                            
                            total_converted += 1
                            self.changes_made += 1
                            
                        except (ValueError, InvalidOperation) as e:
                            self.log_error(f"Error converting {component.id}: {str(e)}")
                            continue
        
        if total_converted > 0:
            self.log_success(f"Standardized {total_converted} measurements to metric units")
        else:
            self.log_success("All measurements already use standard units")

    def _validate_units(self):
        """
        Validate unit consistency and detect anomalies.
        
        Validation Checks:
        1. Detect unreasonable amounts (e.g., 1000ml of bitters)
        2. Find inconsistent unit usage within recipes
        3. Identify unknown or invalid units
        4. Check for missing units
        """
        self.log_info("🔍 Validating unit consistency and amounts...")
        
        issues_found = 0
        
        # Check for missing units
        no_unit = RecipeComponent.objects.filter(unit__isnull=True) | RecipeComponent.objects.filter(unit='')
        if no_unit.exists():
            count = no_unit.count()
            self.log_warning(f"Found {count} components with missing units")
            issues_found += count
            
            for component in no_unit:
                self.log_verbose(f"   Missing unit: {component.cocktail.name} - {component.ingredient.name}")
        
        # Check for unreasonable amounts
        unreasonable_amounts = []
        
        # Define reasonable ranges for different unit types
        reasonable_ranges = {
            'ml': (0.1, 500),     # 0.1ml to 500ml reasonable for cocktails
            'oz': (0.01, 16),     # 0.01oz to 16oz reasonable
            'tsp': (0.1, 10),     # 0.1tsp to 10tsp reasonable
            'tbsp': (0.1, 5),     # 0.1tbsp to 5tbsp reasonable
            'dash': (1, 10),      # 1 to 10 dashes reasonable
            'splash': (1, 5),     # 1 to 5 splashes reasonable
            'piece': (1, 10),     # 1 to 10 pieces reasonable
        }
        
        for component in RecipeComponent.objects.all():
            unit = component.unit.lower() if component.unit else ''
            amount = float(component.amount) if component.amount else 0
            
            if unit in reasonable_ranges:
                min_amount, max_amount = reasonable_ranges[unit]
                if not (min_amount <= amount <= max_amount):
                    unreasonable_amounts.append({
                        'component': component,
                        'amount': amount,
                        'unit': unit,
                        'range': reasonable_ranges[unit]
                    })
        
        if unreasonable_amounts:
            self.log_warning(f"Found {len(unreasonable_amounts)} components with unreasonable amounts")
            issues_found += len(unreasonable_amounts)
            
            for item in unreasonable_amounts:
                component = item['component']
                self.log_verbose(
                    f"   Unreasonable: {component.cocktail.name} - "
                    f"{component.ingredient.name}: {item['amount']} {item['unit']} "
                    f"(expected: {item['range'][0]}-{item['range'][1]})"
                )
        
        # Check for unknown units
        known_units = {'ml', 'oz', 'fl oz', 'tsp', 'tbsp', 'cup', 'pint', 'quart', 
                      'dash', 'splash', 'piece', 'slice', 'wedge', 'twist', 'sprig'}
        
        unknown_units = RecipeComponent.objects.exclude(
            unit__isnull=True
        ).exclude(
            unit__in=known_units
        ).values_list('unit', flat=True).distinct()
        
        if unknown_units:
            self.log_warning(f"Found unknown units: {', '.join(unknown_units)}")
            issues_found += len(unknown_units)
        
        if issues_found == 0:
            self.log_success("All units are valid and within reasonable ranges")
        else:
            self.log_warning(f"Total validation issues found: {issues_found}")

    def _fix_amounts(self):
        """
        Fix obviously incorrect amount values.
        
        Common Issues:
        1. Decimal point errors (e.g., 15.0 instead of 1.5)
        2. Unit confusion (e.g., 30 oz instead of 30 ml)
        3. Missing decimal points (e.g., 15 instead of 1.5)
        """
        self.log_info("🔧 Fixing obviously incorrect amounts...")
        
        fixes_applied = 0
        
        # Fix decimal point errors (amounts > 100 for small units)
        small_units = ['oz', 'fl oz', 'tsp', 'tbsp']
        
        for unit in small_units:
            large_amounts = RecipeComponent.objects.filter(
                unit__iexact=unit,
                amount__gt=100
            )
            
            for component in large_amounts:
                old_amount = float(component.amount)
                # Likely decimal point error - divide by 10
                new_amount = round(old_amount / 10, 2)
                
                self.log_verbose(
                    f"Fixing decimal point: {component.cocktail.name} - "
                    f"{component.ingredient.name}: {old_amount} → {new_amount} {unit}"
                )
                
                if not self.dry_run:
                    component.amount = Decimal(str(new_amount))
                    component.save()
                
                fixes_applied += 1
                self.changes_made += 1
        
        # Fix unreasonably small amounts for large units
        large_units = ['ml']
        
        for unit in large_units:
            tiny_amounts = RecipeComponent.objects.filter(
                unit__iexact=unit,
                amount__lt=0.1
            )
            
            for component in tiny_amounts:
                old_amount = float(component.amount)
                # Likely missing decimal point - multiply by 10
                new_amount = round(old_amount * 10, 2)
                
                # But cap at reasonable maximums
                if new_amount > 500:
                    new_amount = round(old_amount * 100, 2)  # Try different multiplier
                    if new_amount > 500:
                        continue  # Skip if still unreasonable
                
                self.log_verbose(
                    f"Fixing small amount: {component.cocktail.name} - "
                    f"{component.ingredient.name}: {old_amount} → {new_amount} {unit}"
                )
                
                if not self.dry_run:
                    component.amount = Decimal(str(new_amount))
                    component.save()
                
                fixes_applied += 1
                self.changes_made += 1
        
        if fixes_applied > 0:
            self.log_success(f"Fixed {fixes_applied} amount values")
        else:
            self.log_success("All amounts appear to be correct")
