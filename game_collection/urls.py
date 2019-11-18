from django.urls import path

from . import views, views_tables

urlpatterns = [

    path('list/import', views.import_list, name='import_lists'),
    path('list/export', views.export_list, name='export_lists'),

    path('list/interested', views_tables.insterested_table, name='interested_table'),
    path('list/wishlist', views_tables.wishlist_table, name='wishlist_table'),

    path('collection/', views.collection_summary, name='collection_summary'),
    path('collection/import', views.import_collection, name='import_collection'),
    path('collection/export', views.export_collection, name='export_collection'),

    path('collection/queue', views_tables.queue_table, name='queue_table'),
    path('collection/playing', views_tables.playing_table, name='playing_table'),
    path('collection/finished', views_tables.finished_table, name='finished_table'),
    path('collection/played', views_tables.played_table, name='played_table'),
    path('collection/abandoned', views_tables.abandoned_table, name='abandoned_table'),

    path('search', views.game_search, name='game_search'),
    path('tag/', views_tables.tag_table, name='tag_table'),

    path('game/<str:id>', views.game_view, name='game_view'),
]
