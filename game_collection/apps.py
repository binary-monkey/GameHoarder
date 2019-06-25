from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GameCollectionConfig(AppConfig):
    name = 'game_collection'
    verbose_name = _("Game Collection")
