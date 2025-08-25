"""
Comprehensive Favorites Functionality Test

This test simulates the complete favorites workflow including:
- User authentication
- Template rendering with JavaScript inclusion
- AJAX favorites toggle requests
- Database persistence verification
- Add/Remove functionality

Useful for debugging JavaScript integration issues.
"""

import json
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from stir_craft.models import Cocktail, List

User = get_user_model()


class FavoritesComprehensiveTest(TestCase):
    """Comprehensive test for favorites functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testfavorites',
            password='testpass123',
            email='test@example.com'
        )
        
        # Get a test cocktail (assuming at least one exists)
        self.cocktail = Cocktail.objects.first()
        if not self.cocktail:
            # Create a minimal cocktail for testing if none exists
            self.cocktail = Cocktail.objects.create(
                name="Test Cocktail",
                instructions="Mix ingredients",
                creator=self.user
            )
    
    @override_settings(ALLOWED_HOSTS=['testserver', 'localhost', '127.0.0.1'])
    def test_comprehensive_favorites_workflow(self):
        """Test complete favorites workflow"""
        print("=== COMPREHENSIVE FAVORITES TEST ===\n")
        
        # 1. Test authentication
        login_result = self.client.login(username='testfavorites', password='testpass123')
        self.assertTrue(login_result, "Login should succeed")
        print(f"✅ Login successful: {login_result}")
        
        # 2. Check initial state
        favorites_list = List.objects.filter(creator=self.user, name="Favorites").first()
        is_initially_favorited = False
        if favorites_list:
            is_initially_favorited = self.cocktail in favorites_list.cocktails.all()
        print(f"✅ Initially favorited: {is_initially_favorited}")
        
        # 3. Test cocktail detail page loads with favorites button
        detail_response = self.client.get(f'/cocktails/{self.cocktail.id}/')
        self.assertEqual(detail_response.status_code, 200, "Detail page should load")
        
        detail_content = detail_response.content.decode()
        has_fav_btn = 'id="favorite-btn"' in detail_content
        has_js = 'cocktail-actions.js' in detail_content
        
        self.assertTrue(has_fav_btn, "Should have favorite button")
        self.assertTrue(has_js, "Should include favorites JavaScript")
        
        print(f"✅ Detail page status: {detail_response.status_code}")
        print(f"✅ Has favorite button: {has_fav_btn}")
        print(f"✅ Has JavaScript: {has_js}")
        
        # 4. Test favorites toggle (add)
        print("\n--- Testing Add to Favorites ---")
        toggle_response = self.client.post(
            f'/cocktails/{self.cocktail.id}/favorite/', 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(toggle_response.status_code, 200, "Toggle should succeed")
        
        toggle_data = json.loads(toggle_response.content.decode())
        self.assertTrue(toggle_data.get('success'), "Toggle should be successful")
        
        print(f"✅ Toggle response status: {toggle_response.status_code}")
        print(f"✅ Toggle success: {toggle_data.get('success')}")
        print(f"✅ Action: {toggle_data.get('action')}")
        print(f"✅ Message: {toggle_data.get('message')}")
        print(f"✅ Favorited: {toggle_data.get('favorited')}")
        
        # 5. Verify in database
        favorites_list = List.objects.filter(creator=self.user, name="Favorites").first()
        self.assertIsNotNone(favorites_list, "Favorites list should be created")
        
        is_now_favorited = self.cocktail in favorites_list.cocktails.all()
        self.assertTrue(is_now_favorited, "Cocktail should be in favorites")
        
        print(f"✅ Verified in database: {is_now_favorited}")
        print(f"✅ Favorites list has {favorites_list.cocktails.count()} cocktails")
        
        # 6. Test remove from favorites
        print("\n--- Testing Remove from Favorites ---")
        toggle_response2 = self.client.post(
            f'/cocktails/{self.cocktail.id}/favorite/', 
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(toggle_response2.status_code, 200, "Second toggle should succeed")
        
        toggle_data2 = json.loads(toggle_response2.content.decode())
        self.assertTrue(toggle_data2.get('success'), "Second toggle should be successful")
        self.assertEqual(toggle_data2.get('action'), 'removed', "Should be removal action")
        self.assertFalse(toggle_data2.get('favorited'), "Should not be favorited after removal")
        
        print(f"✅ Second toggle action: {toggle_data2.get('action')}")
        print(f"✅ Second toggle favorited: {toggle_data2.get('favorited')}")
        
        # 7. Verify removal in database
        favorites_list.refresh_from_db()
        is_removed = self.cocktail not in favorites_list.cocktails.all()
        self.assertTrue(is_removed, "Cocktail should be removed from favorites")
        
        # 8. Final status
        print("\n=== FINAL STATUS ===")
        print("✅ Backend favorites functionality: WORKING")
        print("✅ Authentication: WORKING")  
        print("✅ Template rendering: WORKING")
        print("✅ JavaScript inclusion: WORKING")
        print("✅ AJAX endpoints: WORKING")
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")


def run_standalone_test():
    """
    Run comprehensive test as standalone script for debugging
    Usage: python manage.py shell -c "from stir_craft.tests.test_favorites_comprehensive import run_standalone_test; run_standalone_test()"
    """
    import os
    import django
    
    # Setup Django if not already done
    if not django.apps.apps.ready:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')
        django.setup()
    
    from django.test.utils import setup_test_environment, teardown_test_environment
    from django.test.runner import DiscoverRunner
    from django.conf import settings
    
    setup_test_environment()
    runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=True)
    
    # Create test database
    old_config = runner.setup_databases()
    
    try:
        # Run the test
        test = FavoritesComprehensiveTest()
        test.setUp()
        test.test_comprehensive_favorites_workflow()
        print("\n✅ Comprehensive test completed successfully!")
        
    finally:
        # Clean up
        runner.teardown_databases(old_config)
        teardown_test_environment()


if __name__ == "__main__":
    run_standalone_test()
