"""
StirCraft List Forms Module

This module contains all form classes related to cocktail list creation, management, and organization.
Lists in StirCraft can be favorites, custom collections, or auto-generated lists like "Your Creations".

Key Features:
- Custom list creation and editing
- Cocktail membership management (add/remove cocktails from lists)
- Integration with existing List and Cocktail models
- Bootstrap-styled form widgets for professional UI
- Proper validation and error handling

Author: StirCraft Development Team
Date: August 2025
Version: 1.0

Usage Examples:
    # Creating a new list
    list_form = ListForm(user=request.user)
    
    # Managing cocktails in a list
    cocktail_form = ListCocktailForm(instance=list_obj, user=request.user)
    
    # Quick add to favorites
    add_form = QuickAddToListForm(user=request.user)
"""

from django import forms
from django.contrib.auth.models import User
from ..models import List, Cocktail


class ListForm(forms.ModelForm):
    """
    Form for creating and updating cocktail lists.
    Handles basic list information like name and description.
    
    This form is used for both creating new lists and editing existing ones.
    System lists (favorites, creations) have restrictions on what can be edited.
    
    Features:
    - Bootstrap-styled form widgets
    - Validation to prevent duplicate list names per user
    - Dynamic help text based on user context
    - Support for both creation and editing modes
    
    Args:
        user (User): Current user for validation and customization
        
    Example:
        form = ListForm(user=request.user)
        if form.is_valid():
            list_obj = form.save(commit=False)
            list_obj.creator = request.user
            list_obj.save()
    """
    
    class Meta:
        model = List
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter list name (e.g., "Summer Favorites")',
                'maxlength': 100
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description of your list...'
            }),
        }
        help_texts = {
            'name': 'Choose a unique name for your cocktail collection',
            'description': 'Describe what makes this collection special (optional)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Make description optional
        self.fields['description'].required = False
        
        # Customize for editing vs creating
        if self.instance and self.instance.pk:
            # Editing mode
            if not self.instance.is_editable:
                # For system lists, only allow description editing
                self.fields['name'].widget.attrs['readonly'] = True
                self.fields['name'].help_text = 'System list names cannot be changed'
        else:
            # Creation mode
            if self.user:
                self.fields['name'].help_text = f"This will be your personal cocktail collection"

    def clean_name(self):
        """Validate that list name is unique for this user."""
        name = self.cleaned_data.get('name')
        if not name:
            return name
            
        # Check for duplicate names (excluding current instance if editing)
        existing_lists = List.objects.filter(creator=self.user, name=name)
        if self.instance and self.instance.pk:
            existing_lists = existing_lists.exclude(pk=self.instance.pk)
        
        if existing_lists.exists():
            raise forms.ValidationError(
                f'You already have a list named "{name}". Please choose a different name.'
            )
        
        return name

    def clean(self):
        """Additional validation for the entire form."""
        cleaned_data = super().clean()
        
        # Prevent editing of non-editable lists
        if self.instance and self.instance.pk and not self.instance.is_editable:
            # Only allow description changes for system lists
            if 'name' in self.changed_data:
                raise forms.ValidationError(
                    'System lists cannot be renamed.'
                )
        
        return cleaned_data


class ListCocktailForm(forms.ModelForm):
    """
    Form for managing which cocktails are in a list.
    Allows bulk adding/removing of cocktails from collections.
    
    This form provides a multiple selection interface for managing
    cocktail membership in lists. It's used in the list edit view
    to bulk modify list contents.
    
    Features:
    - Multi-select checkbox interface for cocktails
    - Filtered to show only cocktails the user can see
    - Pre-selected with current list contents
    - Search functionality for large cocktail collections
    
    Args:
        user (User): Current user for filtering available cocktails
        
    Example:
        form = ListCocktailForm(instance=list_obj, user=request.user)
        if form.is_valid():
            form.save()  # Updates the list's cocktail membership
    """
    
    cocktails = forms.ModelMultipleChoiceField(
        queryset=Cocktail.objects.none(),  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        required=False,
        help_text='Select cocktails to include in this list'
    )
    
    class Meta:
        model = List
        fields = ['cocktails']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set up cocktail queryset based on user
        if self.user:
            # Show all cocktails (users can add any cocktail to their lists)
            # TODO: Consider privacy settings later
            cocktails = Cocktail.objects.select_related('creator').order_by('name')
            self.fields['cocktails'].queryset = cocktails
            
            # For large numbers of cocktails, consider using a different widget
            cocktail_count = cocktails.count()
            if cocktail_count > 50:
                # Switch to a more manageable widget for large collections
                self.fields['cocktails'].widget = forms.SelectMultiple(attrs={
                    'class': 'form-select',
                    'multiple': True,
                    'size': 10,
                    'data-placeholder': 'Select cocktails...'
                })
        
        # Pre-select current cocktails if editing
        if self.instance and self.instance.pk:
            self.initial['cocktails'] = self.instance.cocktails.all()


class QuickAddToListForm(forms.Form):
    """
    Form for quickly adding a cocktail to one of the user's lists.
    Used in modals or quick-action interfaces.
    
    This form provides a simple dropdown to select from the user's
    existing lists when they want to add a cocktail to a collection.
    
    Features:
    - Dropdown of user's editable lists
    - Excludes system lists that shouldn't be manually modified
    - Optional creation of new list on the fly
    - AJAX-friendly for smooth user experience
    
    Args:
        user (User): Current user to filter available lists
        cocktail (Cocktail, optional): Pre-selected cocktail to add
        
    Example:
        form = QuickAddToListForm(user=request.user, cocktail=cocktail)
        if form.is_valid():
            selected_list = form.cleaned_data['list']
            selected_list.cocktails.add(cocktail)
    """
    
    list = forms.ModelChoiceField(
        queryset=List.objects.none(),  # Will be set in __init__
        empty_label="Choose a list...",
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Select which list to add this cocktail to'
    )
    
    # Optional field for creating a new list on the fly
    new_list_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Or create a new list...'
        }),
        help_text='Leave blank to use existing list, or enter name for new list'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.cocktail = kwargs.pop('cocktail', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Show only editable lists for this user
            user_lists = List.objects.filter(
                creator=self.user,
                is_editable=True
            ).order_by('name')
            self.fields['list'].queryset = user_lists
            
            # If user has no lists, encourage creating one
            if not user_lists.exists():
                self.fields['list'].empty_label = "No lists yet - create one below"
                self.fields['list'].required = False
                self.fields['new_list_name'].required = True
                self.fields['new_list_name'].help_text = 'Enter a name for your first list'

    def clean(self):
        """Validate that either existing list or new list name is provided."""
        cleaned_data = super().clean()
        existing_list = cleaned_data.get('list')
        new_list_name = cleaned_data.get('new_list_name')
        
        if not existing_list and not new_list_name:
            raise forms.ValidationError(
                'Please select an existing list or enter a name for a new list.'
            )
        
        if existing_list and new_list_name:
            raise forms.ValidationError(
                'Please choose either an existing list OR create a new one, not both.'
            )
        
        # If creating new list, check for duplicate names
        if new_list_name and self.user:
            if List.objects.filter(creator=self.user, name=new_list_name).exists():
                raise forms.ValidationError(
                    f'You already have a list named "{new_list_name}". Please choose a different name.'
                )
        
        return cleaned_data

    def save(self):
        """
        Save the form by either adding to existing list or creating new list.
        Returns the list that the cocktail was added to.
        """
        if not self.is_valid():
            return None
            
        existing_list = self.cleaned_data.get('list')
        new_list_name = self.cleaned_data.get('new_list_name')
        
        if existing_list:
            # Add to existing list
            if self.cocktail:
                existing_list.cocktails.add(self.cocktail)
            return existing_list
        
        elif new_list_name and self.user:
            # Create new list and add cocktail
            new_list = List.objects.create(
                name=new_list_name,
                creator=self.user,
                list_type='custom'
            )
            if self.cocktail:
                new_list.cocktails.add(self.cocktail)
            return new_list
        
        return None


class BulkListActionForm(forms.Form):
    """
    Form for performing bulk actions on multiple lists.
    Useful for organizing and managing many lists at once.
    
    This form allows users to select multiple lists and perform
    actions like bulk deletion, bulk tagging, or bulk privacy changes.
    
    Features:
    - Multiple list selection with checkboxes
    - Various bulk actions (delete, export, etc.)
    - Confirmation requirements for destructive actions
    - Filtered to user's own lists only
    
    Args:
        user (User): Current user to filter available lists
        
    Example:
        form = BulkListActionForm(user=request.user)
        if form.is_valid():
            selected_lists = form.cleaned_data['lists']
            action = form.cleaned_data['action']
            # Perform bulk action...
    """
    
    ACTION_CHOICES = [
        ('delete', 'Delete selected lists'),
        ('export', 'Export selected lists'),
        ('make_private', 'Make selected lists private'),
        ('make_public', 'Make selected lists public'),
    ]
    
    lists = forms.ModelMultipleChoiceField(
        queryset=List.objects.none(),  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input'
        }),
        help_text='Select lists to perform bulk actions on'
    )
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Choose what to do with selected lists'
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='I understand this action cannot be undone'
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Show only user's custom lists (exclude system lists)
            user_lists = List.objects.filter(
                creator=self.user,
                list_type='custom',
                is_deletable=True  # Only show deletable lists for bulk actions
            ).order_by('name')
            self.fields['lists'].queryset = user_lists

    def clean(self):
        """Validate bulk actions."""
        cleaned_data = super().clean()
        selected_lists = cleaned_data.get('lists', [])
        action = cleaned_data.get('action')
        
        # Ensure at least one list is selected
        if not selected_lists:
            raise forms.ValidationError('Please select at least one list.')
        
        # Validate that selected lists can be modified
        if action == 'delete':
            non_deletable = [lst for lst in selected_lists if not lst.is_deletable]
            if non_deletable:
                list_names = ', '.join([lst.name for lst in non_deletable])
                raise forms.ValidationError(
                    f'These lists cannot be deleted: {list_names}'
                )
        
        return cleaned_data


# =============================================================================
# 🏷️ LIST SEARCH AND FILTER FORMS
# =============================================================================

class ListSearchForm(forms.Form):
    """
    Form for searching and filtering lists.
    Used in list browsing and user list pages.
    """
    
    query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search lists by name or description...',
            'autocomplete': 'off'
        })
    )
    
    list_type = forms.ChoiceField(
        choices=[
            ('', 'All lists'),
            ('custom', 'Custom lists'),
            ('favorites', 'Favorites'),
            ('creations', 'Your Creations'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-updated_at', 'Recently updated'),
            ('-created_at', 'Newest first'),
            ('created_at', 'Oldest first'),
            ('name', 'Name A-Z'),
            ('-name', 'Name Z-A'),
            ('-cocktails__count', 'Most cocktails'),
        ],
        required=False,
        initial='-updated_at',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_cocktails = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min cocktails',
            'min': '0'
        }),
        help_text='Show lists with at least this many cocktails'
    )


# =============================================================================
# 🎯 QUICK ACTION FORMS
# =============================================================================

class QuickFavoriteForm(forms.Form):
    """
    Simple form for adding/removing cocktails from favorites.
    Used for AJAX favorite toggle functionality.
    """
    
    cocktail_id = forms.IntegerField(widget=forms.HiddenInput())
    action = forms.ChoiceField(
        choices=[('add', 'Add to favorites'), ('remove', 'Remove from favorites')],
        widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_cocktail_id(self):
        """Validate that cocktail exists."""
        cocktail_id = self.cleaned_data.get('cocktail_id')
        try:
            cocktail = Cocktail.objects.get(id=cocktail_id)
            return cocktail_id
        except Cocktail.DoesNotExist:
            raise forms.ValidationError('Cocktail not found.')

    def save(self):
        """Perform the favorite/unfavorite action."""
        if not self.is_valid() or not self.user:
            return None
            
        cocktail_id = self.cleaned_data['cocktail_id']
        action = self.cleaned_data['action']
        
        cocktail = Cocktail.objects.get(id=cocktail_id)
        favorites_list = List.get_or_create_favorites_list(self.user)
        
        if action == 'add':
            favorites_list.cocktails.add(cocktail)
            return True
        elif action == 'remove':
            favorites_list.cocktails.remove(cocktail)
            return False
        
        return None
