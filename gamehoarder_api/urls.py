from django.urls import path

from . import views

urlpatterns = [

    path('login', views.login, name="api_login"),

    path('stats', views.stats, name='stats'),
    path('stats/collection', views.collection_stats, name='collection_stats'),
    path('stats/user', views.user_stats, name='user_stats'),

    path('users', views.user_list, name='user_list'),
    path('users/delete', views.delete_user, name='delete_user'),
    path('users/edit', views.edit_user, name='api_edit_user'),
    path('users/<str:username>', views.user_view, name='api_user_view'),
]
