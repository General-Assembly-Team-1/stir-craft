from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import JsonResponse
from ..models import List, Cocktail, RecipeComponent, Ingredient, Vessel
import json


class BulkOperationsTest(TestCase):
    """Tests for bulk operations on cocktail lists."""

    def setUp(self):
        self.client = Client()
        
        # Create test users
        self.user = User.objects.create_user(username='bulk_user', password='pass123')
        self.other_user = User.objects.create_user(username='other_user', password='pass123')
        
        # Create test objects for cocktails
        self.vessel = Vessel.objects.create(name='Test Glass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(
            name='Test Spirit', 
            ingredient_type='spirit', 
            alcohol_content=40.0
        )
        
        # Create test cocktails
        self.cocktail1 = Cocktail.objects.create(
            name='Cocktail 1',
            instructions='Mix well',
            creator=self.user,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail1, 
            ingredient=self.ingredient, 
            amount=50.0, 
            unit='ml', 
            order=1
        )
        
        self.cocktail2 = Cocktail.objects.create(
            name='Cocktail 2',
            instructions='Shake with ice',
            creator=self.user,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail2, 
            ingredient=self.ingredient, 
            amount=60.0, 
            unit='ml', 
            order=1
        )
        
        self.cocktail3 = Cocktail.objects.create(
            name='Cocktail 3',
            instructions='Stir gently',
            creator=self.user,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(
            cocktail=self.cocktail3, 
            ingredient=self.ingredient, 
            amount=45.0, 
            unit='ml', 
            order=1
        )
        
        # Create test lists
        self.source_list = List.objects.create(
            name='Source List',
            description='List for testing bulk operations',
            creator=self.user,
            list_type='custom'
        )
        self.source_list.cocktails.add(self.cocktail1, self.cocktail2, self.cocktail3)
        
        self.target_list = List.objects.create(
            name='Target List',
            description='Destination for bulk operations',
            creator=self.user,
            list_type='custom'
        )
        
        # Create a list owned by another user
        self.other_list = List.objects.create(
            name='Other User List',
            description='Not accessible for bulk operations',
            creator=self.other_user,
            list_type='custom'
        )

    def test_bulk_operations_requires_login(self):
        """Test that bulk operations endpoint requires authentication."""
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_bulk_operations_requires_post(self):
        """Test that bulk operations endpoint only accepts POST requests."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertFalse(data['success'])
        self.assertIn('POST method required', data['error'])

    def test_bulk_operations_permission_check(self):
        """Test that only list owner can perform bulk operations."""
        self.client.login(username='other_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        data = {
            'operation': 'remove',
            'cocktail_ids': [self.cocktail1.id]
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Permission denied', response_data['error'])

    def test_bulk_remove_operation(self):
        """Test removing cocktails from a list."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        initial_count = self.source_list.cocktails.count()
        self.assertEqual(initial_count, 3)
        
        data = {
            'operation': 'remove',
            'cocktail_ids': [self.cocktail1.id, self.cocktail2.id]
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('Removed 2 cocktails', response_data['message'])
        
        # Verify cocktails were removed
        self.source_list.refresh_from_db()
        self.assertEqual(self.source_list.cocktails.count(), 1)
        self.assertNotIn(self.cocktail1, self.source_list.cocktails.all())
        self.assertNotIn(self.cocktail2, self.source_list.cocktails.all())
        self.assertIn(self.cocktail3, self.source_list.cocktails.all())

    def test_bulk_copy_operation(self):
        """Test copying cocktails to another list."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        initial_source_count = self.source_list.cocktails.count()
        initial_target_count = self.target_list.cocktails.count()
        
        data = {
            'operation': 'copy',
            'cocktail_ids': [self.cocktail1.id, self.cocktail2.id],
            'target_list_id': self.target_list.id
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('Copied 2 cocktails', response_data['message'])
        
        # Verify cocktails were copied (not moved)
        self.source_list.refresh_from_db()
        self.target_list.refresh_from_db()
        self.assertEqual(self.source_list.cocktails.count(), initial_source_count)  # Unchanged
        self.assertEqual(self.target_list.cocktails.count(), initial_target_count + 2)
        
        # Verify specific cocktails are in target list
        self.assertIn(self.cocktail1, self.target_list.cocktails.all())
        self.assertIn(self.cocktail2, self.target_list.cocktails.all())

    def test_bulk_move_operation(self):
        """Test moving cocktails to another list."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        initial_source_count = self.source_list.cocktails.count()
        initial_target_count = self.target_list.cocktails.count()
        
        data = {
            'operation': 'move',
            'cocktail_ids': [self.cocktail1.id],
            'target_list_id': self.target_list.id
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('Moved 1 cocktails', response_data['message'])
        
        # Verify cocktail was moved (removed from source, added to target)
        self.source_list.refresh_from_db()
        self.target_list.refresh_from_db()
        self.assertEqual(self.source_list.cocktails.count(), initial_source_count - 1)
        self.assertEqual(self.target_list.cocktails.count(), initial_target_count + 1)
        
        # Verify specific cocktail moved
        self.assertNotIn(self.cocktail1, self.source_list.cocktails.all())
        self.assertIn(self.cocktail1, self.target_list.cocktails.all())

    def test_bulk_clone_operation(self):
        """Test cloning entire list to another list."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        initial_source_count = self.source_list.cocktails.count()
        initial_target_count = self.target_list.cocktails.count()
        
        data = {
            'operation': 'clone',
            'target_list_id': self.target_list.id
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertTrue(response_data['success'])
        self.assertIn('Cloned all 3 cocktails', response_data['message'])
        
        # Verify all cocktails were cloned
        self.source_list.refresh_from_db()
        self.target_list.refresh_from_db()
        self.assertEqual(self.source_list.cocktails.count(), initial_source_count)  # Unchanged
        self.assertEqual(self.target_list.cocktails.count(), initial_target_count + 3)
        
        # Verify all cocktails are in target list
        for cocktail in self.source_list.cocktails.all():
            self.assertIn(cocktail, self.target_list.cocktails.all())

    def test_bulk_operations_target_permission_check(self):
        """Test that user must own target list for move/copy operations."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        data = {
            'operation': 'move',
            'cocktail_ids': [self.cocktail1.id],
            'target_list_id': self.other_list.id  # Not owned by current user
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Cannot modify target list', response_data['error'])

    def test_bulk_operations_invalid_operation(self):
        """Test handling of invalid operation types."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        data = {
            'operation': 'invalid_operation',
            'cocktail_ids': [self.cocktail1.id]
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Invalid operation', response_data['error'])

    def test_bulk_operations_missing_target_list(self):
        """Test that operations requiring target list fail without it."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        data = {
            'operation': 'move',
            'cocktail_ids': [self.cocktail1.id]
            # Missing target_list_id
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data), 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Target list required', response_data['error'])

    def test_bulk_operations_invalid_json(self):
        """Test handling of invalid JSON data."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': self.source_list.id})
        
        response = self.client.post(
            url, 
            data='invalid json', 
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertFalse(response_data['success'])
        self.assertIn('Invalid JSON data', response_data['error'])

    def test_bulk_operations_nonexistent_list(self):
        """Test handling of non-existent list IDs."""
        self.client.login(username='bulk_user', password='pass123')
        url = reverse('list_bulk_operations', kwargs={'list_id': 9999})
        
        response = self.client.post(url, content_type='application/json')
        self.assertEqual(response.status_code, 404)
