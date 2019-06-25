from django.contrib import admin

from game_collection.models import *


class QueueAdmin(admin.ModelAdmin):
    list_display = ("user", "date_adquired", "__str__", "time_played")
    list_display_links = ('__str__',)
    ordering = ("date_adquired",)


class PlayingAdmin(admin.ModelAdmin):
    list_display = ("user", "date_adquired", "date_started", "__str__", "time_played")
    list_display_links = ('__str__',)
    ordering = ("date_started", "date_adquired",)


class FinishedAdmin(admin.ModelAdmin):
    list_display = ("user", "date_adquired", "date_started", "date_finished",
                    "__str__", "time_played", "time_to_finish", "playstyle")
    list_display_links = ('__str__',)
    ordering = ("date_finished", "date_started", "date_adquired",)


class PlayedAdmin(admin.ModelAdmin):
    list_display = ("user", "date_adquired", "date_started", "__str__", "time_played")
    list_display_links = ('__str__',)
    ordering = ("date_stopped", "date_started", "date_adquired",)


class AbandonedAdmin(admin.ModelAdmin):
    list_display = ("user", "date_adquired", "date_started", "date_abandoned", "__str__", "time_played")
    list_display_links = ('__str__',)
    ordering = ("date_abandoned", "date_started", "date_adquired",)


class InterestedAdmin(admin.ModelAdmin):
    list_display = ("user", "date_added", "__str__",)
    list_display_links = ('__str__',)
    ordering = ("date_added",)


class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "date_added", "__str__",)
    list_display_links = ('__str__',)
    ordering = ("date_added",)


class TagAdmin(admin.ModelAdmin):
    list_display = ("user", "tag_group", "name",)
    list_display_links = ('name',)
    ordering = ("name",)


class TagGroupAdmin(admin.ModelAdmin):
    list_display = ("user", "name",)
    list_display_links = ('name',)
    ordering = ("name",)


admin.site.register(Queue, QueueAdmin)
admin.site.register(Playing, PlayingAdmin)
admin.site.register(Finished, FinishedAdmin)
admin.site.register(Played, PlayedAdmin)
admin.site.register(Abandoned, AbandonedAdmin)

admin.site.register(Interested, InterestedAdmin)
admin.site.register(Wishlist, WishlistAdmin)

admin.site.register(Tag, TagAdmin)
admin.site.register(TagGroup, TagGroupAdmin)
