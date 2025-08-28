"""
Management command to clean up vibe tags and improve tag quality.
Removes "normal drink" tags and standardizes cocktail/shot distinction.
"""

from django.core.management.base import BaseCommand
from django.db.models import Q
from taggit.models import Tag, TaggedItem
from stir_craft.models import Cocktail


class Command(BaseCommand):
    help = 'Clean up vibe tags: remove "normal drink", standardize cocktail/shot tags'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes'
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Apply the changes to the database'
        )

    def handle(self, *args, **options):
        if not options['dry_run'] and not options['apply']:
            self.stdout.write(
                self.style.WARNING(
                    'Use --dry-run to preview changes or --apply to make changes'
                )
            )
            return

        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS('🏷️  Starting vibe tag cleanup...')
        )

        # 1. Remove "normal drink" tags
        self.clean_normal_drink_tags(dry_run)
        
        # 2. Standardize shot vs cocktail tags
        self.standardize_drink_types(dry_run)
        
        # 3. Clean up duplicate and similar tags
        self.clean_duplicate_tags(dry_run)
        
        # 4. Add missing cocktail/shot tags based on ingredients
        self.add_missing_drink_type_tags(dry_run)

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    '👀 This was a dry run. Use --apply to make actual changes.'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ Vibe tag cleanup completed!')
            )

    def clean_normal_drink_tags(self, dry_run):
        """Remove 'normal drink' tags as requested."""
        self.stdout.write('\n1. Removing "normal drink" tags...')
        
        normal_drink_tags = Tag.objects.filter(
            Q(name__icontains='normal drink') |
            Q(name__icontains='normal') |
            Q(name__icontains='regular drink')
        )
        
        for tag in normal_drink_tags:
            tagged_items = TaggedItem.objects.filter(tag=tag)
            cocktail_count = tagged_items.count()
            
            self.stdout.write(f'  - "{tag.name}": {cocktail_count} cocktails')
            
            if not dry_run:
                tagged_items.delete()
                tag.delete()

    def standardize_drink_types(self, dry_run):
        """Standardize shot vs cocktail tags."""
        self.stdout.write('\n2. Standardizing drink type tags...')
        
        # Find shot-related tags
        shot_tags = Tag.objects.filter(
            Q(name__icontains='shot') |
            Q(name__icontains='shooter')
        )
        
        # Find cocktail-related tags  
        cocktail_tags = Tag.objects.filter(
            Q(name__icontains='cocktail') &
            ~Q(name__icontains='shot')
        )
        
        self.stdout.write(f'  Found {shot_tags.count()} shot-related tags')
        self.stdout.write(f'  Found {cocktail_tags.count()} cocktail-related tags')
        
        # Standardize to just "shot" and "cocktail"
        if not dry_run:
            standard_shot_tag, created = Tag.objects.get_or_create(name='shot')
            standard_cocktail_tag, created = Tag.objects.get_or_create(name='cocktail')
            
            # Merge all shot variants to "shot"
            for tag in shot_tags:
                if tag.name != 'shot':
                    tagged_items = TaggedItem.objects.filter(tag=tag)
                    for item in tagged_items:
                        # Add standard shot tag
                        item.content_object.vibe_tags.add(standard_shot_tag)
                        # Remove old tag
                        item.content_object.vibe_tags.remove(tag)
                    tag.delete()
            
            # Merge all cocktail variants to "cocktail" 
            for tag in cocktail_tags:
                if tag.name != 'cocktail':
                    tagged_items = TaggedItem.objects.filter(tag=tag)
                    for item in tagged_items:
                        # Add standard cocktail tag
                        item.content_object.vibe_tags.add(standard_cocktail_tag)
                        # Remove old tag
                        item.content_object.vibe_tags.remove(tag)
                    tag.delete()

    def clean_duplicate_tags(self, dry_run):
        """Clean up duplicate and similar tags."""
        self.stdout.write('\n3. Cleaning duplicate tags...')
        
        # Common duplicates to merge
        duplicates_map = {
            'tropical': ['tropic', 'tropics'],
            'party': ['parties', 'partying'],
            'summer': ['summery'],
            'winter': ['wintery'],
            'sweet': ['sweetness'],
            'sour': ['sourness'],
            'strong': ['strength'],
            'light': ['lite'],
            'classic': ['classical'],
            'modern': ['contemporary'],
        }
        
        for canonical, variants in duplicates_map.items():
            canonical_tag, created = Tag.objects.get_or_create(name=canonical)
            
            for variant in variants:
                try:
                    variant_tag = Tag.objects.get(name=variant)
                    tagged_items = TaggedItem.objects.filter(tag=variant_tag)
                    count = tagged_items.count()
                    
                    if count > 0:
                        self.stdout.write(f'  Merging "{variant}" → "{canonical}" ({count} items)')
                        
                        if not dry_run:
                            for item in tagged_items:
                                item.content_object.vibe_tags.add(canonical_tag)
                                item.content_object.vibe_tags.remove(variant_tag)
                            variant_tag.delete()
                            
                except Tag.DoesNotExist:
                    continue

    def add_missing_drink_type_tags(self, dry_run):
        """Add cocktail/shot tags to drinks that don't have them."""
        self.stdout.write('\n4. Adding missing drink type tags...')
        
        # Get cocktails without shot or cocktail tags
        cocktails_without_type = Cocktail.objects.exclude(
            Q(vibe_tags__name='shot') | Q(vibe_tags__name='cocktail')
        )
        
        shot_tag, created = Tag.objects.get_or_create(name='shot')
        cocktail_tag, created = Tag.objects.get_or_create(name='cocktail')
        
        self.stdout.write(f'  Found {cocktails_without_type.count()} cocktails without type tags')
        
        shot_count = 0
        cocktail_count = 0
        
        for cocktail in cocktails_without_type:
            # Heuristics to determine if it's a shot or cocktail
            is_shot = (
                cocktail.get_total_volume() <= 60 or  # Small volume (2 oz or less)
                'shot' in cocktail.name.lower() or
                'shooter' in cocktail.name.lower() or
                any('shot' in tag.name.lower() for tag in cocktail.vibe_tags.all())
            )
            
            if is_shot:
                self.stdout.write(f'    Adding "shot" tag to: {cocktail.name}')
                shot_count += 1
                if not dry_run:
                    cocktail.vibe_tags.add(shot_tag)
            else:
                self.stdout.write(f'    Adding "cocktail" tag to: {cocktail.name}')
                cocktail_count += 1
                if not dry_run:
                    cocktail.vibe_tags.add(cocktail_tag)
        
        self.stdout.write(f'  Would add "shot" to {shot_count} drinks')
        self.stdout.write(f'  Would add "cocktail" to {cocktail_count} drinks')
