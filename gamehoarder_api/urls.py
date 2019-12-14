from django.urls import path

from . import views

urlpatterns = [
    path('stats', views.stats, name='stats'),
    path('collection_stats', views.collection_stats, name='collection_stats'),
]
