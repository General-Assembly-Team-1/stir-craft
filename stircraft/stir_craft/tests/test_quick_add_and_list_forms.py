from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client
from ..forms.list_forms import QuickAddToListForm, ListForm
from ..models import List, Cocktail, Ingredient, Vessel, RecipeComponent


class QuickAddAndListFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='qa_user', password='pass123')
        self.other = User.objects.create_user(username='qa_other', password='pass123')

        # Minimal cocktail setup
        self.vessel = Vessel.objects.create(name='TestGlass', volume=200, material='Glass')
        self.ingredient = Ingredient.objects.create(name='Lime Juice', ingredient_type='juice', alcohol_content=0.0)
        self.cocktail = Cocktail.objects.create(name='QuickAddCocktail', instructions='Stir', creator=self.user, vessel=self.vessel)
        RecipeComponent.objects.create(cocktail=self.cocktail, ingredient=self.ingredient, amount=30.0, unit='ml', order=1)

    def test_quick_add_form_creates_new_list_when_no_existing(self):
        # User has no editable lists yet
        form = QuickAddToListForm(data={'new_list_name': 'My New List'}, user=self.user, cocktail=self.cocktail)
        self.assertTrue(form.is_valid())
        lst = form.save()
        self.assertIsNotNone(lst)
        self.assertEqual(lst.creator, self.user)
        self.assertIn(self.cocktail, lst.cocktails.all())

    def test_quick_add_form_adds_to_existing_list(self):
        lst = List.objects.create(name='Existing', creator=self.user, is_editable=True)
        form = QuickAddToListForm(data={'list': lst.id}, user=self.user, cocktail=self.cocktail)
        self.assertTrue(form.is_valid())
        returned = form.save()
        self.assertEqual(returned, lst)
        self.assertIn(self.cocktail, lst.cocktails.all())

    def test_quick_add_modal_view_get_and_post(self):
        # Create an editable list for the user
        lst = List.objects.create(name='ModalList', creator=self.user, is_editable=True)

        self.client.login(username='qa_user', password='pass123')
        url = reverse('quick_add_modal', args=[self.cocktail.id])

        # GET should return the modal HTML
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('form', resp.context)

        # POST using existing list should redirect to detail
        resp = self.client.post(url, data={'list': lst.id})
        self.assertEqual(resp.status_code, 302)
        # Cocktail should now be in that list
        lst.refresh_from_db()
        self.assertIn(self.cocktail, lst.cocktails.all())

    def test_listform_duplicate_name_validation(self):
        List.objects.create(name='UniqueName', creator=self.user)
        form = ListForm(data={'name': 'UniqueName', 'description': 'x'}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_list_update_owner_can_edit(self):
        lst = List.objects.create(name='Editable', creator=self.user, is_editable=True)
        self.client.login(username='qa_user', password='pass123')
        url = reverse('list_update', args=[lst.id])

        # POST update_details should change name
        resp = self.client.post(url, data={'update_details': '1', 'name': 'Edited Name', 'description': 'desc'})
        self.assertEqual(resp.status_code, 302)
        lst.refresh_from_db()
        self.assertEqual(lst.name, 'Edited Name')

    def test_system_list_cannot_be_renamed(self):
        # Create a system (creations) list which is not editable
        sys_list = List.objects.create(name='Your Creations', creator=self.user, list_type='creations', is_editable=False)
        form = ListForm(instance=sys_list, data={'name': 'NewName', 'description': 'x'}, user=self.user)
        # Clean should raise validation error about renaming system lists
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_bulk_list_action_requires_selection(self):
        from ..forms.list_forms import BulkListActionForm
        form = BulkListActionForm(data={'action': 'delete', 'confirm': True}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
