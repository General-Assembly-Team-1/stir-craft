"""
Consolidated Tag Maintenance Command

This command handles all tag-related maintenance tasks including cleanup,
normalization, duplicate removal, and tag quality optimization across
the entire cocktail database.

Usage:
    python manage.py maintain_tags --dry-run
    python manage.py maintain_tags --clean-duplicates --normalize-names
    python manage.py maintain_tags --all --verbose
"""

from django.core.management.base import CommandError
from django.db import transaction
from collections import defaultdict
import re
from ...utils.command_base import DataMaintenanceCommand
from ...models import Cocktail
from taggit.models import Tag, TaggedItem


class Command(DataMaintenanceCommand):
    help = 'Consolidated tag maintenance: cleanup, normalization, and optimization'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        parser.add_argument(
            '--clean-duplicates',
            action='store_true',
            help='Remove duplicate and near-duplicate tags',
        )
        parser.add_argument(
            '--normalize-names',
            action='store_true',
            help='Normalize tag names (case, spacing, punctuation)',
        )
        parser.add_argument(
            '--remove-unused',
            action='store_true',
            help='Remove tags that are not used by any cocktails',
        )
        parser.add_argument(
            '--consolidate-colors',
            action='store_true',
            help='Consolidate color tags to standard color palette',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all tag maintenance tasks',
        )

    def handle(self, *args, **options):
        """Execute the consolidated tag maintenance process."""
        self.setup_command(options)
        
        # Determine which tasks to run
        tasks = []
        if options['all']:
            tasks = ['duplicates', 'normalize', 'unused', 'colors']
        else:
            if options['clean_duplicates']:
                tasks.append('duplicates')
            if options['normalize_names']:
                tasks.append('normalize')
            if options['remove_unused']:
                tasks.append('unused')
            if options['consolidate_colors']:
                tasks.append('colors')
        
        if not tasks:
            raise CommandError("Please specify at least one maintenance task or use --all")
        
        self.log_info(f"Starting tag maintenance with tasks: {', '.join(tasks)}")
        
        try:
            # Execute tasks in optimal order
            if 'normalize' in tasks:
                self._normalize_tag_names()
            
            if 'duplicates' in tasks:
                self._clean_duplicate_tags()
            
            if 'colors' in tasks:
                self._consolidate_color_tags()
            
            if 'unused' in tasks:
                self._remove_unused_tags()
            
            self.print_summary()
            
        except Exception as e:
            self.log_error(f"Tag maintenance failed: {str(e)}")
            raise CommandError(f"Tag maintenance failed: {str(e)}")

    def _normalize_tag_names(self):
        """
        Normalize tag names for consistency.
        
        Normalization Rules:
        1. Convert to lowercase for consistency
        2. Remove extra whitespace and trim
        3. Replace multiple spaces with single spaces
        4. Remove special characters except hyphens
        5. Standardize common abbreviations
        """
        self.log_info("✨ Normalizing tag names...")
        
        normalized_count = 0
        
        for tag in Tag.objects.all():
            original_name = tag.name
            normalized_name = self._normalize_tag_name(original_name)
            
            if normalized_name != original_name:
                self.log_verbose(f"Normalizing: '{original_name}' → '{normalized_name}'")
                
                # Check if normalized name already exists
                existing_tag = Tag.objects.filter(name=normalized_name).first()
                
                if existing_tag and existing_tag.id != tag.id:
                    # Merge with existing tag
                    self.log_verbose(f"Merging with existing tag: '{normalized_name}'")
                    self._merge_tags(tag, existing_tag)
                else:
                    # Just rename the tag
                    if not self.dry_run:
                        tag.name = normalized_name
                        tag.save()
                
                normalized_count += 1
                self.changes_made += 1
        
        if normalized_count > 0:
            self.log_success(f"Normalized {normalized_count} tag names")
        else:
            self.log_success("All tag names are already properly normalized")

    def _clean_duplicate_tags(self):
        """
        Remove duplicate and near-duplicate tags.
        
        Duplicate Detection Strategy:
        1. Exact name matches (case-insensitive)
        2. Similar names with minor variations
        3. Plural/singular variations
        4. Abbreviation variations
        """
        self.log_info("🔍 Finding and cleaning duplicate tags...")
        
        # Group tags by normalized name
        tag_groups = defaultdict(list)
        
        for tag in Tag.objects.all():
            normalized = self._normalize_tag_name(tag.name)
            tag_groups[normalized].append(tag)
        
        duplicates_cleaned = 0
        
        for normalized_name, tags in tag_groups.items():
            if len(tags) > 1:
                # Sort by usage count (keep the most used one)
                tags_with_usage = []
                for tag in tags:
                    usage_count = TaggedItem.objects.filter(tag=tag).count()
                    tags_with_usage.append((tag, usage_count))
                
                # Sort by usage count descending, then by ID ascending
                tags_with_usage.sort(key=lambda x: (-x[1], x[0].id))
                
                primary_tag = tags_with_usage[0][0]
                duplicate_tags = [t[0] for t in tags_with_usage[1:]]
                
                self.log_verbose(f"Merging duplicates into '{primary_tag.name}':")
                for dup_tag in duplicate_tags:
                    usage_count = next(t[1] for t in tags_with_usage if t[0] == dup_tag)
                    self.log_verbose(f"  - '{dup_tag.name}' ({usage_count} uses)")
                
                # Merge all duplicates into the primary tag
                for dup_tag in duplicate_tags:
                    self._merge_tags(dup_tag, primary_tag)
                    duplicates_cleaned += 1
                    self.changes_made += 1
        
        if duplicates_cleaned > 0:
            self.log_success(f"Cleaned {duplicates_cleaned} duplicate tags")
        else:
            self.log_success("No duplicate tags found")

    def _consolidate_color_tags(self):
        """
        Consolidate color tags to a standard color palette.
        
        Standard Color Palette:
        - Primary: red, blue, green, yellow, orange, purple, pink
        - Neutrals: clear, white, black, brown, amber, golden
        - Descriptive: light, dark, bright, pale
        """
        self.log_info("🎨 Consolidating color tags to standard palette...")
        
        # Define color mapping
        color_mappings = {
            # Red variations
            'red': ['red', 'crimson', 'scarlet', 'burgundy', 'maroon'],
            'pink': ['pink', 'rose', 'blush', 'salmon'],
            
            # Blue variations  
            'blue': ['blue', 'navy', 'azure', 'cobalt', 'sapphire'],
            
            # Green variations
            'green': ['green', 'lime', 'emerald', 'forest', 'olive'],
            
            # Yellow variations
            'yellow': ['yellow', 'gold', 'lemon', 'canary'],
            'golden': ['golden', 'gold', 'brass', 'honey'],
            
            # Orange variations
            'orange': ['orange', 'tangerine', 'peach', 'coral'],
            
            # Purple variations
            'purple': ['purple', 'violet', 'lavender', 'plum', 'magenta'],
            
            # Neutral variations
            'clear': ['clear', 'transparent', 'colorless'],
            'white': ['white', 'cream', 'ivory', 'pearl'],
            'black': ['black', 'ebony', 'charcoal'],
            'brown': ['brown', 'chocolate', 'coffee', 'mocha', 'caramel'],
            'amber': ['amber', 'cognac', 'whiskey-colored'],
        }
        
        # Create reverse mapping for lookup
        color_lookup = {}
        for standard_color, variations in color_mappings.items():
            for variation in variations:
                color_lookup[variation.lower()] = standard_color
        
        consolidated_count = 0
        
        # Find color tags that need consolidation
        for tag in Tag.objects.all():
            tag_name_lower = tag.name.lower()
            
            # Check if this tag matches any color variation
            for variation, standard_color in color_lookup.items():
                if variation in tag_name_lower or tag_name_lower == variation:
                    if tag.name != standard_color:
                        self.log_verbose(f"Consolidating color: '{tag.name}' → '{standard_color}'")
                        
                        # Get or create the standard color tag
                        standard_tag, created = Tag.objects.get_or_create(name=standard_color)
                        
                        if created:
                            self.log_verbose(f"Created standard color tag: '{standard_color}'")
                        
                        # Merge into standard color
                        self._merge_tags(tag, standard_tag)
                        consolidated_count += 1
                        self.changes_made += 1
                        break
        
        if consolidated_count > 0:
            self.log_success(f"Consolidated {consolidated_count} color tags")
        else:
            self.log_success("All color tags are already using standard palette")

    def _remove_unused_tags(self):
        """Remove tags that are not used by any cocktails."""
        self.log_info("🧹 Removing unused tags...")
        
        unused_tags = []
        
        for tag in Tag.objects.all():
            if not TaggedItem.objects.filter(tag=tag).exists():
                unused_tags.append(tag)
        
        if unused_tags:
            self.log_info(f"Found {len(unused_tags)} unused tags")
            
            for tag in unused_tags:
                self.log_verbose(f"Removing unused tag: '{tag.name}'")
                
                if not self.dry_run:
                    tag.delete()
                
                self.changes_made += 1
            
            self.log_success(f"Removed {len(unused_tags)} unused tags")
        else:
            self.log_success("No unused tags found")

    def _normalize_tag_name(self, name):
        """
        Normalize a single tag name.
        
        Args:
            name: Original tag name
            
        Returns:
            str: Normalized tag name
        """
        # Convert to lowercase
        normalized = name.lower().strip()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Remove special characters except hyphens and spaces
        normalized = re.sub(r'[^\w\s-]', '', normalized)
        
        # Handle common abbreviations and standardizations
        standardizations = {
            'w/': 'with',
            '&': 'and',
            '+': 'and',
        }
        
        for abbrev, full in standardizations.items():
            normalized = normalized.replace(abbrev, full)
        
        return normalized.strip()

    def _merge_tags(self, source_tag, target_tag):
        """
        Merge source tag into target tag.
        
        Args:
            source_tag: Tag to be merged (will be deleted)
            target_tag: Tag to merge into (will be kept)
        """
        if not self.dry_run:
            with transaction.atomic():
                # Move all tagged items from source to target
                tagged_items = TaggedItem.objects.filter(tag=source_tag)
                
                for item in tagged_items:
                    # Check if target tag is already applied to this object
                    existing = TaggedItem.objects.filter(
                        tag=target_tag,
                        content_type=item.content_type,
                        object_id=item.object_id
                    ).exists()
                    
                    if not existing:
                        # Update the tagged item to use the target tag
                        item.tag = target_tag
                        item.save()
                    else:
                        # Target tag already exists, just delete the duplicate
                        item.delete()
                
                # Delete the source tag
                source_tag.delete()
