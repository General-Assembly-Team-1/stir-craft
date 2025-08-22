from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Cocktail, Ingredient, Vessel, RecipeComponent


class CocktailEdgeCasesTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='edge_user', password='pass123')
        self.other = User.objects.create_user(username='other_user', password='pass123')

        # Ingredients
        self.vodka = Ingredient.objects.create(name='Edge Vodka', ingredient_type='spirit', alcohol_content=40.0)
        self.juice = Ingredient.objects.create(name='Edge Juice', ingredient_type='juice', alcohol_content=0.0)

        # Vessels
        self.rocks = Vessel.objects.create(name='Rocks Glass', volume=200, material='Glass')
        self.coupe = Vessel.objects.create(name='Coupe', volume=150, material='Glass')

        # Base cocktails used in several tests
        self.alc = Cocktail.objects.create(name='Alcoholic One', instructions='Mix', creator=self.user, vessel=self.rocks, color='Red', is_alcoholic=True)
        RecipeComponent.objects.create(cocktail=self.alc, ingredient=self.vodka, amount=50.0, unit='ml', order=1)

        self.non_alc = Cocktail.objects.create(name='NonAlcoholic', instructions='Mix', creator=self.user, vessel=self.coupe, color='Yellow', is_alcoholic=False)
        RecipeComponent.objects.create(cocktail=self.non_alc, ingredient=self.juice, amount=100.0, unit='ml', order=1)

    def test_index_filter_by_vessel(self):
        resp = self.client.get(reverse('cocktail_index'), {'vessel': self.rocks.id})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Alcoholic One')
        self.assertNotContains(resp, 'NonAlcoholic')

    def test_index_filter_by_is_alcoholic(self):
        resp = self.client.get(reverse('cocktail_index'), {'is_alcoholic': 'True'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Alcoholic One')
        self.assertNotContains(resp, 'NonAlcoholic')

        resp = self.client.get(reverse('cocktail_index'), {'is_alcoholic': 'False'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'NonAlcoholic')
        self.assertNotContains(resp, 'Alcoholic One')

    def test_index_filter_by_color_and_sorting(self):
        # Color filter
        resp = self.client.get(reverse('cocktail_index'), {'color': 'Red'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Alcoholic One')

        # Sorting by name ascending
        # Create an extra cocktail to test ordering
        Cocktail.objects.create(name='A Cocktail', instructions='a', creator=self.user)
        resp = self.client.get(reverse('cocktail_index'), {'sort_by': 'name'})
        self.assertEqual(resp.status_code, 200)
        # Ensure first page contains 'A Cocktail' before others
        content = resp.content.decode()
        self.assertTrue(content.index('A Cocktail') < content.index('Alcoholic One'))

    def test_pagination_on_index(self):
        # Create many cocktails to force pagination
        for i in range(20):
            Cocktail.objects.create(name=f'Paginated {i}', instructions='x', creator=self.user)

        resp = self.client.get(reverse('cocktail_index'))
        self.assertEqual(resp.status_code, 200)
        # Expect paginator to be present; page_obj in context
        self.assertIn('page_obj', resp.context)
        # Request page 2
        resp2 = self.client.get(reverse('cocktail_index'), {'page': 2})
        self.assertEqual(resp2.status_code, 200)
        self.assertIn('page_obj', resp2.context)

    def test_detail_context_for_unauthenticated_and_non_creator(self):
        # Unauthenticated users should be redirected to login for cocktail details
        resp = self.client.get(reverse('cocktail_detail', args=[self.alc.id]))
        self.assertEqual(resp.status_code, 302)  # Redirect to login
        
        # Non-creator authenticated should be able to view details but not edit
        self.client.login(username='other_user', password='pass123')
        resp = self.client.get(reverse('cocktail_detail', args=[self.alc.id]))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.context.get('can_edit', False))

    def test_create_sets_is_alcoholic_flag(self):
        self.client.login(username='edge_user', password='pass123')
        # Create with alcohol ingredient only
        post_data = {
            'name': 'Created Alc',
            'instructions': 'Mix',
            'vessel': self.rocks.id,
            'is_alcoholic': True,

            'components-TOTAL_FORMS': '1',
            'components-INITIAL_FORMS': '0',
            'components-MIN_NUM_FORMS': '1',
            'components-MAX_NUM_FORMS': '15',
            'components-0-ingredient': self.vodka.id,
            'components-0-amount': '50',
            'components-0-unit': 'ml',
            'components-0-order': '1',
        }
        resp = self.client.post(reverse('cocktail_create'), data=post_data)
        self.assertEqual(resp.status_code, 302)
        c = Cocktail.objects.get(name='Created Alc')
        # Should detect alcohol because ingredient has alcohol_content
        self.assertTrue(c.is_alcoholic)

        # Create with only non-alcoholic ingredient
        post_data['name'] = 'Created NonAlc'
        post_data['components-0-ingredient'] = self.juice.id
        resp = self.client.post(reverse('cocktail_create'), data=post_data)
        self.assertEqual(resp.status_code, 302)
        c2 = Cocktail.objects.get(name='Created NonAlc')
        self.assertFalse(c2.is_alcoholic)
