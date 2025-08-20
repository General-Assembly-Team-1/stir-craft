# =============================================================================
# 👤 PROFILE FORMS - Sign Up & Profile Management
# =============================================================================
# This file contains all form logic for user profile management including:
# - User registration/sign up with profile creation
# - Profile editing (name, birthdate, location, avatar)
# - Profile deletion confirmation
# 
# Forms handle validation, custom widgets, and Django's built-in User model
# integration with our custom Profile model.
# =============================================================================

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from datetime import date
from ..models import Profile


# =============================================================================
# 🆕 SIGN UP FORM - Combines User + Profile Creation
# =============================================================================

class SignUpForm(UserCreationForm):
    """
    Extended user registration form that creates both User and Profile.
    Used during sign up process to collect all necessary user information.
    
    Combines Django's built-in UserCreationForm with custom Profile fields.
    Handles age validation (21+) and creates Profile instance after User creation.
    """
    
    # Django User model fields (first_name, last_name, email)
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    # Custom Profile model fields
    birthdate = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'placeholder': 'YYYY-MM-DD'
        }),
        help_text="You must be 21 or older to join StirCraft"
    )
    
    location = forms.CharField(
        max_length=10,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your zip code (optional)'
        }),
        help_text="Your zip code helps us suggest local ingredients and bars"
    )
    
    # TODO: Stretch Goal - Add location validation and API lookup
    def clean_location(self):
        """
        Validate zip code format and optionally lookup city/state.
        Future enhancement: Use API call to convert zip to "City, State".
        
        For international support, consider:
        - US: 5 digits (12345) or 9 digits (12345-6789)  
        - Canada: A1A 1A1 format
        - UK: SW1A 1AA format
        - etc.
        """
        location = self.cleaned_data.get('location')
        if location:
            # Basic US zip code validation (stretch goal: expand for international)
            import re
            us_zip_pattern = r'^\d{5}(-\d{4})?$'
            if not re.match(us_zip_pattern, location.strip()):
                # TODO: Add more flexible validation for international postal codes
                pass  # For now, accept any input
                
            # TODO: Stretch Goal - API call to validate and get city/state
            # Example with a geocoding API:
            # try:
            #     city, state, country = self.lookup_location_by_zip(location)
            #     # Store expanded location or validate zip exists
            # except LocationNotFound:
            #     raise ValidationError("Please enter a valid zip code.")
                
        return location
    
    # TODO: Stretch Goal - Location API lookup helper method
    # def lookup_location_by_zip(self, zip_code):
    #     """
    #     Use external API to convert zip code to city, state, country.
    #     
    #     Potential APIs:
    #     - Google Geocoding API
    #     - OpenCage Geocoder  
    #     - Nominatim (free OpenStreetMap)
    #     - Zippopotam.us (free zip code API)
    #     
    #     Returns: (city, state, country) tuple
    #     Raises: LocationNotFound if zip code is invalid
    #     """
    #     pass
    
    # TODO: Add avatar field when image handling is implemented
    # avatar = forms.ImageField(
    #     required=False,
    #     widget=forms.FileInput(attrs={
    #         'class': 'form-control',
    #         'accept': 'image/*'
    #     }),
    #     help_text="Upload a profile picture (optional)"
    # )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        """
        Customize form initialization.
        Add CSS classes and placeholders to password fields.
        Customize password validation help text.
        """
        super().__init__(*args, **kwargs)
        
        # Add CSS classes to password fields (inherited from UserCreationForm)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        
        # Customize password help text for better user guidance
        self.fields['password1'].help_text = (
            "Your password must contain at least 8 characters, "
            "cannot be entirely numeric, and cannot be too common."
        )
        
        # TODO: Stretch Goal - Add custom password validators
        # Django's AUTH_PASSWORD_VALIDATORS in settings.py controls validation
        # Custom validators can be added for specific requirements like:
        # - Must contain at least 1 number
        # - Must contain at least 1 special character  
        # - Cannot contain username or email
        # - Custom length requirements
    
    def clean_email(self):
        """
        Validate that email address is unique.
        Django User model doesn't enforce email uniqueness by default.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    
    def clean_birthdate(self):
        """
        Validate that user is 21 or older.
        This mirrors the validation in the Profile model's clean() method.
        """
        birthdate = self.cleaned_data.get('birthdate')
        if birthdate:
            today = date.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            if age < 21:
                raise ValidationError("You must be at least 21 years old to join StirCraft.")
        return birthdate
    
    def save(self, commit=True):
        """
        Override save to create both User and Profile instances.
        This method is called when form.save() is used in views.
        """
        # Save the User instance first
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create associated Profile instance
            profile = Profile.objects.create(
                user=user,
                birthdate=self.cleaned_data['birthdate'],
                location=self.cleaned_data.get('location', ''),
                # avatar=self.cleaned_data.get('avatar'),  # TODO: Uncomment when avatar is implemented
            )
            
            # TODO: Create default "Favorites" list for new user
            # from ..models import List
            # List.create_default_list(user)
            
        return user


# =============================================================================
# ✏️ PROFILE UPDATE FORM - Edit Existing Profile
# =============================================================================

class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating existing user profiles.
    Allows users to modify their profile information after registration.
    
    Includes both User model fields (name, email) and Profile model fields.
    Used in profile edit views with pre-populated current values.
    """
    
    # Django User model fields that users can update
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your first name'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your last name'
        })
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['birthdate', 'location']  # TODO: Add 'avatar' when implemented
        widgets = {
            'birthdate': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your zip code'
            })
        }
    
    def __init__(self, *args, **kwargs):
        """
        Initialize form with current user data.
        Pre-populate User model fields from the associated user instance.
        """
        self.user = kwargs.pop('user', None)  # Get user instance from view
        super().__init__(*args, **kwargs)
        
        # Pre-populate User model fields if user instance exists
        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        """
        Validate email uniqueness, excluding current user.
        Allow user to keep their current email or change to a unique one.
        """
        email = self.cleaned_data.get('email')
        if self.user and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("An account with this email already exists.")
        return email
    
    def clean_birthdate(self):
        """
        Validate age requirement for profile updates.
        Maintain 21+ age requirement even when updating profile.
        """
        birthdate = self.cleaned_data.get('birthdate')
        if birthdate:
            today = date.today()
            age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
            if age < 21:
                raise ValidationError("You must be at least 21 years old to use StirCraft.")
        return birthdate
    
    def save(self, commit=True):
        """
        Save both User and Profile model updates.
        Update the associated User instance with name and email changes.
        """
        # Save Profile model changes
        profile = super().save(commit=False)
        
        if commit:
            profile.save()
            
            # Update associated User model fields
            if self.user:
                self.user.first_name = self.cleaned_data['first_name']
                self.user.last_name = self.cleaned_data['last_name']
                self.user.email = self.cleaned_data['email']
                self.user.save()
        
        return profile


# =============================================================================
# 🗑️ PROFILE DELETE FORM - Account Deletion Confirmation
# =============================================================================

class ProfileDeleteForm(forms.Form):
    """
    Confirmation form for profile/account deletion.
    Requires user to type their username to confirm deletion.
    
    Used as a safety measure to prevent accidental account deletion.
    Does not inherit from ModelForm as it doesn't save data.
    """
    
    username_confirmation = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type your username to confirm deletion'
        }),
        help_text="Type your exact username to confirm account deletion. This action cannot be undone."
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password to confirm'
        }),
        help_text="Enter your current password for additional security."
    )
    
    def __init__(self, *args, **kwargs):
        """
        Initialize with user instance for validation.
        Store user reference to compare against confirmation input.
        """
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_username_confirmation(self):
        """
        Validate that entered username matches current user's username.
        Case-sensitive comparison for security.
        """
        username_confirmation = self.cleaned_data.get('username_confirmation')
        
        if not self.user:
            raise ValidationError("User validation error.")
        
        if username_confirmation != self.user.username:
            raise ValidationError(
                f"Please type your exact username '{self.user.username}' to confirm deletion."
            )
        
        return username_confirmation
    
    def clean_password(self):
        """
        Validate that entered password matches current user's password.
        """
        password = self.cleaned_data.get('password')
        
        if not self.user:
            raise ValidationError("User validation error.")
        
        if not self.user.check_password(password):
            raise ValidationError("Incorrect password. Please try again.")
        
        return password


# =============================================================================
# 🔒 PASSWORD CHANGE FORM - Security Settings
# =============================================================================

# TODO: Consider adding custom password change form if needed
# Django provides built-in PasswordChangeForm that works well
# Custom implementation would go here if special styling/validation needed

# from django.contrib.auth.forms import PasswordChangeForm
# 
# class CustomPasswordChangeForm(PasswordChangeForm):
#     """
#     Custom password change form with consistent styling.
#     Inherits from Django's built-in PasswordChangeForm.
#     """
#     
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Add custom styling to all fields
#         for field_name, field in self.fields.items():
#             field.widget.attrs.update({'class': 'form-control'})