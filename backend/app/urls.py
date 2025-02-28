# app/urls.py
from django.urls import path
from . import views  # Import views from your app

urlpatterns = [
    # Example path
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('fcHome', views.factCheckHome, name='fcHome'),  # Link this to a view function in views.py
    path('fcResults/', views.factCheckResults, name='fcResults'),
    path('ccHome/', views.consistencyCheckHome, name='ccHome'),  # Link this to a view function in views.py
    path('ccResults/', views.consistencyCheckResults, name='ccResults'),
    path('upload/', views.uploadFile, name='uploadFile'),
]
