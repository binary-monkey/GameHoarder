from django.contrib import admin

from game_database.models import *


class GameAdmin(admin.ModelAdmin):
    list_filter = ('genres',)
    list_display = ('release_date', "db_id", 'title', 'main_time', 'extra_time', 'completion_time')
    list_display_links = ('db_id',)
    readonly_fields = ('main_time', 'extra_time', 'completion_time')
    ordering = ('-release_date',)


class GameVersionAdmin(admin.ModelAdmin):
    list_filter = ('platform',)
    list_display = ('release_date', 'db_id', 'platform', 'parent_game',)
    list_display_links = ('db_id',)
    ordering = ('-release_date',)


admin.site.register(Platform)
admin.site.register(Genre)
admin.site.register(Game, GameAdmin)
admin.site.register(GameVersion, GameVersionAdmin)
