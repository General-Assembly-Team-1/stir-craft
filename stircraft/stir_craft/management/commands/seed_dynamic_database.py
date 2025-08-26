"""
Django management command to create a dynamic database with multiple users,
their own favorites, and custom themed lists for presentations.

This command enhances the basic TheCocktailDB import by creating a realistic
social environment with multiple users who have different tastes and preferences.

FEATURES:
- Creates multiple fun users with themed usernames
- Each user gets their own random favorite cocktails
- Users create custom themed lists with personality
- Random cross-favoriting between users creates network effects
- Realistic data distribution for impressive demos

USAGE EXAMPLES:
    # Clear everything and create fresh dynamic database
    python manage.py seed_dynamic_database --clear --limit 100

    # Add social features to existing database
    python manage.py seed_dynamic_database --users-only

    # Create specific number of users with custom lists
    python manage.py seed_dynamic_database --num-users 10 --lists-per-user 3

    # Full production-ready setup
    python manage.py seed_dynamic_database --clear --limit 200 --num-users 15
"""

import random
import logging
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.auth.models import User
from django.core.management import call_command
from stir_craft.models import Cocktail, List, Profile
from decimal import Decimal
from datetime import date, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create a dynamic database with multiple users, favorites, and custom lists'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data and start fresh',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=150,
            help='Number of cocktails to import from TheCocktailDB (default: 150)',
        )
        parser.add_argument(
            '--num-users',
            type=int,
            default=12,
            help='Number of fake users to create (default: 12)',
        )
        parser.add_argument(
            '--lists-per-user',
            type=int,
            default=3,
            help='Average number of custom lists per user (default: 3)',
        )
        parser.add_argument(
            '--users-only',
            action='store_true',
            help='Only create users and lists, skip cocktail import',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🍸 Creating dynamic StirCraft database for presentations...'))
        
        limit = options['limit']
        num_users = options['num_users']
        lists_per_user = options['lists_per_user']
        clear_data = options['clear']
        users_only = options['users_only']
        
        try:
            # Step 1: Clear existing data if requested
            if clear_data:
                self._clear_existing_data()
            
            # Step 2: Import cocktails from TheCocktailDB (unless users-only)
            if not users_only:
                self._import_cocktails(limit)
            
            # Step 3: Create fun users with profiles
            users = self._create_fun_users(num_users)
            
            # Step 4: Create custom lists for each user
            self._create_custom_lists(users, lists_per_user)
            
            # Step 5: Add random favorites for each user
            self._add_random_favorites(users)
            
            # Step 6: Create cross-user favorites (social network effect)
            self._create_cross_user_favorites(users)
            
            # Step 7: Print summary
            self._print_summary()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 Successfully created dynamic database with {len(users)} users!'
                )
            )
            
        except Exception as e:
            logger.exception("Unexpected error occurred")
            raise CommandError(f"Database seeding failed: {e}")
    
    def _clear_existing_data(self):
        """Clear existing data for fresh start."""
        self.stdout.write("🧹 Clearing existing data...")
        
        with transaction.atomic():
            # Clear lists first (they reference cocktails)
            List.objects.all().delete()
            # Clear user profiles
            Profile.objects.all().delete()
            # Clear non-admin users (keep cocktaildb_admin for imports)
            User.objects.exclude(username='cocktaildb_admin').delete()
            
            # Optionally clear cocktails too if starting completely fresh
            # (The base seeding command handles cocktail clearing)
        
        self.stdout.write(self.style.WARNING("Cleared existing users, profiles, and lists"))
    
    def _import_cocktails(self, limit):
        """Import cocktails using the existing TheCocktailDB command."""
        self.stdout.write("📡 Importing cocktails from TheCocktailDB...")
        
        # Call the existing seeding command
        call_command(
            'seed_from_thecocktaildb',
            limit=limit,
            verbosity=1  # Reduce verbosity for cleaner output
        )
        
        cocktail_count = Cocktail.objects.count()
        self.stdout.write(f"✅ Imported {cocktail_count} cocktails")
    
    def _create_fun_users(self, num_users):
        """Create fun themed users with profiles."""
        self.stdout.write("👥 Creating fun users...")
        
        # Fun themed usernames with personality
        fun_usernames = [
            'ShakenNotNerd',
            'NegroniBaloney', 
            'BittersAndBytes',
            'Highballer',
            'FizzWhiz',
            'PourDecision',
            'TheRealMaiTai',
            'OldFashionedDev',
            'MuddleBuddy',
            'GinAndTonicCode',
            'CraftyCordial',
            'RumIfYouWantTo',
            'MixAndTwist',
            'SourPowered',
            'BarBackEnd',
            'StirCrazy88',
            'TheMocktailMod',
            'WhiskeyBusiness',
            'CocktailCompiler',
            'TheLastWordsmith'
        ]
        
        # Themed first/last names
        first_names = [
            'Alex', 'Jordan', 'Casey', 'Taylor', 'Morgan', 'Riley', 'Avery', 'Quinn',
            'Charlie', 'Jamie', 'Sage', 'River', 'Phoenix', 'Rowan', 'Emery', 'Blake'
        ]
        
        last_names = [
            'Martini', 'Collins', 'Manhattan', 'Mojito', 'Daiquiri', 'Gimlet',
            'Sidecar', 'Aviation', 'Sazerac', 'Boulevardier', 'Negroni', 'Bellini'
        ]
        
        # Fun email domains
        email_domains = [
            'stircraft.app', 'cocktailclub.io', 'mixology.pro', 'barcraft.net',
            'liquidart.com', 'drinksmith.co', 'craftedspirits.org'
        ]
        
        created_users = []
        
        # Ensure we don't exceed available usernames
        num_users = min(num_users, len(fun_usernames))
        
        for i in range(num_users):
            username = fun_usernames[i]
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email_domain = random.choice(email_domains)
            email = f"{username.lower()}@{email_domain}"
            
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='stircraft2024'  # Simple password for demo
            )
            
            # Create profile with realistic data
            birthdate = self._generate_realistic_birthdate()
            
            profile = Profile.objects.create(
                user=user,
                birthdate=birthdate,
                location=self._generate_random_zipcode()
            )
            
            created_users.append(user)
            
            # Create default lists (handled by signals, but ensure they exist)
            List.create_default_lists(user)
            
            logger.info(f"Created user: {username} ({first_name} {last_name})")
        
        self.stdout.write(f"✅ Created {len(created_users)} themed users")
        return created_users
    
    def _generate_realistic_birthdate(self):
        """Generate realistic birthdate for users 21-65 years old."""
        today = date.today()
        # Random age between 21 and 65
        age = random.randint(21, 65)
        birth_year = today.year - age
        
        # Random month and day
        birth_month = random.randint(1, 12)
        
        # Handle February and different month lengths
        days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if birth_month == 2 and ((birth_year % 4 == 0 and birth_year % 100 != 0) or birth_year % 400 == 0):
            max_day = 29  # Leap year
        else:
            max_day = days_in_month[birth_month - 1]
        
        birth_day = random.randint(1, max_day)
        
        return date(birth_year, birth_month, birth_day)
    
    def _generate_random_zipcode(self):
        """Generate random US zipcode."""
        return f"{random.randint(10000, 99999)}"
    
    def _create_custom_lists(self, users, lists_per_user):
        """Create themed custom lists for each user."""
        self.stdout.write("📋 Creating custom themed lists...")
        
        # Themed list names with personality
        list_themes = [
            # Professional/Tech themed
            ("My Pourfolio", "A curated collection of my signature drinks"),
            ("Shaken & Stirred", "The classics, perfected"),
            ("Bittersweet Symphony", "Complex flavors for sophisticated palates"),
            ("The Booze Clues", "Mystery ingredients that make magic happen"),
            ("Liquid Assets", "High-value cocktails worth investing in"),
            ("The Stir List", "My go-to mixing repertoire"),
            ("High Spirits Only", "Mood-boosting cocktails for any occasion"),
            ("Drafts & Crafts", "Experimental recipes in development"),
            ("My Happy Hour Hits", "Crowd-pleasers that never disappoint"),
            ("The Real McCoy's Picks", "Authentic recipes with no shortcuts"),
            
            # Nerdy/Experimental themed
            ("🧪 Test Tubes & Tinctures", "Laboratory-worthy experimental cocktails"),
            ("Beta Barrels", "Cocktails in testing phase"),
            ("Cocktail Lab Notes", "Scientific approach to mixology"),
            ("Flavor Variables", "Playing with ingredient substitutions"),
            ("Mixology v1.0", "First-generation recipe experiments"),
            ("The Debugger's Daiquiris", "Fixing failed cocktail attempts"),
            ("Patch Notes & Punch Bowls", "Updated and improved recipes"),
            ("Forked & Fortified", "Variations on classic themes"),
            
            # Thematic/Roleplay
            ("🎭 Villainous Vintages", "Dark and mysterious cocktails"),
            ("Elixirs of Enchantment", "Magical potions for special occasions"),
            ("The Alchemist's Cabinet", "Transformative cocktail chemistry"),
            ("Potions & Notions", "Whimsical drinks with personality"),
            ("The Bard's Bar Menu", "Storytelling through cocktails"),
            ("Tavern Tales & Tipples", "Medieval-inspired libations"),
            ("Spells & Sours", "Mystical sour cocktails"),
            
            # Inclusive/Feel-Good
            ("🌈 Zero-Proof, 100% Joy", "Alcohol-free cocktails that impress"),
            ("Sip Happens", "Life's too short for bad cocktails"),
            ("Mocktail Magic", "Non-alcoholic wonders"),
            ("Cheers to Queers", "Celebrating diversity through drinks"),
            ("Inclusive Infusions", "Something for everyone"),
            ("No Proof, No Problem", "Amazing alcohol-free options"),
            
            # Seasonal/Situational
            ("🧊 Sweater Weather Sips", "Cozy cocktails for cold days"),
            ("Summer Slammers", "Hot weather refreshers"),
            ("Rainy Day Remedies", "Comfort drinks for gloomy weather"),
            ("Holiday Spirits", "Festive cocktails for celebrations"),
            ("Brunch & Bubbles", "Perfect morning cocktails"),
            ("After-Hours Alchemy", "Late-night cocktail experiments"),
        ]
        
        created_lists = 0
        
        for user in users:
            # Random number of lists per user (around the average)
            num_lists = random.randint(
                max(1, lists_per_user - 2), 
                lists_per_user + 2
            )
            
            # Select random themes for this user
            user_themes = random.sample(list_themes, min(num_lists, len(list_themes)))
            
            for theme_name, theme_description in user_themes:
                # Create the custom list
                custom_list = List.objects.create(
                    name=theme_name,
                    description=theme_description,
                    creator=user,
                    list_type='custom',
                    is_editable=True,
                    is_deletable=True
                )
                
                # Add random cocktails to the list
                self._populate_themed_list(custom_list, theme_name)
                
                created_lists += 1
                logger.info(f"Created list: '{theme_name}' for {user.username}")
        
        self.stdout.write(f"✅ Created {created_lists} custom themed lists")
    
    def _populate_themed_list(self, custom_list, theme_name):
        """Add appropriate cocktails to a themed list based on its name."""
        all_cocktails = list(Cocktail.objects.all())
        
        if not all_cocktails:
            return
        
        # Different strategies based on list theme
        theme_lower = theme_name.lower()
        selected_cocktails = []
        
        # Determine list size based on theme
        if 'test' in theme_lower or 'lab' in theme_lower or 'experimental' in theme_lower:
            list_size = random.randint(3, 8)  # Smaller experimental lists
        elif 'portfolio' in theme_lower or 'assets' in theme_lower:
            list_size = random.randint(8, 15)  # Larger curated collections
        else:
            list_size = random.randint(5, 12)  # Standard size
        
        # Theme-based cocktail selection
        if 'zero-proof' in theme_lower or 'mocktail' in theme_lower or 'no proof' in theme_lower:
            # Non-alcoholic cocktails
            non_alcoholic = [c for c in all_cocktails if not c.is_alcoholic]
            if non_alcoholic:
                selected_cocktails = random.sample(
                    non_alcoholic, 
                    min(list_size, len(non_alcoholic))
                )
            else:
                # Fallback to random if no non-alcoholic found
                selected_cocktails = random.sample(all_cocktails, min(list_size, len(all_cocktails)))
        
        elif 'summer' in theme_lower or 'tropical' in theme_lower:
            # Summer/tropical themed cocktails
            summer_cocktails = []
            for cocktail in all_cocktails:
                cocktail_name_lower = cocktail.name.lower()
                vibe_tags = [tag.name.lower() for tag in cocktail.vibe_tags.all()]
                
                if any(word in cocktail_name_lower for word in ['margarita', 'mojito', 'daiquiri', 'piña', 'mai tai']) or \
                   any(tag in vibe_tags for tag in ['tropical', 'summer', 'citrusy', 'refreshing']):
                    summer_cocktails.append(cocktail)
            
            if summer_cocktails:
                selected_cocktails = random.sample(
                    summer_cocktails, 
                    min(list_size, len(summer_cocktails))
                )
            else:
                selected_cocktails = random.sample(all_cocktails, min(list_size, len(all_cocktails)))
        
        elif 'winter' in theme_lower or 'sweater' in theme_lower or 'holiday' in theme_lower:
            # Winter/cozy themed cocktails
            winter_cocktails = []
            for cocktail in all_cocktails:
                cocktail_name_lower = cocktail.name.lower()
                vibe_tags = [tag.name.lower() for tag in cocktail.vibe_tags.all()]
                
                if any(word in cocktail_name_lower for word in ['hot', 'warm', 'toddy', 'punch', 'mulled']) or \
                   any(tag in vibe_tags for tag in ['hot', 'warm', 'winter', 'spiced']):
                    winter_cocktails.append(cocktail)
            
            if winter_cocktails:
                selected_cocktails = random.sample(
                    winter_cocktails, 
                    min(list_size, len(winter_cocktails))
                )
            else:
                selected_cocktails = random.sample(all_cocktails, min(list_size, len(all_cocktails)))
        
        elif 'bitter' in theme_lower or 'complex' in theme_lower or 'sophisticated' in theme_lower:
            # Complex/bitter cocktails
            complex_cocktails = []
            for cocktail in all_cocktails:
                cocktail_name_lower = cocktail.name.lower()
                vibe_tags = [tag.name.lower() for tag in cocktail.vibe_tags.all()]
                
                if any(word in cocktail_name_lower for word in ['negroni', 'manhattan', 'old fashioned', 'sazerac']) or \
                   any(tag in vibe_tags for tag in ['bitter', 'complex', 'sophisticated', 'classic']):
                    complex_cocktails.append(cocktail)
            
            if complex_cocktails:
                selected_cocktails = random.sample(
                    complex_cocktails, 
                    min(list_size, len(complex_cocktails))
                )
            else:
                selected_cocktails = random.sample(all_cocktails, min(list_size, len(all_cocktails)))
        
        elif 'brunch' in theme_lower or 'bubbles' in theme_lower:
            # Brunch cocktails
            brunch_cocktails = []
            for cocktail in all_cocktails:
                cocktail_name_lower = cocktail.name.lower()
                vibe_tags = [tag.name.lower() for tag in cocktail.vibe_tags.all()]
                
                if any(word in cocktail_name_lower for word in ['mimosa', 'bellini', 'bloody', 'screwdriver']) or \
                   any(tag in vibe_tags for tag in ['brunch', 'sparkling', 'bubbly']):
                    brunch_cocktails.append(cocktail)
            
            if brunch_cocktails:
                selected_cocktails = random.sample(
                    brunch_cocktails, 
                    min(list_size, len(brunch_cocktails))
                )
            else:
                selected_cocktails = random.sample(all_cocktails, min(list_size, len(all_cocktails)))
        
        else:
            # Default: random selection
            selected_cocktails = random.sample(all_cocktails, min(list_size, len(all_cocktails)))
        
        # Add cocktails to the list
        if selected_cocktails:
            custom_list.cocktails.set(selected_cocktails)
            logger.debug(f"Added {len(selected_cocktails)} cocktails to '{custom_list.name}'")
    
    def _add_random_favorites(self, users):
        """Add random favorite cocktails for each user."""
        self.stdout.write("⭐ Adding random favorites for each user...")
        
        all_cocktails = list(Cocktail.objects.all())
        
        if not all_cocktails:
            self.stdout.write(self.style.WARNING("No cocktails found to favorite"))
            return
        
        favorites_added = 0
        
        for user in users:
            # Get or create favorites list for user
            favorites_list = List.get_or_create_favorites_list(user)
            
            # Random number of favorites per user (realistic range)
            num_favorites = random.randint(5, 25)
            
            # Select random cocktails for favorites
            user_favorites = random.sample(
                all_cocktails, 
                min(num_favorites, len(all_cocktails))
            )
            
            # Add to favorites list
            favorites_list.cocktails.set(user_favorites)
            favorites_added += len(user_favorites)
            
            logger.info(f"Added {len(user_favorites)} favorites for {user.username}")
        
        self.stdout.write(f"✅ Added {favorites_added} total favorites across all users")
    
    def _create_cross_user_favorites(self, users):
        """Create realistic cross-user favorites to simulate social network."""
        self.stdout.write("🤝 Creating cross-user favorite patterns...")
        
        # This simulates users discovering and favoriting cocktails from other users' lists
        cross_favorites_added = 0
        
        for user in users:
            # Each user discovers cocktails from 2-4 other users
            other_users = [u for u in users if u != user]
            discovered_users = random.sample(other_users, min(random.randint(2, 4), len(other_users)))
            
            user_favorites_list = List.get_or_create_favorites_list(user)
            current_favorites = set(user_favorites_list.cocktails.all())
            
            for discovered_user in discovered_users:
                # Look at their custom lists
                other_user_lists = List.objects.filter(
                    creator=discovered_user, 
                    list_type='custom'
                )
                
                for other_list in other_user_lists:
                    # Chance to discover and favorite cocktails from this list
                    if random.random() < 0.3:  # 30% chance per list
                        list_cocktails = list(other_list.cocktails.all())
                        
                        if list_cocktails:
                            # Favorite 1-3 cocktails from this list
                            num_to_favorite = random.randint(1, min(3, len(list_cocktails)))
                            new_favorites = random.sample(list_cocktails, num_to_favorite)
                            
                            # Only add if not already in favorites
                            for cocktail in new_favorites:
                                if cocktail not in current_favorites:
                                    user_favorites_list.cocktails.add(cocktail)
                                    current_favorites.add(cocktail)
                                    cross_favorites_added += 1
                                    
                                    logger.debug(
                                        f"{user.username} discovered '{cocktail.name}' "
                                        f"from {discovered_user.username}'s '{other_list.name}'"
                                    )
        
        self.stdout.write(f"✅ Added {cross_favorites_added} cross-user favorites")
    
    def _print_summary(self):
        """Print comprehensive summary of the dynamic database."""
        user_count = User.objects.exclude(username='cocktaildb_admin').count()
        cocktail_count = Cocktail.objects.count()
        custom_lists_count = List.objects.filter(list_type='custom').count()
        favorites_lists_count = List.objects.filter(list_type='favorites').count()
        total_favorites = sum(
            list_obj.cocktails.count() 
            for list_obj in List.objects.filter(list_type='favorites')
        )
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("📊 DYNAMIC DATABASE SUMMARY"))
        self.stdout.write("="*60)
        self.stdout.write(f"👥 Users Created: {user_count}")
        self.stdout.write(f"🍸 Total Cocktails: {cocktail_count}")
        self.stdout.write(f"📋 Custom Lists: {custom_lists_count}")
        self.stdout.write(f"⭐ Favorites Lists: {favorites_lists_count}")
        self.stdout.write(f"💖 Total Favorites: {total_favorites}")
        self.stdout.write("="*60)
        
        # Show sample users and their activity
        sample_users = User.objects.exclude(username='cocktaildb_admin')[:5]
        if sample_users:
            self.stdout.write("🎯 Sample user activity:")
            for user in sample_users:
                user_lists = List.objects.filter(creator=user, list_type='custom').count()
                user_favorites = List.objects.filter(creator=user, list_type='favorites').first()
                favorites_count = user_favorites.cocktails.count() if user_favorites else 0
                
                self.stdout.write(
                    f"  • {user.username}: {user_lists} custom lists, {favorites_count} favorites"
                )
        
        self.stdout.write(f"\n💡 Demo ready! Features to showcase:")
        self.stdout.write(f"  • Multiple users with unique personalities")
        self.stdout.write(f"  • Themed custom lists with curated cocktails")
        self.stdout.write(f"  • Realistic favorite patterns and social discovery")
        self.stdout.write(f"  • Cross-user interactions and list browsing")
        self.stdout.write(f"  • Ready for user authentication demos")
        self.stdout.write("="*60 + "\n")
