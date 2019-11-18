from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
     
    path('login', views.login_register, name='login_register'),
    path('logout', views.logout, name='logout'),
    path('friends', views.friends, name='friends'),
    path('export', views.download_csv, name='download_csv'),

    path('search', views.search, name='search'),
]
