from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client
from ..models import List, Cocktail, RecipeComponent, Ingredient, Vessel
import json


class ListViewsTest(TestCase):
    """Tests for List (collections) views and AJAX endpoints."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='list_user', password='pass123')
        self.other = User.objects.create_user(username='other_user', password='pass123')

        # Minimal objects to create cocktails
        self.vessel = Vessel.objects.create(name='Test Glass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(name='Test Spirit', ingredient_type='spirit', alcohol_content=40.0)

        # Create a cocktail owned by self.user
        self.cocktail = Cocktail.objects.create(
            name='List Cocktail',
            instructions='Mix',
            creator=self.user,
            vessel=self.vessel
        )
        RecipeComponent.objects.create(cocktail=self.cocktail, ingredient=self.ingredient, amount=50.0, unit='ml', order=1)

    def test_list_create_requires_login_and_creates(self):
        # Anonymous should be redirected
        response = self.client.get(reverse('list_create'))
        self.assertEqual(response.status_code, 302)

        # Logged in user can GET form
        self.client.login(username='list_user', password='pass123')
        response = self.client.get(reverse('list_create'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create New List')

        # POST valid data creates list and redirects to detail
        post_data = {'name': 'My Favorites', 'description': 'Tasty drinks'}
        response = self.client.post(reverse('list_create'), data=post_data)
        self.assertEqual(response.status_code, 302)

        created = List.objects.filter(name='My Favorites', creator=self.user).first()
        self.assertIsNotNone(created)
        self.assertEqual(created.creator, self.user)

    def test_list_detail_shows_cocktails(self):
        # Create a list and add cocktail
        lst = List.objects.create(name='Show List', creator=self.user)
        lst.cocktails.add(self.cocktail)

        response = self.client.get(reverse('list_detail', args=[lst.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, lst.name)
        self.assertContains(response, self.cocktail.name)

    def test_list_update_redirects_non_owner(self):
        lst = List.objects.create(name='Owned List', creator=self.user)

        # Other user should be redirected when trying to edit
        self.client.login(username='other_user', password='pass123')
        response = self.client.get(reverse('list_update', args=[lst.id]))
        self.assertEqual(response.status_code, 302)

    def test_add_to_list_and_remove_from_list_ajax(self):
        # Create a list for the user
        lst = List.objects.create(name='AJAX List', creator=self.user)

        # Login as owner and add cocktail
        self.client.login(username='list_user', password='pass123')
        add_url = reverse('add_to_list', args=[self.cocktail.id, lst.id])
        response = self.client.post(add_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertIn(self.cocktail, lst.cocktails.all())

        # Adding again should return error (already in list)
        response = self.client.post(add_url)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))

        # Remove from list
        remove_url = reverse('remove_from_list', args=[self.cocktail.id, lst.id])
        response = self.client.post(remove_url)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(data.get('success'))
        self.assertNotIn(self.cocktail, lst.cocktails.all())

        # Non-owner cannot add/remove
        self.client.logout()
        self.client.login(username='other_user', password='pass123')
        response = self.client.post(add_url)
        data = json.loads(response.content)
        self.assertFalse(data.get('success'))

    def test_list_feed_shows_public_lists(self):
        # Create some lists
        List.objects.create(name='Public One', creator=self.user, list_type='custom')
        List.objects.create(name='Public Two', creator=self.other, list_type='custom')

        response = self.client.get(reverse('list_feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Public One')
        self.assertContains(response, 'Public Two')
