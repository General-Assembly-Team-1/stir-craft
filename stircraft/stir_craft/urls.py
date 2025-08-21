from django.urls import path
from . import views

urlpatterns = [
    # 🏠 GENERAL URLS
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 🔑 AUTHENTICATION URLS (placeholders)
    # path('sign-up/', views.sign_up, name='sign_up'),
    # path('sign-in/', views.sign_in, name='sign_in'),

    # 👤 USER & PROFILE URLS
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    # 🍹 COCKTAIL URLS
    path('cocktails/', views.cocktail_index, name='cocktail_index'),
    path('cocktails/<int:cocktail_id>/', views.cocktail_detail, name='cocktail_detail'),
    path('cocktails/create/', views.cocktail_create, name='cocktail_create'),
    path('cocktails/<int:cocktail_id>/edit/', views.cocktail_update, name='cocktail_update'),
    path('cocktails/<int:cocktail_id>/delete/', views.cocktail_delete, name='cocktail_delete'),
]
