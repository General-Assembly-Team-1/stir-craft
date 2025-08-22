from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout  # Add login and logout imports
from django.contrib import messages
from django.db import models
from django.core.paginator import Paginator
from .models import Profile, Vessel, List, Ingredient  # Fixed: List not CocktailList
from .forms.profile_forms import ProfileUpdateForm, SignUpForm
from .forms.list_forms import ListForm  # Fixed: ListForm not CocktailListForm
from .forms.cocktail_forms import QuickIngredientForm  # Fixed: QuickIngredientForm not IngredientForm
from collections import defaultdict  # Import defaultdict for ingredient grouping
from django.views.generic import DetailView
from django.contrib.auth.forms import AuthenticationForm  # Fixed: Use Django's built-in form

# =============================================================================
# �️ UTILITY FUNCTIONS
# =============================================================================

def render_error(request, status_code, error_message=None, exception=None):
    """
    Render a dynamic error page with the specified status code and message.
    
    Args:
        request: Django request object
        status_code: HTTP status code (403, 404, 500, etc.)
        error_message: Custom error message to display
        exception: Exception object for debug information
    
    Returns:
        HttpResponse with the error template and appropriate status code
    """
    context = {
        'status_code': status_code,
        'error_message': error_message,
    }
    
    # Add debug information if in debug mode
    from django.conf import settings
    if settings.DEBUG and exception:
        context['debug'] = True
        context['exception'] = str(exception)
    
    return render(request, 'errors/error.html', context, status=status_code)

# =============================================================================
# �🔑 AUTHENTICATION VIEWS
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

def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # log in immediately after signup
            messages.success(request, "Account created successfully!")
            return redirect("home")  # change to your home URL
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SignUpForm()
    return render(request, "auth/auth.html", {
        "signup_form": form,
        "login_form": AuthenticationForm(),
    })


def sign_in(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, "auth/auth.html", {
        "login_form": form,
        "signup_form": SignUpForm(),
    })


def sign_out(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


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

    return render(request, 'users/profile_detail.html', {
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
    
    return render(request, 'users/profile_update.html', {
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

# -----------------------------------------------------------------------------
# Ingredient Index View
# -----------------------------------------------------------------------------
def ingredient_index(request):
    """
    Display all available ingredients.
    Includes filter by type, search by name, and grouping by category.
    """

    search_query = request.GET.get("q", "")
    filter_type = request.GET.get("type", "")

    ingredients = Ingredient.objects.all()

    if search_query:
        ingredients = ingredients.filter(name__icontains=search_query)

    if filter_type:
        ingredients = ingredients.filter(ingredient_type=filter_type)

    # Group by category for accordion display
    ingredients_by_category = defaultdict(list)
    for ingredient in ingredients:
        ingredients_by_category[ingredient.ingredient_type].append(ingredient)

    context = {
        "ingredients_by_category": ingredients_by_category,
        "categories": Ingredient.INGREDIENT_TYPES,  # [('spirit','Spirit'),...]
        "form": QuickIngredientForm(),  # quick add form
    }
    return render(request, "ingredients/index.html", context)


# -----------------------------------------------------------------------------
# Ingredient Detail View
# -----------------------------------------------------------------------------
def ingredient_detail(request, ingredient_id):
    """
    Show ingredient details and cocktails that use it.
    Display flavor tags, alcohol content, etc.
    """
    from .models import Ingredient, Cocktail
    ingredient = get_object_or_404(Ingredient, id=ingredient_id)

    # If cocktails reference Ingredient through a "Component" model
    cocktails = Cocktail.objects.filter(components__ingredient=ingredient).distinct()

    context = {
        "ingredient": ingredient,
        "cocktails": cocktails,
    }
    return render(request, "ingredients/detail.html", context)


# -----------------------------------------------------------------------------
# Ingredient Create View
# -----------------------------------------------------------------------------
def ingredient_create(request):
    """
    Create new ingredients.
    Handles GET (show form) and POST (save new ingredient).
    """
    if request.method == "POST":
        form = QuickIngredientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("ingredient_index")
    else:
        form = QuickIngredientForm()

    return render(request, "ingredients/ingredient_form.html", {"form": form})


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


def vessel_index(request):
    """
    Display all available vessels/glassware.
    Show capacity, descriptions, images.
    """
    vessels = Vessel.objects.all().order_by('name')  # order alphabetically
    context = {'vessels': vessels}
    return render(request, 'vessels/vessel_index.html', context)


class VesselDetailView(DetailView):
    model = Vessel
    template_name = 'vessels/vessel_detail.html'
    context_object_name = 'vessel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Adjust depending on your Cocktail model ForeignKey related_name
        context['cocktails'] = self.object.cocktail_set.all()
        return context


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
    cocktails = Cocktail.objects.select_related('creator', 'vessel').prefetch_related('components__ingredient', 'vibe_tags')
    
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
    
    return render(request, 'cocktails/index.html', {
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
    
    return render(request, 'cocktails/detail.html', context)

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
    
    return render(request, 'cocktails/create.html', {
        'cocktail_form': cocktail_form,
        'formset': formset,
        'page_title': 'Create New Cocktail',
    })




@login_required
def cocktail_update(request, cocktail_id):
    """
    Edit an existing cocktail. Only the creator may edit.

    - GET: show pre-populated CocktailForm and RecipeComponentFormSet
    - POST: atomically update cocktail and components (create/update/delete)
    """
    from .forms.cocktail_forms import CocktailForm, RecipeComponentFormSet
    from .models import Cocktail
    from django.db import transaction

    cocktail = get_object_or_404(Cocktail, id=cocktail_id)

    # Only creator can edit
    if request.user != cocktail.creator:
        return render_error(request, 403, 'Only the creator of this cocktail can edit it.')

    if request.method == 'POST':
        cocktail_form = CocktailForm(request.POST, instance=cocktail, user=request.user)
        formset = RecipeComponentFormSet(request.POST, instance=cocktail)

        if cocktail_form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    cocktail = cocktail_form.save()
                    # Only call save_m2m if the form has it (for many-to-many fields)
                    if hasattr(cocktail_form, 'save_m2m'):
                        cocktail_form.save_m2m()

                    # Save formset (handles create/update/delete)
                    formset.instance = cocktail
                    components = formset.save()

                    # Recompute alcoholic flag
                    has_alcohol = any(c.ingredient.alcohol_content > 0 for c in cocktail.components.all())
                    if has_alcohol != cocktail.is_alcoholic:
                        cocktail.is_alcoholic = has_alcohol
                        cocktail.save()

                messages.success(request, f'🍸 "{cocktail.name}" has been updated successfully!')
                return redirect('cocktail_detail', cocktail_id=cocktail.id)
            except Exception as e:
                messages.error(request, 'An error occurred saving your cocktail. Please try again.')
                # Continue to re-render the form with the error message
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        cocktail_form = CocktailForm(instance=cocktail, user=request.user)
        formset = RecipeComponentFormSet(instance=cocktail)

    return render(request, 'cocktails/create.html', {
        'cocktail_form': cocktail_form,
        'formset': formset,
        'page_title': f'Edit: {cocktail.name}',
        'cocktail': cocktail,
    })




@login_required
def cocktail_delete(request, cocktail_id):
    """
    Delete a cocktail. Only admin users are allowed to delete (per request).

    - GET: show confirmation page
    - POST: perform deletion and redirect to index
    """
    from .models import Cocktail

    cocktail = get_object_or_404(Cocktail, id=cocktail_id)

    # If the user is staff/admin they may fully delete the cocktail
    if request.user.is_staff:
        if request.method == 'POST':
            name = cocktail.name
            cocktail.delete()
            messages.success(request, f'🍸 "{name}" has been deleted.')
            return redirect('cocktail_index')

        return render(request, 'cocktails/confirm_delete.html', {
            'cocktail': cocktail,
        })

    # If the user is the creator but not staff, anonymize the cocktail instead of deleting
    if request.user == cocktail.creator:
        if request.method == 'POST':
            from django.db import IntegrityError

            original_creator = request.user
            # Ensure an anonymous system user exists
            anonymous, created = User.objects.get_or_create(
                username='anonymous',
                defaults={'email': 'anonymous@localhost'}
            )
            if created:
                anonymous.set_unusable_password()
                anonymous.is_active = False
                anonymous.save()

            # Reassign ownership. Handle unique_together collisions by renaming if needed.
            original_name = cocktail.name
            try:
                cocktail.creator = anonymous
                cocktail.save()
            except IntegrityError:
                # Name conflict for anonymous owner; append suffix until unique
                suffix = 1
                while True:
                    new_name = f"{original_name} (anonymous{'' if suffix==1 else ' '+str(suffix)})"
                    cocktail.name = new_name
                    cocktail.creator = anonymous
                    try:
                        cocktail.save()
                        break
                    except IntegrityError:
                        suffix += 1

            # Ensure the original creator's creations list no longer contains this cocktail
            from .models import List
            try:
                creations_list = List.objects.get(creator=original_creator, list_type='creations')
                creations_list.sync_creations_list()
            except List.DoesNotExist:
                pass

            messages.success(request, f'Your association with "{original_name}" has been removed — it is now anonymous.')
            return redirect('cocktail_detail', cocktail_id=cocktail.id)

        # Show a specialized confirmation for anonymization
        return render(request, 'cocktails/confirm_delete.html', {
            'cocktail': cocktail,
            'anonymize': True,
        })

    # Other non-staff users cannot delete or anonymize cocktails they don't own
    return render_error(request, 403, 'Only the creator or staff can delete this cocktail.')


# =============================================================================
# 📁 LIST VIEWS (Favorites & Collections)
# =============================================================================

def list_detail(request, list_id):
    """
    Display cocktails in a specific list.
    Handle privacy settings, show list metadata.
    Show add/remove buttons for list owner.
    """
    from .models import List, Cocktail
    from .forms.cocktail_forms import CocktailSearchForm
    from django.core.paginator import Paginator
    
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check if user can view this list (for now, all lists are viewable)
    # TODO: Add privacy settings later if needed
    
    # Get cocktails in this list with search/filtering
    cocktails = list_obj.cocktails.select_related('creator', 'vessel').prefetch_related('components__ingredient', 'vibe_tags')
    
    # Handle search within the list
    search_form = CocktailSearchForm(request.GET or None)
    if search_form.is_valid():
        cleaned_data = search_form.cleaned_data
        
        # Text search
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
        
        # Filter by alcoholic
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
        cocktails = cocktails.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(cocktails, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check permissions
    can_edit = request.user.is_authenticated and (
        request.user == list_obj.creator or request.user.is_staff
    ) and list_obj.is_editable
    
    context = {
        'list_obj': list_obj,
        'page_obj': page_obj,
        'search_form': search_form,
        'total_count': paginator.count,
        'can_edit': can_edit,
        'is_owner': request.user == list_obj.creator if request.user.is_authenticated else False,
    }
    
    return render(request, 'lists/detail.html', context)

@login_required
def list_create(request):
    """
    Create new cocktail collection.
    Set name, description for custom lists.
    """
    from .forms.list_forms import ListForm
    
    if request.method == 'POST':
        form = ListForm(request.POST, user=request.user)
        
        if form.is_valid():
            list_obj = form.save(commit=False)
            list_obj.creator = request.user
            list_obj.list_type = 'custom'  # Only custom lists can be created manually
            list_obj.save()
            
            messages.success(request, f'🗂️ List "{list_obj.name}" has been created successfully!')
            return redirect('list_detail', list_id=list_obj.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ListForm(user=request.user)
    
    return render(request, 'lists/list_form.html', {
        'form': form,
        'page_title': 'Create New List',
        'submit_text': 'Create List',
    })

@login_required
def list_update(request, list_id):
    """
    Edit list details (only by creator).
    Add/remove cocktails, change name/description.
    """
    from .forms.list_forms import ListForm, ListCocktailForm
    from .models import List
    
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check permissions
    if request.user != list_obj.creator:
        messages.error(request, "You can only edit your own lists.")
        return redirect('list_detail', list_id=list_id)
    
    if not list_obj.is_editable:
        messages.error(request, "This list cannot be edited.")
        return redirect('list_detail', list_id=list_id)
    
    if request.method == 'POST':
        # Check which form was submitted
        if 'update_details' in request.POST:
            # Update list name/description
            form = ListForm(request.POST, instance=list_obj, user=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, f'List "{list_obj.name}" has been updated successfully!')
                return redirect('list_detail', list_id=list_obj.id)
        
        elif 'update_cocktails' in request.POST:
            # Update cocktail membership
            cocktail_form = ListCocktailForm(request.POST, instance=list_obj, user=request.user)
            if cocktail_form.is_valid():
                cocktail_form.save()
                messages.success(request, 'Cocktail list has been updated!')
                return redirect('list_detail', list_id=list_obj.id)
    else:
        form = ListForm(instance=list_obj, user=request.user)
        cocktail_form = ListCocktailForm(instance=list_obj, user=request.user)
    
    return render(request, 'lists/list_update.html', {
        'list_obj': list_obj,
        'form': form,
        'cocktail_form': cocktail_form,
        'page_title': f'Edit: {list_obj.name}',
    })

@login_required
def add_to_list(request, cocktail_id, list_id):
    """
    Add cocktail to a user's list.
    Handle AJAX requests for quick adding.
    """
    from .models import List, Cocktail
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    # Get the cocktail and list
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check permissions
    if request.user != list_obj.creator:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if not list_obj.is_editable:
        return JsonResponse({'success': False, 'error': 'List is not editable'})
    
    # Add cocktail to list if not already there
    if cocktail in list_obj.cocktails.all():
        return JsonResponse({'success': False, 'error': 'Cocktail already in list'})
    
    list_obj.cocktails.add(cocktail)
    
    # Return success response
    return JsonResponse({
        'success': True,
        'message': f'"{cocktail.name}" added to "{list_obj.name}"',
        'cocktail_count': list_obj.cocktail_count()
    })

@login_required
def remove_from_list(request, cocktail_id, list_id):
    """
    Remove cocktail from a user's list.
    Handle AJAX requests for quick removal.
    """
    from .models import List, Cocktail
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    # Get the cocktail and list
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check permissions
    if request.user != list_obj.creator:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if not list_obj.is_editable:
        return JsonResponse({'success': False, 'error': 'List is not editable'})
    
    # Remove cocktail from list
    if cocktail not in list_obj.cocktails.all():
        return JsonResponse({'success': False, 'error': 'Cocktail not in list'})
    
    list_obj.cocktails.remove(cocktail)
    
    # Return success response
    return JsonResponse({
        'success': True,
        'message': f'"{cocktail.name}" removed from "{list_obj.name}"',
        'cocktail_count': list_obj.cocktail_count()
    })

def user_lists(request, user_id=None):
    """
    Show all lists created by a user.
    Handle privacy filtering for other users.
    """
    from .models import List
    
    # Determine which user's lists to show
    if user_id:
        user = get_object_or_404(User, id=user_id)
    else:
        if not request.user.is_authenticated:
            return redirect('home')
        user = request.user
    
    # Get user's lists (exclude system lists for other users' view)
    if request.user == user:
        # Show all lists for the owner
        lists = List.objects.filter(creator=user).order_by('-updated_at')
    else:
        # For other users, only show custom lists (hide system lists like favorites)
        # TODO: Add privacy settings later
        lists = List.objects.filter(
            creator=user, 
            list_type='custom'
        ).order_by('-updated_at')
    
    # Pagination
    paginator = Paginator(lists, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'user': user,
        'page_obj': page_obj,
        'is_owner': request.user == user,
        'total_count': paginator.count,
    }
    
    return render(request, 'lists/user_lists.html', context)

@login_required
def list_delete(request, list_id):
    """
    Delete a list (only custom lists can be deleted).
    Show confirmation page and handle deletion.
    """
    from .models import List
    
    list_obj = get_object_or_404(List, id=list_id)
    
    # Check permissions
    if request.user != list_obj.creator:
        messages.error(request, "You can only delete your own lists.")
        return redirect('list_detail', list_id=list_id)
    
    if not list_obj.is_deletable:
        messages.error(request, "This list cannot be deleted.")
        return redirect('list_detail', list_id=list_id)
    
    if request.method == 'POST':
        list_name = list_obj.name
        list_obj.delete()
        messages.success(request, f'🗂️ List "{list_name}" has been deleted.')
        return redirect('user_lists')
    
    return render(request, 'lists/confirm_delete.html', {
        'list_obj': list_obj,
    })

@login_required
def toggle_favorite(request, cocktail_id):
    """
    Toggle a cocktail's favorite status for the current user.
    Used for AJAX favorite buttons throughout the site.
    """
    from .models import Cocktail, List
    from django.http import JsonResponse
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST method required'})
    
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)
    favorites_list = List.get_or_create_favorites_list(request.user)
    
    # Check if cocktail is already in favorites
    is_favorited = cocktail in favorites_list.cocktails.all()
    
    if is_favorited:
        # Remove from favorites
        favorites_list.cocktails.remove(cocktail)
        action = 'removed'
        favorited = False
    else:
        # Add to favorites
        favorites_list.cocktails.add(cocktail)
        action = 'added'
        favorited = True
    
    return JsonResponse({
        'success': True,
        'favorited': favorited,
        'action': action,
        'message': f'"{cocktail.name}" {action} {"to" if favorited else "from"} favorites',
        'favorites_count': favorites_list.cocktail_count()
    })

@login_required
def quick_add_modal(request, cocktail_id):
    """
    Show a modal for quickly adding a cocktail to user's lists.
    Returns HTML for insertion into page via AJAX.
    """
    from .models import Cocktail, List
    from .forms.list_forms import QuickAddToListForm
    
    cocktail = get_object_or_404(Cocktail, id=cocktail_id)
    
    if request.method == 'POST':
        form = QuickAddToListForm(request.POST, user=request.user, cocktail=cocktail)
        if form.is_valid():
            target_list = form.save()
            if target_list:
                messages.success(request, f'"{cocktail.name}" added to "{target_list.name}"!')
                return redirect('cocktail_detail', cocktail_id=cocktail.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuickAddToListForm(user=request.user, cocktail=cocktail)
    
    # Get user's current lists that already contain this cocktail
    current_lists = List.objects.filter(
        creator=request.user,
        cocktails=cocktail
    ).values_list('name', flat=True)
    
    return render(request, 'partials/lists/quick_add_modal.html', {
        'form': form,
        'cocktail': cocktail,
        'current_lists': current_lists,
    })

def list_feed(request):
    """
    Show a feed of recently updated public lists.
    Discover new cocktail collections from other users.
    """
    from .models import List
    from django.core.paginator import Paginator
    
    # Get public custom lists (exclude system lists)
    # TODO: Add privacy settings when implemented
    lists = List.objects.filter(
        list_type='custom'
    ).select_related('creator').prefetch_related('cocktails').order_by('-updated_at')
    
    # Add search functionality
    query = request.GET.get('q')
    if query:
        lists = lists.filter(
            models.Q(name__icontains=query) |
            models.Q(description__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(lists, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'lists/list_feed.html', {
        'page_obj': page_obj,
        'query': query,
        'total_count': paginator.count,
    })

@login_required
def list_detail(request, list_id):
    """
    Display cocktails in a specific list.
    Handle privacy settings, show list metadata.
    """
    cocktail_list = get_object_or_404(List, id=list_id)
    
    # For now, only the list creator can view the list
    # TODO: Implement privacy settings with is_public field
    if request.user != cocktail_list.creator:
        messages.error(request, 'You do not have permission to view this list.')
        return redirect('user_lists')  # Redirect to lists index or appropriate page
    
    return render(request, 'lists/detail.html', {
        'list': cocktail_list,
        'cocktails': cocktail_list.cocktails.all(),
    })

# Class-based view for list detail (alternative implementation)
class ListDetailView(DetailView):
    model = List
    template_name = 'lists/detail.html'  # Fixed template path
    context_object_name = 'list'
    
    def get_object(self, queryset=None):
        """Override to handle privacy checks"""
        obj = super().get_object(queryset)
        if not obj.is_public and self.request.user != obj.creator:
            messages.error(self.request, 'You do not have permission to view this list.')
            # You might want to raise Http404 or redirect instead
            return None
        return obj

# Function-based view for list creation
@login_required
def list_create(request):
    """
    Create new cocktail collection.
    Set visibility, name, description.
    """
    if request.method == 'POST':
        form = ListForm(request.POST, user=request.user)
        if form.is_valid():
            cocktail_list = form.save(commit=False)
            cocktail_list.creator = request.user
            cocktail_list.save()
            return redirect('list_detail', list_id=cocktail_list.id)  # Fixed redirect
    else:
        form = ListForm(user=request.user)
    
    return render(request, 'lists/list_form.html', {'form': form})




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
    return render(request, 'base/home.html')

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
    
    Template: users/dashboard.html
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
    
    return render(request, 'users/dashboard.html', context)

def about(request):
    """
    Simple about page describing the app and team.

    This is intentionally lightweight: it renders a template that inherits
    from `base.html` and provides a short description, links to docs, and
    a small team block. Kept minimal so it's safe to render without extra
    context or database access.
    """
    return render(request, 'base/about.html', {
        'page_title': 'About Stir Craft',
    })

# =============================================================================
# Error handlers for production
# These wrappers call the centralized render_error helper so the same
# `errors/error.html` layout is used for 403/404/500 pages.
# =============================================================================
def handler_403(request, exception=None):
    """Return a 403 error page using the centralized error template."""
    return render_error(request, 403, exception=exception)


def handler_404(request, exception=None):
    """Return a 404 error page using the centralized error template."""
    return render_error(request, 404, exception=exception)


def handler_500(request):
    """Return a 500 error page using the centralized error template."""
    return render_error(request, 500, error_message='An internal server error occurred.')
