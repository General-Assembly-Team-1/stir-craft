"""
Django management command to check for cocktail image consistency.

This command helps identify and optionally fix mismatches between
database image paths and actual files in the media directory.

USAGE:
    # Check for image issues (read-only)
    python manage.py check_cocktail_images

    # Check and auto-fix issues
    python manage.py check_cocktail_images --fix

    # Show detailed report
    python manage.py check_cocktail_images --verbose
"""

import os
from django.core.management.base import BaseCommand
from django.conf import settings
from stir_craft.models import Cocktail


class Command(BaseCommand):
    help = 'Check for cocktail image path consistency and optionally fix issues'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Automatically fix image path mismatches',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed information about each cocktail',
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Checking cocktail image consistency...")
        
        media_cocktails_dir = os.path.join(settings.MEDIA_ROOT, 'cocktails')
        
        if not os.path.exists(media_cocktails_dir):
            self.stdout.write(
                self.style.ERROR(f"Media directory not found: {media_cocktails_dir}")
            )
            return
        
        # Get all actual files
        actual_files = set(os.listdir(media_cocktails_dir))
        self.stdout.write(f"📁 Found {len(actual_files)} files in media directory")
        
        # Check all cocktails
        cocktails = Cocktail.objects.all()
        total_cocktails = cocktails.count()
        issues = []
        working = []
        
        for cocktail in cocktails:
            if not cocktail.image:
                if options['verbose']:
                    self.stdout.write(f"⚠️  {cocktail.name}: No image in database")
                continue
                
            db_filename = os.path.basename(cocktail.image.name)
            
            if db_filename in actual_files:
                working.append(cocktail.name)
                if options['verbose']:
                    self.stdout.write(f"✅ {cocktail.name}: Image OK")
            else:
                # Look for potential match
                base_name = self._normalize_name(cocktail.name)
                base_filename = f"{base_name}.jpg"
                
                if base_filename in actual_files:
                    issues.append({
                        'cocktail': cocktail,
                        'db_filename': db_filename,
                        'correct_filename': base_filename,
                        'fixable': True
                    })
                else:
                    issues.append({
                        'cocktail': cocktail,
                        'db_filename': db_filename,
                        'correct_filename': None,
                        'fixable': False
                    })
        
        # Report results
        self.stdout.write("\n📊 RESULTS:")
        self.stdout.write(f"   Total cocktails: {total_cocktails}")
        self.stdout.write(f"   Working images: {len(working)}")
        self.stdout.write(f"   Issues found: {len(issues)}")
        
        if issues:
            self.stdout.write(f"\n❌ ISSUES FOUND:")
            fixable_count = sum(1 for issue in issues if issue['fixable'])
            
            for issue in issues:
                if issue['fixable']:
                    self.stdout.write(
                        f"   🔧 {issue['cocktail'].name}: "
                        f"{issue['db_filename']} → {issue['correct_filename']}"
                    )
                else:
                    self.stdout.write(
                        f"   💥 {issue['cocktail'].name}: "
                        f"No matching file found for {issue['db_filename']}"
                    )
            
            self.stdout.write(f"\n   Fixable issues: {fixable_count}")
            self.stdout.write(f"   Unfixable issues: {len(issues) - fixable_count}")
            
            # Fix issues if requested
            if options['fix'] and fixable_count > 0:
                self.stdout.write(f"\n🔧 FIXING {fixable_count} ISSUES...")
                fixed_count = 0
                
                for issue in issues:
                    if issue['fixable']:
                        old_path = issue['cocktail'].image.name
                        new_path = f"cocktails/{issue['correct_filename']}"
                        
                        issue['cocktail'].image.name = new_path
                        issue['cocktail'].save(update_fields=['image'])
                        
                        self.stdout.write(f"   ✅ Fixed: {issue['cocktail'].name}")
                        fixed_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(f"\n🎉 Fixed {fixed_count} image path issues!")
                )
            elif options['fix']:
                self.stdout.write(
                    self.style.WARNING("No fixable issues found.")
                )
            else:
                self.stdout.write(
                    f"\n💡 Run with --fix to automatically fix {fixable_count} issues"
                )
        else:
            self.stdout.write(
                self.style.SUCCESS("\n🎉 All cocktail images are working correctly!")
            )
            
        # Calculate coverage
        if total_cocktails > 0:
            coverage = (len(working) + len([i for i in issues if i['fixable']])) / total_cocktails * 100
            self.stdout.write(f"\n📈 Image coverage: {coverage:.1f}%")

    def _normalize_name(self, name):
        """Normalize cocktail name to match filename format."""
        normalized = name.lower().replace(' ', '-').replace("'", "")
        normalized = ''.join(c for c in normalized if c.isalnum() or c in '-_')
        return normalized
