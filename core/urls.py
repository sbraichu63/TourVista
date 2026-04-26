from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.homepage, name='home'),
    path('packages/', views.package_list, name='packages'),
    path('packages/<slug:slug>/', views.package_detail, name='package_detail'),
    path('wishlist/toggle/<int:pk>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('seasons/', views.seasons_view, name='seasons'),
    path('about/', views.about_view, name='about'),
    path('explore/', views.explore_map, name='explore_map'),
]
