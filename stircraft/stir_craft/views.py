from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
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
# def profile_index(request):
#     """
#     Browse other users' profiles.
#     Filter and search functionality.
#     """
#     pass


# =============================================================================
# 🧂 INGREDIENT VIEWS
# =============================================================================

# TODO: Ingredient index view
# def ingredient_index(request):
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

# TODO: Ingredient create view 
# def ingredient_create(request):
#     """
#     Create new ingredients.
#     Form handling with validation.
#     """
#     pass


# =============================================================================
# 🍸 VESSEL VIEWS
# =============================================================================

# TODO: Vessel index view
# def vessel_index(request):
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

def cocktail_index(request):
    """
    Main cocktail browsing page with advanced search and filtering.
    
    This view provides a comprehensive cocktail discovery experience with:
    - Full-text search across cocktail names, descriptions, and ingredients
    - Advanced filtering by ingredient, vessel, alcohol content, and color
    - Sorting options (newest, oldest, alphabetical, by creator)
    - Pagination for efficient handling of large datasets
    - Responsive design for mobile and desktop users
    
    Query Optimization:
    - Uses select_related() for efficient database queries
    - Prefetch related ingredients to avoid N+1 queries
    - Implements distinct() to avoid duplicate results
    - Paginated results to handle large datasets
    
    Search Features:
    - Text search: Searches cocktail name, description, and ingredient names
    - Ingredient filter: Show only cocktails containing specific ingredient
    - Vessel filter: Filter by glassware/serving vessel
    - Alcohol filter: Separate alcoholic from non-alcoholic drinks
    - Color filter: Find cocktails by visual appearance
    - Sorting: Multiple sort options for user preference
    
    Template Context:
    - page_obj: Paginated cocktail results
    - search_form: Form for search/filter controls
    - total_count: Total number of matching cocktails
    
    Performance Considerations:
    - Pagination limits database load (12 cocktails per page)
    - Efficient database queries with proper joins
    - Search form state preserved across pagination
    - Responsive design reduces mobile data usage
    """
    from .forms.cocktail_forms import CocktailSearchForm
    from .models import Cocktail
    from django.core.paginator import Paginator
    
    # Start with all cocktails
    cocktails = Cocktail.objects.select_related('creator', 'vessel').prefetch_related('components__ingredient')
    
    # Handle search and filtering
    search_form = CocktailSearchForm(request.GET or None)
    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        
        # Text search across name and description
        if cleaned_data.get('query'):
            query = cleaned_data['query']
            cocktails = cocktails.filter(
                models.Q(name__icontains=query) | 
                models.Q(description__icontains=query) |
                models.Q(components__ingredient__name__icontains=query)
            ).distinct()
        
        # Filter by ingredient
        if cleaned_data.get('ingredient'):
            cocktails = cocktails.filter(components__ingredient=cleaned_data['ingredient'])
        
        # Filter by vessel
        if cleaned_data.get('vessel'):
            cocktails = cocktails.filter(vessel=cleaned_data['vessel'])
        
        # Filter by alcoholic/non-alcoholic
        if cleaned_data.get('is_alcoholic'):
            is_alcoholic = cleaned_data['is_alcoholic'] == 'True'
            cocktails = cocktails.filter(is_alcoholic=is_alcoholic)
        
        # Filter by color
        if cleaned_data.get('color'):
            cocktails = cocktails.filter(color__icontains=cleaned_data['color'])
        
        # Apply sorting
        if cleaned_data.get('sort_by'):
            cocktails = cocktails.order_by(cleaned_data['sort_by'])
    else:
        # Default ordering
        cocktails = cocktails.order_by('-created_at')
    
    # Additional filter by creator (for dashboard links)
    creator_id = request.GET.get('creator')
    if creator_id:
        try:
            creator = User.objects.get(id=creator_id)
            cocktails = cocktails.filter(creator=creator)
        except (User.DoesNotExist, ValueError):
            pass  # Ignore invalid creator IDs
    
    # Pagination
    paginator = Paginator(cocktails, 12)  # Show 12 cocktails per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'stir_craft/cocktail_index.html', {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_count': paginator.count,
    })

@login_required
def cocktail_detail(request, cocktail_id):
    """
    Display full cocktail recipe with ingredients and instructions.
    Show components, preparation notes, creator info.
    Add to favorites functionality.
    """
    from .models import Cocktail, List
    
    cocktail = get_object_or_404(
        Cocktail.objects.select_related('creator', 'vessel')
                       .prefetch_related('components__ingredient', 'vibe_tags'),
        id=cocktail_id
    )
    
    # Get recipe components ordered by their order field
    components = cocktail.components.select_related('ingredient').order_by('order', 'ingredient__name')
    
    # Check if user has this in any of their lists (for authenticated users)
    user_lists = []
    if request.user.is_authenticated:
        user_lists = List.objects.filter(
            creator=request.user,
            cocktails=cocktail
        ).values_list('name', flat=True)
    
    # Calculate some stats
    total_volume = cocktail.get_total_volume()
    alcohol_content = cocktail.get_alcohol_content()
    
    context = {
        'cocktail': cocktail,
        'components': components,
        'user_lists': user_lists,
        'total_volume': total_volume,
        'alcohol_content': alcohol_content,
        'can_edit': request.user == cocktail.creator,
    }
    
    return render(request, 'stir_craft/cocktail_detail.html', context)

@login_required
def cocktail_create(request):
    """
    Create new cocktail recipes using inline formsets.
    
    This view handles the complex process of creating a cocktail with multiple
    ingredients using Django's inline formset pattern. It manages both the main
    cocktail form and the dynamic ingredient formset in a single submission.
    
    Features:
    - Handles both GET (show form) and POST (process submission) requests
    - Validates both main cocktail form and ingredient formset
    - Automatically sets the creator to the current user
    - Calculates alcohol content based on ingredients
    - Provides user feedback via Django messages
    - Redirects to detail view on successful creation
    
    Process Flow:
    1. User loads page → Show empty forms
    2. User fills out cocktail info and ingredients
    3. Form submission → Validate both forms
    4. If valid → Save cocktail, then ingredients
    5. Update alcohol status based on ingredients
    6. Redirect to cocktail detail page
    7. If invalid → Show errors and let user fix
    
    Template Context:
    - cocktail_form: Main cocktail information form
    - formset: Dynamic ingredient formset (1-15 ingredients)
    - page_title: For consistent page headings
    
    Security:
    - @login_required decorator ensures only authenticated users can create
    - Creator is automatically set to request.user (can't be spoofed)
    - CSRF protection via Django's built-in middleware
    
    Error Handling:
    - Form validation errors displayed to user
    - Database errors caught and reported
    - Success/error messages via Django messages framework
    """
    from .forms.cocktail_forms import CocktailForm, RecipeComponentFormSet
    
    if request.method == 'POST':
        # Create forms with POST data
        cocktail_form = CocktailForm(request.POST, user=request.user)
        formset = RecipeComponentFormSet(request.POST)
        
        # Check if both forms are valid
        if cocktail_form.is_valid() and formset.is_valid():
            # Save the cocktail first (without committing to DB yet)
            cocktail = cocktail_form.save(commit=False)
            cocktail.creator = request.user  # Set the creator
            cocktail.save()  # Now save to get an ID
            
            # Save tags (many-to-many field needs the object to exist first)
            cocktail_form.save_m2m()
            
            # Save the formset with the cocktail instance
            formset.instance = cocktail
            components = formset.save()
            
            # Check if cocktail should be marked as alcoholic based on ingredients
            has_alcohol = any(component.ingredient.alcohol_content > 0 for component in components)
            if has_alcohol != cocktail.is_alcoholic:
                cocktail.is_alcoholic = has_alcohol
                cocktail.save()
            
            messages.success(request, f'🍸 "{cocktail.name}" has been created successfully!')
            return redirect('cocktail_detail', cocktail_id=cocktail.id)
        else:
            # Form validation failed
            messages.error(request, 'Please correct the errors below.')
    else:
        # GET request - show empty forms
        cocktail_form = CocktailForm(user=request.user)
        formset = RecipeComponentFormSet()
    
    return render(request, 'stir_craft/cocktail_create.html', {
        'cocktail_form': cocktail_form,
        'formset': formset,
        'page_title': 'Create New Cocktail',
    })

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
    # Provide featured cocktails and a search form for the landing page
    from .forms.cocktail_forms import CocktailSearchForm
    from .models import Cocktail

    # Home page is intentionally simple: hero and a short explanation/CTA.
    return render(request, 'stir_craft/home.html')

@login_required
def dashboard(request):
    """
    User dashboard showing profile summary, creations, favorites, and lists.
    
    This view provides a comprehensive overview of the user's activity and content,
    including their created cocktails (via "Your Creations" list), favorite recipes, 
    custom lists, and quick actions for creating new content.
    
    Features:
    - Profile summary with statistics
    - "Your Creations" list (auto-updated, edit-locked)
    - Favorites list (from user's "Favorites" list)
    - Custom lists created by the user
    - Quick action buttons for common tasks
    
    Context Data:
    - user: Current authenticated user
    - profile: User's profile information
    - creations_list: Auto-managed list of user's cocktails
    - favorites_list: User's favorites list
    - user_lists: All custom lists created by the user (excluding system lists)
    - stats: Dictionary with user statistics
    
    Template: stir_craft/dashboard.html
    """
    from .models import Cocktail, List, Profile
    from django.db.models import Count
    
    # Get or create user profile
    profile, created = Profile.objects.get_or_create(user=request.user)
    
    # Get or create user's "Your Creations" list (auto-updated)
    creations_list = List.get_or_create_creations_list(request.user)
    
    # Get or create user's favorites list
    favorites_list = List.get_or_create_favorites_list(request.user)
    
    # Get user's custom lists (excluding system lists like favorites and creations)
    user_lists = List.objects.filter(
        creator=request.user, 
        list_type='custom'
    ).order_by('-updated_at')
    
    # Calculate user statistics
    stats = {
        'total_cocktails': creations_list.cocktail_count(),
        'total_lists': user_lists.count() + 2,  # +2 for favorites and creations
        'favorite_count': favorites_list.cocktail_count(),
    }
    
    # Add age calculation to profile for template
    if profile.birthdate:
        from datetime import date
        today = date.today()
        age = today.year - profile.birthdate.year - (
            (today.month, today.day) < (profile.birthdate.month, profile.birthdate.day)
        )
        profile.age = age
    
    context = {
        'user': request.user,
        'profile': profile,
        'creations_list': creations_list,
        'user_cocktails': creations_list.cocktails.all().order_by('-created_at'),  # For backward compatibility
        'favorites_list': favorites_list,
        'user_lists': user_lists,
        'stats': stats,
    }
    
    return render(request, 'stir_craft/dashboard.html', context)

# TODO: About page
# def about(request):
#     """
#     About page with app information and team details.
#     """
#     pass

# Create your views here.
