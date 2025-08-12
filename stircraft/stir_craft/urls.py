from django.urls import path
from . import views

urlpatterns = [
    # 🏠 GENERAL URLS
    path('', views.home, name='home'),
    
    # 🔑 AUTHENTICATION URLS (TODO: Uncomment when views are implemented)
    # path('sign-up/', views.sign_up, name='sign_up'),
    # path('sign-in/', views.sign_in, name='sign_in'),

    # 👤 USER & PROFILE URLS
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('profile/update/', views.profile_update, name='profile_update'),
]
