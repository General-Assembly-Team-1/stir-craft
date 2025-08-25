from django.core.management.base import BaseCommand
from stir_craft.models import RecipeComponent


class Command(BaseCommand):
    help = 'Standardizes units in RecipeComponents by converting oz, tsp, and tbsp to mL for storage'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Conversion factors to mL
        conversion_factors = {
            'oz': 29.5735,
            'tsp': 4.92892,
            'tbsp': 14.7868,
        }
        
        total_updated = 0
        
        for unit, factor in conversion_factors.items():
            components = RecipeComponent.objects.filter(unit=unit)
            count = components.count()
            
            if count > 0:
                self.stdout.write(f"\nProcessing {count} components with unit '{unit}':")
                
                for component in components:
                    old_amount = component.amount
                    new_amount = round(float(old_amount) * factor, 2)
                    
                    self.stdout.write(
                        f"  {component.cocktail.name}: {old_amount} {unit} → {new_amount} ml"
                    )
                    
                    if not dry_run:
                        component.amount = new_amount
                        component.unit = 'ml'
                        component.save()
                
                total_updated += count
        
        # Check for non-standard units that should remain as-is
        non_standard_units = ['dash', 'splash', 'pinch', 'piece', 'slice', 'wedge', 'sprig']
        for unit in non_standard_units:
            count = RecipeComponent.objects.filter(unit=unit).count()
            if count > 0:
                self.stdout.write(f"\nKeeping {count} components with unit '{unit}' as-is")
        
        # Summary
        self.stdout.write(f"\n" + "="*50)
        if dry_run:
            self.stdout.write(
                self.style.WARNING(f"DRY RUN: Would update {total_updated} components")
            )
            self.stdout.write("Run without --dry-run to apply changes")
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Successfully updated {total_updated} components")
            )
        
        # Show final unit distribution
        self.stdout.write(f"\nFinal unit distribution:")
        from django.db.models import Count
        unit_counts = (RecipeComponent.objects
                      .values('unit')
                      .annotate(count=Count('unit'))
                      .order_by('-count'))
        
        for item in unit_counts:
            self.stdout.write(f"  {item['unit']}: {item['count']} components")
