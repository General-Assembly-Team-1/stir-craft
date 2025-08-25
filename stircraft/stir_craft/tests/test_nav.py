from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class NavTests(TestCase):
    def test_nav_anonymous_user(self):
        """Anonymous users see About, Browse links and Login; not dashboard/create/admin."""
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'About')
        self.assertContains(resp, 'Browse Cocktails')
        self.assertContains(resp, 'Browse Lists')
        self.assertContains(resp, 'Login')
        self.assertNotContains(resp, 'Dashboard')
        self.assertNotContains(resp, 'Create Cocktail')
        self.assertNotContains(resp, 'Admin')

    def test_nav_authenticated_user(self):
        """Authenticated non-staff users see dashboard/create/profile and logout, not admin."""
        user = User.objects.create_user(username='tester', password='pass')
        self.client.force_login(user)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        # Left-side actions
        self.assertContains(resp, 'Browse Cocktails')
        self.assertContains(resp, 'Browse Lists')
        self.assertContains(resp, 'Dashboard')
        self.assertContains(resp, 'Create Cocktail')
        # Right-side actions
        self.assertContains(resp, 'Dashboard')
        self.assertContains(resp, user.username)
        self.assertNotContains(resp, 'Login')
        self.assertNotContains(resp, 'Admin')

    def test_nav_staff_user(self):
        """Staff users additionally see Admin link."""
        staff = User.objects.create_user(username='adminuser', password='pass', is_staff=True)
        self.client.force_login(staff)
        resp = self.client.get(reverse('home'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Admin')
        self.assertContains(resp, 'Dashboard')
        self.assertContains(resp, 'Create Cocktail')
