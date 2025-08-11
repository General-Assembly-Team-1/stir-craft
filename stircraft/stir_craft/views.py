from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile
from .forms.profile_forms import ProfileUpdateForm

# =============================================================================
# 🔑 AUTHENTICATION VIEWS
# =============================================================================

# TODO: Sign Up View
# def sign_up(request):
#     """
#     Allow new users to register for an account.
#     Integrates with SignUpForm to create User and Profile.
#     """
#     pass

# TODO: Sign In View
# def sign_in(request):
#     """
#     Allow existing users to log in to their account.
#     Handles authentication and redirects to home or profile.
#     """
#     pass

# =============================================================================
# 👤 USER & PROFILE VIEWS
# =============================================================================
# the login_required decorator ensures that only authenticated users can access the profile detail view
@login_required
def profile_detail(request, user_id=None):
    """
    Display user profile information.
    If user_id is None, show current user's profile.
    """
    if user_id is None:
        user = request.user
    else:
        user = get_object_or_404(User, id=user_id)

    profile = get_object_or_404(Profile, user=user)

    return render(request, 'stir_craft/profile_detail.html', {
        'profile': profile,
        'user': user,
    })

# TODO: Profile update view
@login_required
def profile_update(request):
    """
    Allow users to update their profile information.
    Handle age validation and form processing.
    Uses ProfileUpdateForm to handle both User and Profile model updates.
    """
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = ProfileUpdateForm(
            request.POST, 
            request.FILES,  # For avatar uploads when implemented
            instance=profile, 
            user=request.user
        )
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_detail')  # Redirect to avoid re-submission
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show form with current data
        form = ProfileUpdateForm(instance=profile, user=request.user)
    
    return render(request, 'stir_craft/profile_update.html', {
        'form': form,
        'profile': profile,
    })

# TODO: Profile list view (browse users)
# def profile_list(request):
#     """
#     Browse other users' profiles.
#     Filter and search functionality.
#     """
#     pass


# =============================================================================
# 🧂 INGREDIENT VIEWS
# =============================================================================

# TODO: Ingredient list view
# def ingredient_list(request):
#     """
#     Display all available ingredients.
#     Filter by type, search by name, sort options.
#     """
#     pass

# TODO: Ingredient detail view
# def ingredient_detail(request, ingredient_id):
#     """
#     Show ingredient details and cocktails that use it.
#     Display flavor tags, alcohol content, etc.
#     """
#     pass

# TODO: Ingredient create view (admin/staff)
# def ingredient_create(request):
#     """
#     Create new ingredients (restricted to staff).
#     Form handling with validation.
#     """
#     pass


# =============================================================================
# 🍸 VESSEL VIEWS
# =============================================================================

# TODO: Vessel list view
# def vessel_list(request):
#     """
#     Display all available vessels/glassware.
#     Show capacity, descriptions, images.
#     """
#     pass

# TODO: Vessel detail view
# def vessel_detail(request, vessel_id):
#     """
#     Show vessel details and cocktails that use it.
#     Display capacity, image, description.
#     """
#     pass


# =============================================================================
# 🍹 COCKTAIL VIEWS
# =============================================================================

# TODO: Cocktail list view (main page)
# def cocktail_list(request):
#     """
#     Main cocktail browsing page.
#     Filter by difficulty, alcohol content, ingredients.
#     Search, sort, pagination functionality.
#     """
#     pass

# TODO: Cocktail detail view
# def cocktail_detail(request, cocktail_id):
#     """
#     Display full cocktail recipe with ingredients and instructions.
#     Show components, preparation notes, creator info.
#     Add to favorites functionality.
#     """
#     pass

# TODO: Cocktail create view
# def cocktail_create(request):
#     """
#     Create new cocktail recipes.
#     Multi-step form with ingredient selection and measurements.
#     Handle RecipeComponent creation.
#     """
#     pass

# TODO: Cocktail update view
# def cocktail_update(request, cocktail_id):
#     """
#     Edit existing cocktail (only by creator).
#     Update recipe components and metadata.
#     """
#     pass

# TODO: Cocktail delete view
# def cocktail_delete(request, cocktail_id):
#     """
#     Delete cocktail (only by creator).
#     Confirmation and cascade handling.
#     """
#     pass


# =============================================================================
# 📁 LIST VIEWS (Favorites & Collections)
# =============================================================================

# TODO: List detail view
# def list_detail(request, list_id):
#     """
#     Display cocktails in a specific list.
#     Handle privacy settings, show list metadata.
#     """
#     pass

# TODO: List create view
# def list_create(request):
#     """
#     Create new cocktail collection.
#     Set visibility, name, description.
#     """
#     pass

# TODO: List update view
# def list_update(request, list_id):
#     """
#     Edit list details (only by creator).
#     Add/remove cocktails, change visibility.
#     """
#     pass

# TODO: Add to list view (AJAX)
# def add_to_list(request, cocktail_id, list_id):
#     """
#     Add cocktail to a user's list.
#     Handle AJAX requests for quick adding.
#     """
#     pass

# TODO: User's lists view
# def user_lists(request, user_id=None):
#     """
#     Show all lists created by a user.
#     Handle privacy filtering for other users.
#     """
#     pass


# =============================================================================
# 🔍 SEARCH & FILTER VIEWS
# =============================================================================

# TODO: Advanced search view
# def advanced_search(request):
#     """
#     Advanced search with multiple filters.
#     Ingredient-based search, difficulty, ABV, etc.
#     """
#     pass

# TODO: Search suggestions (AJAX)
# def search_suggestions(request):
#     """
#     Provide search autocomplete suggestions.
#     Return JSON for cocktail and ingredient names.
#     """
#     pass


# =============================================================================
# 🏠 GENERAL VIEWS
# =============================================================================

def home(request):
    """
    Landing page with featured cocktails and recent additions.
    Show popular recipes, seasonal recommendations.
    """
    # TODO: Implement home page
    # Hero Logo
    # elevator pitch of the app
    # Call to action for users to explore cocktails
    return render(request, 'stir_craft/home.html')

# TODO: About page
# def about(request):
#     """
#     About page with app information and team details.
#     """
#     pass

# Create your views here.
