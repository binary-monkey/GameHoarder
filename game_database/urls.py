from django.urls import path

from . import views

urlpatterns = [
    path('update', views.update_games, name='update_games'),
    path('clean', views.clean_orphans, name='clean_orphans'),
]
