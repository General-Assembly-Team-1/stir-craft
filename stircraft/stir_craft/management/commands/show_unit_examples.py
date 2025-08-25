from django.core.management.base import BaseCommand
from stir_craft.models import RecipeComponent


class Command(BaseCommand):
    help = 'Shows examples of the unit display system for documentation'

    def handle(self, *args, **options):
        self.stdout.write("🍸 StirCraft Unit Display System Examples")
        self.stdout.write("=" * 50)
        
        # Examples of different amounts and how they display
        examples = [
            # Very small amounts - use teaspoons
            (2.46, 'ml', 'Half teaspoon of bitters'),
            (4.93, 'ml', 'One teaspoon of grenadine'), 
            (7.39, 'ml', 'One and half teaspoons of simple syrup'),
            (9.86, 'ml', 'Two teaspoons of lemon juice'),
            
            # Small amounts - quarter ounces
            (7.5, 'ml', 'Quarter ounce of lime juice'),
            (15, 'ml', 'Half ounce of cointreau'),
            (22.5, 'ml', 'Three quarter ounce of sweet vermouth'),
            
            # Standard amounts - whole and half ounces
            (30, 'ml', 'One ounce of bourbon'),
            (45, 'ml', 'One and half ounce of rye whiskey'),
            (60, 'ml', 'Two ounces of gin'),
            (90, 'ml', 'Three ounces of champagne'),
            
            # Non-standard semantic units
            (1, 'dash', 'Dash of angostura bitters'),
            (2, 'dash', 'Two dashes of orange bitters'),
            (1, 'splash', 'Splash of soda water'),
            (1, 'piece', 'One lime wheel'),
            (3, 'piece', 'Three olives'),
        ]
        
        self.stdout.write("\nStorage (mL) -> Display Conversion:")
        self.stdout.write("-" * 40)
        
        for amount, unit, description in examples:
            component = RecipeComponent(amount=amount, unit=unit)
            display = component.get_display_amount()
            
            if unit == 'ml':
                oz_equiv = amount / 29.5735
                self.stdout.write(f"{amount:5.2f} ml ({oz_equiv:.3f} oz) -> {display:>10} | {description}")
            else:
                self.stdout.write(f"{amount:5.0f} {unit:>3} {'':>13} -> {display:>10} | {description}")
        
        self.stdout.write("\n📝 Key Features:")
        self.stdout.write("• Amounts < 0.33 oz display as teaspoons (more intuitive)")
        self.stdout.write("• Ounces rounded to nearest quarter (0.25, 0.5, 0.75)")
        self.stdout.write("• Semantic units (dash, splash) preserved as-is")
        self.stdout.write("• Storage standardized in mL for consistency")
        self.stdout.write("• Display optimized for cocktail recipes")
