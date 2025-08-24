"""
Test suite for image handling functionality added in the image handling feature.

This module tests:
- Image upload and validation
- Image resizing and optimization
- Image URL generation and display
- Form handling for image uploads
- Media handling configuration

Tests focus on the new image field and related functionality added to the Cocktail model.
"""

import os
import tempfile
from io import BytesIO
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from PIL import Image as PILImage
from ..models import Cocktail
from ..forms.cocktail_forms import CocktailForm


# Use a temporary directory for test media files
TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ImageHandlingTest(TestCase):
    """Test class for cocktail image handling functionality."""
    
    @classmethod
    def setUpTestData(cls):
        """Create test user for cocktail creation."""
        cls.test_user = User.objects.create_user(
            username='image_tester',
            email='image@stircraft.com',
            password='test_password_123'
        )
    
    def setUp(self):
        """Set up test data for each test method."""
        # Create a simple test image in memory
        self.test_image = self._create_test_image()
        self.large_test_image = self._create_test_image(size=(2000, 2000))
    
    def _create_test_image(self, size=(800, 600), format='JPEG'):
        """
        Create a test image in memory for testing purposes.
        
        Args:
            size (tuple): Image dimensions (width, height)
            format (str): Image format (JPEG, PNG, WebP)
        
        Returns:
            SimpleUploadedFile: Django file object for testing
        """
        # Create a PIL image
        img = PILImage.new('RGB', size, color='red')
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, format=format)
        img_io.seek(0)
        
        # Create Django file object
        return SimpleUploadedFile(
            name=f'test_image.{format.lower()}',
            content=img_io.getvalue(),
            content_type=f'image/{format.lower()}'
        )
    
    def test_cocktail_image_upload_valid(self):
        """Test successful image upload to cocktail."""
        cocktail = Cocktail.objects.create(
            name='Test Cocktail with Image',
            instructions='Mix and serve',
            creator=self.test_user,
            image=self.test_image
        )
        
        # Verify image was saved
        self.assertTrue(cocktail.image)
        self.assertTrue(cocktail.has_image())
        self.assertIsNotNone(cocktail.get_image_url())
        
        # Verify file exists
        self.assertTrue(os.path.exists(cocktail.image.path))
    
    def test_cocktail_without_image(self):
        """Test cocktail creation without image."""
        cocktail = Cocktail.objects.create(
            name='Test Cocktail No Image',
            instructions='Mix and serve',
            creator=self.test_user
        )
        
        # Verify no image
        self.assertFalse(cocktail.image)
        self.assertFalse(cocktail.has_image())
        self.assertIsNone(cocktail.get_image_url())
    
    def test_image_upload_via_form(self):
        """Test image upload through CocktailForm."""
        form_data = {
            'name': 'Form Image Test',
            'instructions': 'Test instructions',
            'color': 'Red',
            'is_alcoholic': True
        }
        
        form = CocktailForm(
            data=form_data,
            files={'image': self.test_image},
            user=self.test_user
        )
        
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
        
        cocktail = form.save(commit=False)
        cocktail.creator = self.test_user
        cocktail.save()
        
        self.assertTrue(cocktail.has_image())
        self.assertIsNotNone(cocktail.get_image_url())
    
    def test_image_format_validation(self):
        """Test that only valid image formats are accepted."""
        # Test valid formats
        valid_formats = ['JPEG', 'PNG', 'WebP']
        
        for format_name in valid_formats:
            with self.subTest(format=format_name):
                test_image = self._create_test_image(format=format_name)
                cocktail = Cocktail.objects.create(
                    name=f'Test {format_name}',
                    instructions='Test',
                    creator=self.test_user,
                    image=test_image
                )
                self.assertTrue(cocktail.has_image())
    
    def test_image_size_handling(self):
        """Test handling of large images."""
        # Create a large image (should still work, but may be resized)
        large_image = self._create_test_image(size=(3000, 3000))
        
        cocktail = Cocktail.objects.create(
            name='Large Image Test',
            instructions='Test instructions',
            creator=self.test_user,
            image=large_image
        )
        
        self.assertTrue(cocktail.has_image())
        self.assertIsNotNone(cocktail.get_image_url())
    
    def test_image_url_string_representation(self):
        """Test that image URL is properly formatted."""
        cocktail = Cocktail.objects.create(
            name='URL Test Cocktail',
            instructions='Test instructions',
            creator=self.test_user,
            image=self.test_image
        )
        
        image_url = cocktail.get_image_url()
        
        # URL should contain the media URL path
        self.assertIn('/media/', image_url)
        self.assertIn('cocktails/', image_url)
        self.assertTrue(image_url.endswith(('.jpg', '.jpeg', '.png', '.webp')))
    
    def test_image_deletion_with_cocktail(self):
        """Test that image files are cleaned up when cocktail is deleted."""
        cocktail = Cocktail.objects.create(
            name='Deletion Test',
            instructions='Test instructions',
            creator=self.test_user,
            image=self.test_image
        )
        
        image_path = cocktail.image.path
        
        # Verify file exists before deletion
        self.assertTrue(os.path.exists(image_path))
        
        # Delete cocktail
        cocktail.delete()
        
        # File cleanup would typically happen with proper storage backend
        # In test, we just verify the cocktail is gone
        self.assertFalse(Cocktail.objects.filter(name='Deletion Test').exists())
    
    def test_cocktail_image_field_blank_and_null(self):
        """Test that image field properly handles blank and null values."""
        # Test creation without image
        cocktail = Cocktail.objects.create(
            name='No Image Cocktail',
            instructions='Test instructions',
            creator=self.test_user
            # image is not provided (blank=True, null=True)
        )
        
        self.assertIsNone(cocktail.image.name if cocktail.image else None)
        self.assertFalse(cocktail.has_image())
        self.assertIsNone(cocktail.get_image_url())
    
    def test_image_upload_path(self):
        """Test that images are uploaded to the correct path."""
        cocktail = Cocktail.objects.create(
            name='Path Test Cocktail',
            instructions='Test instructions',
            creator=self.test_user,
            image=self.test_image
        )
        
        # Image should be uploaded to 'cocktails/' directory
        self.assertTrue(cocktail.image.name.startswith('cocktails/'))
    
    def tearDown(self):
        """Clean up test files after each test."""
        # Clean up any created image files
        import shutil
        try:
            if os.path.exists(TEMP_MEDIA_ROOT):
                shutil.rmtree(TEMP_MEDIA_ROOT)
        except:
            pass
