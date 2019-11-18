from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('friends', views.friends, name='friends'),
    path('export', views.download_csv, name='download_csv'),
]
