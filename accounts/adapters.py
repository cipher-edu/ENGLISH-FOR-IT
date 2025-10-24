from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site


class CustomAccountAdapter(DefaultAccountAdapter):
    """Custom account adapter with additional functionality"""
    
    def is_open_for_signup(self, request):
        """Check whether site is open for signups"""
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
    
    def save_user(self, request, user, form, commit=True):
        """Save a new user instance using form data"""
        user = super().save_user(request, user, form, commit=False)
        
        # Add custom user fields here if needed
        if hasattr(form, 'cleaned_data'):
            # Example: user.phone = form.cleaned_data.get('phone', '')
            pass
        
        if commit:
            user.save()
        return user
    
    def get_login_redirect_url(self, request):
        """Return the default redirect URL after login"""
        path = "/"
        return path
    
    def get_logout_redirect_url(self, request):
        """Return the redirect URL after logout"""
        path = "/"
        return path


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Custom social account adapter"""
    
    def is_open_for_signup(self, request, sociallogin):
        """Check whether site is open for social signups"""
        return getattr(settings, 'SOCIALACCOUNT_ALLOW_REGISTRATION', True)
    
    def populate_user(self, request, sociallogin, data):
        """Populate user instance from social data"""
        user = super().populate_user(request, sociallogin, data)
        
        # Add custom logic here
        # Example: Set default values based on social provider
        
        return user
    
    def save_user(self, request, sociallogin, form=None):
        """Save social user"""
        user = super().save_user(request, sociallogin, form)
        
        # Add any custom fields or logic here
        # Example: Set user level based on social data
        
        return user