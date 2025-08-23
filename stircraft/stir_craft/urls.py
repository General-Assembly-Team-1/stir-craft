from django.urls import path
from . import views

urlpatterns = [
    # 🏠 GENERAL URLS
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # 🔑 AUTHENTICATION URLS 
    path('sign-up/', views.sign_up, name='signup'),
    path('sign-in/', views.sign_in, name='login'),
    path('sign-out/', views.sign_out, name='logout'),

    # 👤 USER & PROFILE URLS
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/<int:user_id>/', views.profile_detail, name='profile_detail'),
    path('profile/update/', views.profile_update, name='profile_update'),
    
    # 🍹 COCKTAIL URLS
    path('cocktails/', views.cocktail_index, name='cocktail_index'),
    path('cocktails/<int:cocktail_id>/', views.cocktail_detail, name='cocktail_detail'),
    path('cocktails/create/', views.cocktail_create, name='cocktail_create'),
    path('cocktails/<int:fork_from_id>/fork/', views.cocktail_create, name='cocktail_fork'),
    path('cocktails/<int:cocktail_id>/edit/', views.cocktail_update, name='cocktail_update'),
    path('cocktails/<int:cocktail_id>/delete/', views.cocktail_delete, name='cocktail_delete'),
    
    # 📁 LIST URLS
    path('lists/', views.user_lists, name='user_lists'),
    path('lists/create/', views.list_create, name='list_create'),
    path('lists/feed/', views.list_feed, name='list_feed'),
    path('lists/<int:list_id>/', views.list_detail, name='list_detail'),
    path('lists/<int:list_id>/edit/', views.list_update, name='list_update'),
    path('lists/<int:list_id>/delete/', views.list_delete, name='list_delete'),
    path('users/<int:user_id>/lists/', views.user_lists, name='user_lists'),
    
    # 🎯 AJAX LIST ACTIONS
    path('cocktails/<int:cocktail_id>/add-to-list/<int:list_id>/', views.add_to_list, name='add_to_list'),
    path('cocktails/<int:cocktail_id>/quick-add-to-list/', views.quick_add_to_list, name='quick_add_to_list'),
    path('cocktails/<int:cocktail_id>/remove-from-list/<int:list_id>/', views.remove_from_list, name='remove_from_list'),
    path('cocktails/<int:cocktail_id>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('cocktails/<int:cocktail_id>/quick-add/', views.quick_add_modal, name='quick_add_modal'),
    
    # 🥃 INGREDIENT URLS (updated to follow naming conventions)
    path('ingredients/', views.ingredient_index, name='ingredient_index'),
    path('ingredients/<int:ingredient_id>/', views.ingredient_detail, name='ingredient_detail'),
    path('ingredients/create/', views.ingredient_create, name='ingredient_add'),
    
    # 🍸 VESSEL URLS (updated to follow naming conventions)
    path('vessels/', views.vessel_index, name='vessel_index'),
    path('vessels/<int:pk>/', views.VesselDetailView.as_view(), name='vessel_detail'),
    
    # General
    path('about/', views.about, name='about'),
]
