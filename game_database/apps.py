from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class GameDatabaseConfig(AppConfig):
    name = 'game_database'
    verbose_name = _("Game Database")
