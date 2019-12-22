from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),

    url(r'^password_reset/$',
        auth_views.PasswordResetView.as_view(template_name="registration/password_reset_form.html"),
        name='password_reset'),
    url(r'^password_reset/done/$',
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"),
        name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"),
        name='password_reset_confirm'),
    url(r'^reset/done/$',
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"),
        name='password_reset_complete'),

    path('export', views.download_csv, name='download_csv'),
    path('search', views.search, name='search'),
    path('login', views.login_register, name='login'),
    path('logout', views.logout, name='logout'),
    path('profile', views.profileView, name='profileView'),
    path('profile/<int:pk>/', views.profileView, name='profile_with_pk'),
    path('edit_user', views.edit_user, name='edit_user'),
    path('search_users', views.search_users, name='search_users'),

    url(r'^connect/(?P<operation>.+)/(?P<pk>\d+)/$', views.change_friends, name='change_friends'),

]
