from django.test import TestCase, RequestFactory, override_settings
from django.contrib.auth.models import User, AnonymousUser
from django.urls import reverse
from django.test import Client
from .. import views
from ..models import Cocktail, Ingredient, Vessel, RecipeComponent, List


class RenderErrorAndFavoriteTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.user = User.objects.create_user(username='fav_user', password='pass123')

        # Minimal cocktail setup
        self.vessel = Vessel.objects.create(name='Glass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(name='Gin Test', ingredient_type='spirit', alcohol_content=40.0)
        self.cocktail = Cocktail.objects.create(name='Fav Cocktail', instructions='Mix', creator=self.user, vessel=self.vessel)
        RecipeComponent.objects.create(cocktail=self.cocktail, ingredient=self.ingredient, amount=30.0, unit='ml', order=1)

    def test_render_error_shows_custom_message_and_actions_for_authenticated(self):
        # Build a request and assign an authenticated user
        request = self.factory.get('/dummy')
        request.user = self.user

        response = views.render_error(request, 403, error_message='Only the creator may edit this.')
        self.assertEqual(response.status_code, 403)
        content = response.content.decode()
        # Custom message appears
        self.assertIn('Only the creator may edit this.', content)
        # Authenticated users should see dashboard action for 403
        self.assertIn('Go to Dashboard', content)

    @override_settings(DEBUG=True)
    def test_render_error_includes_exception_when_debug(self):
        request = self.factory.get('/err')
        request.user = AnonymousUser()

        response = views.render_error(request, 500, error_message=None, exception=Exception('boom-details'))
        self.assertEqual(response.status_code, 500)
        content = response.content.decode()
        # In DEBUG mode the exception string should be rendered
        self.assertIn('boom-details', content)

    def test_toggle_favorite_add_and_remove(self):
        # Anonymous POST should redirect to login (login_required)
        resp = self.client.post(reverse('toggle_favorite', args=[self.cocktail.id]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/admin/login/', resp.url)

        # Logged in user toggles favorite
        self.client.login(username='fav_user', password='pass123')

        url = reverse('toggle_favorite', args=[self.cocktail.id])
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertTrue(data.get('favorited'))
        self.assertEqual(data.get('favorites_count'), 1)

        # Toggling again removes
        resp = self.client.post(url)
        data = resp.json()
        self.assertTrue(data.get('success'))
        self.assertFalse(data.get('favorited'))
        self.assertEqual(data.get('favorites_count'), 0)

    def test_toggle_favorite_requires_post(self):
        self.client.login(username='fav_user', password='pass123')
        resp = self.client.get(reverse('toggle_favorite', args=[self.cocktail.id]))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertFalse(data.get('success'))
        self.assertIn('POST method required', data.get('error', ''))
