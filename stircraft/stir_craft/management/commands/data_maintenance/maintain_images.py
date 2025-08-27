"""
Consolidated Image Maintenance Command

This command handles all image-related maintenance tasks including consistency
checks, optimization, missing image detection, and storage cleanup for the
cocktail image system.

Usage:
    python manage.py maintain_images --dry-run
    python manage.py maintain_images --check-consistency --optimize
    python manage.py maintain_images --all --verbose
"""

import os
from pathlib import Path
from django.core.management.base import CommandError
from django.conf import settings
from django.core.files.storage import default_storage
from PIL import Image
from ...utils.command_base import DataMaintenanceCommand
from ...models import Cocktail


class Command(DataMaintenanceCommand):
    help = 'Consolidated image maintenance: consistency, optimization, and cleanup'

    def add_arguments(self, parser):
        super().add_arguments(parser)
        
        parser.add_argument(
            '--check-consistency',
            action='store_true',
            help='Check consistency between database paths and actual files',
        )
        parser.add_argument(
            '--optimize',
            action='store_true',
            help='Optimize image sizes and formats for web delivery',
        )
        parser.add_argument(
            '--fix-paths',
            action='store_true',
            help='Fix incorrect image paths in database',
        )
        parser.add_argument(
            '--cleanup-orphans',
            action='store_true',
            help='Remove orphaned image files not referenced in database',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Run all image maintenance tasks',
        )

    def handle(self, *args, **options):
        """Execute the consolidated image maintenance process."""
        self.setup_command(options)
        
        # Determine which tasks to run
        tasks = []
        if options['all']:
            tasks = ['consistency', 'fix_paths', 'optimize', 'cleanup']
        else:
            if options['check_consistency']:
                tasks.append('consistency')
            if options['fix_paths']:
                tasks.append('fix_paths')
            if options['optimize']:
                tasks.append('optimize')
            if options['cleanup_orphans']:
                tasks.append('cleanup')
        
        if not tasks:
            raise CommandError("Please specify at least one maintenance task or use --all")
        
        self.log_info(f"Starting image maintenance with tasks: {', '.join(tasks)}")
        
        try:
            if 'consistency' in tasks:
                self._check_image_consistency()
            
            if 'fix_paths' in tasks:
                self._fix_image_paths()
            
            if 'optimize' in tasks:
                self._optimize_images()
            
            if 'cleanup' in tasks:
                self._cleanup_orphaned_images()
            
            self.print_summary()
            
        except Exception as e:
            self.log_error(f"Image maintenance failed: {str(e)}")
            raise CommandError(f"Image maintenance failed: {str(e)}")

    def _check_image_consistency(self):
        """
        Check consistency between database image paths and actual files.
        
        Consistency Checks:
        1. Database references files that exist
        2. File paths are correctly formatted
        3. Images are accessible and valid
        4. No broken symlinks or corrupted files
        """
        self.log_info("🔍 Checking image consistency...")
        
        cocktails = Cocktail.objects.all()
        total_cocktails = cocktails.count()
        
        issues_found = 0
        missing_files = []
        invalid_images = []
        accessible_images = 0
        
        self.log_info(f"Checking {total_cocktails} cocktail images...")
        
        for i, cocktail in enumerate(cocktails, 1):
            if i % 50 == 0:
                self.update_progress(i, total_cocktails, "cocktails")
            
            if not cocktail.image:
                self.log_verbose(f"No image set: {cocktail.name}")
                continue
            
            image_path = cocktail.image.name
            
            # Check if file exists in storage
            if not default_storage.exists(image_path):
                missing_files.append({
                    'cocktail': cocktail,
                    'path': image_path
                })
                issues_found += 1
                self.log_verbose(f"Missing file: {cocktail.name} - {image_path}")
                continue
            
            # Check if image is valid by trying to open it
            try:
                full_path = default_storage.path(image_path)
                with Image.open(full_path) as img:
                    # Verify image can be processed
                    img.verify()
                    accessible_images += 1
                    
            except Exception as e:
                invalid_images.append({
                    'cocktail': cocktail,
                    'path': image_path,
                    'error': str(e)
                })
                issues_found += 1
                self.log_verbose(f"Invalid image: {cocktail.name} - {str(e)}")
        
        # Report results
        self.log_info(f"📊 Image consistency report:")
        self.log_info(f"   Total cocktails: {total_cocktails}")
        self.log_info(f"   Accessible images: {accessible_images}")
        self.log_info(f"   Missing files: {len(missing_files)}")
        self.log_info(f"   Invalid images: {len(invalid_images)}")
        
        if issues_found == 0:
            self.log_success("All images are consistent and accessible")
        else:
            self.log_warning(f"Found {issues_found} image consistency issues")
            
            if missing_files:
                self.log_warning("Missing files:")
                for item in missing_files[:10]:  # Show first 10
                    self.log_warning(f"  - {item['cocktail'].name}: {item['path']}")
                if len(missing_files) > 10:
                    self.log_warning(f"  ... and {len(missing_files) - 10} more")
            
            if invalid_images:
                self.log_warning("Invalid images:")
                for item in invalid_images[:5]:  # Show first 5
                    self.log_warning(f"  - {item['cocktail'].name}: {item['error']}")
                if len(invalid_images) > 5:
                    self.log_warning(f"  ... and {len(invalid_images) - 5} more")

    def _fix_image_paths(self):
        """
        Fix incorrect image paths in the database.
        
        Path Fixing Strategy:
        1. Find cocktails with invalid image paths
        2. Search for matching files in the media directory
        3. Update database with correct paths
        4. Handle Django's automatic filename suffixes
        """
        self.log_info("🔧 Fixing image paths...")
        
        media_root = Path(settings.MEDIA_ROOT)
        cocktails_dir = media_root / 'cocktails'
        
        if not cocktails_dir.exists():
            self.log_error(f"Cocktails directory not found: {cocktails_dir}")
            return
        
        # Get all image files in the cocktails directory
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp']:
            image_files.extend(cocktails_dir.glob(ext))
        
        self.log_info(f"Found {len(image_files)} image files in {cocktails_dir}")
        
        # Create lookup dictionary for faster matching
        file_lookup = {}
        for file_path in image_files:
            # Key by filename without extension
            base_name = file_path.stem.lower()
            # Handle Django's automatic suffixes
            if '_' in base_name:
                # Remove Django suffix (e.g., "margarita_XYZ123" -> "margarita")
                clean_name = base_name.split('_')[0]
                file_lookup[clean_name] = file_path
            file_lookup[base_name] = file_path
        
        fixed_count = 0
        
        # Check cocktails with missing or incorrect image paths
        for cocktail in Cocktail.objects.all():
            if cocktail.image and default_storage.exists(cocktail.image.name):
                continue  # Image path is correct
            
            # Try to find matching image file
            cocktail_slug = cocktail.name.lower().replace(' ', '-').replace('_', '-')
            potential_matches = [
                cocktail_slug,
                cocktail.name.lower().replace(' ', ''),
                cocktail.name.lower().replace(' ', '_'),
                cocktail.name.lower(),
            ]
            
            found_file = None
            for match in potential_matches:
                if match in file_lookup:
                    found_file = file_lookup[match]
                    break
            
            if found_file:
                # Calculate relative path from MEDIA_ROOT
                relative_path = found_file.relative_to(media_root)
                
                self.log_verbose(f"Fixing path for {cocktail.name}: {relative_path}")
                
                if not self.dry_run:
                    cocktail.image.name = str(relative_path)
                    cocktail.save()
                
                fixed_count += 1
                self.changes_made += 1
            else:
                self.log_verbose(f"No matching file found for: {cocktail.name}")
        
        if fixed_count > 0:
            self.log_success(f"Fixed image paths for {fixed_count} cocktails")
        else:
            self.log_success("All image paths are correct")

    def _optimize_images(self):
        """
        Optimize images for web delivery.
        
        Optimization Strategy:
        1. Resize images to reasonable dimensions (max 800x600)
        2. Convert to JPEG with quality optimization
        3. Remove EXIF data for privacy and size
        4. Create WebP versions for modern browsers
        """
        self.log_info("🎨 Optimizing images for web delivery...")
        
        optimized_count = 0
        max_dimension = 800
        jpeg_quality = 85
        
        cocktails_with_images = Cocktail.objects.exclude(image='').exclude(image__isnull=True)
        
        for cocktail in cocktails_with_images:
            if not default_storage.exists(cocktail.image.name):
                continue
            
            try:
                image_path = default_storage.path(cocktail.image.name)
                
                with Image.open(image_path) as img:
                    original_size = img.size
                    original_format = img.format
                    
                    # Check if optimization is needed
                    needs_resize = max(original_size) > max_dimension
                    needs_format_conversion = original_format != 'JPEG'
                    
                    if not needs_resize and not needs_format_conversion:
                        continue
                    
                    self.log_verbose(f"Optimizing: {cocktail.name} ({original_size[0]}x{original_size[1]} {original_format})")
                    
                    # Convert to RGB if necessary (for JPEG)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparency
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    
                    # Resize if needed
                    if needs_resize:
                        img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                    
                    if not self.dry_run:
                        # Save optimized image
                        img.save(
                            image_path,
                            'JPEG',
                            quality=jpeg_quality,
                            optimize=True,
                            progressive=True
                        )
                    
                    optimized_count += 1
                    self.changes_made += 1
                    
                    new_size = img.size
                    self.log_verbose(f"  → {new_size[0]}x{new_size[1]} JPEG")
                    
            except Exception as e:
                self.log_error(f"Error optimizing {cocktail.name}: {str(e)}")
                continue
        
        if optimized_count > 0:
            self.log_success(f"Optimized {optimized_count} images")
        else:
            self.log_success("All images are already optimized")

    def _cleanup_orphaned_images(self):
        """
        Remove orphaned image files not referenced in the database.
        
        Cleanup Strategy:
        1. Find all image files in media/cocktails/
        2. Check if each file is referenced by a cocktail
        3. Remove files that are not referenced
        4. Preserve backup files and thumbnails
        """
        self.log_info("🧹 Cleaning up orphaned image files...")
        
        media_root = Path(settings.MEDIA_ROOT)
        cocktails_dir = media_root / 'cocktails'
        
        if not cocktails_dir.exists():
            self.log_warning(f"Cocktails directory not found: {cocktails_dir}")
            return
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.gif']:
            image_files.extend(cocktails_dir.glob(ext))
        
        # Get all referenced image paths from database
        referenced_paths = set()
        for cocktail in Cocktail.objects.exclude(image='').exclude(image__isnull=True):
            if cocktail.image:
                full_path = media_root / cocktail.image.name
                referenced_paths.add(full_path.resolve())
        
        orphaned_files = []
        total_size = 0
        
        for image_file in image_files:
            if image_file.resolve() not in referenced_paths:
                # Check if it's a backup or thumbnail (preserve these)
                if any(keyword in image_file.name.lower() for keyword in ['backup', 'thumb', 'orig']):
                    continue
                
                orphaned_files.append(image_file)
                total_size += image_file.stat().st_size
        
        if orphaned_files:
            size_mb = total_size / (1024 * 1024)
            self.log_info(f"Found {len(orphaned_files)} orphaned files ({size_mb:.1f} MB)")
            
            for orphan_file in orphaned_files:
                self.log_verbose(f"Removing: {orphan_file.name}")
                
                if not self.dry_run:
                    try:
                        orphan_file.unlink()
                        self.changes_made += 1
                    except Exception as e:
                        self.log_error(f"Error removing {orphan_file.name}: {str(e)}")
            
            if not self.dry_run:
                self.log_success(f"Removed {len(orphaned_files)} orphaned files, freed {size_mb:.1f} MB")
            else:
                self.log_info(f"Would remove {len(orphaned_files)} orphaned files, freeing {size_mb:.1f} MB")
        else:
            self.log_success("No orphaned image files found")
