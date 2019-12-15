from datetime import datetime
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from game_database.models import GameVersion


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    game_version = models.ForeignKey(GameVersion, on_delete=models.PROTECT, verbose_name=_("game version"))
    price = models.FloatField(default=0.0, verbose_name=_("price"))

    date_adquired = models.DateField(blank=True, null=True, verbose_name=_("date adquired"))
    time_played = models.FloatField(blank=True, null=True, verbose_name=_("time played"))

    class Meta:
        abstract = True
        unique_together = ('user', 'game_version',)

    def __str__(self):
        return self.game_version.__str__()


class Queue(Collection):
    pass


class Playing(Collection):
    date_started = models.DateField(blank=True, null=True, verbose_name=_("date started"))

    class Meta:
        verbose_name = _("Playing")
        verbose_name_plural = _("Playing")


class PlaystyleChoice(Enum):  # A subclass of Enum
    MAIN = "Main Story"
    EXTRA = "Main + Extra"
    COMP = "Completionist"


class Finished(Collection):
    date_started = models.DateField(blank=True, null=True, verbose_name=_("date started"))
    date_finished = models.DateField(blank=True, null=True, verbose_name=_("date finished"))
    time_to_finish = models.FloatField(blank=True, null=True, verbose_name=_("time to finish"))
    playstyle = models.CharField(
        max_length=5,
        choices=[(tag, tag.value) for tag in PlaystyleChoice],
        verbose_name=_("playstyle")
    )

    class Meta:
        verbose_name = _("Finished")
        verbose_name_plural = _("Finished")


class Played(Collection):
    date_started = models.DateField(blank=True, null=True, verbose_name=_("date started"))
    date_stopped = models.DateField(blank=True, null=True, verbose_name=_("date stopped"))

    class Meta:
        verbose_name = _("Played")
        verbose_name_plural = _("Played")


class Abandoned(Collection):
    date_started = models.DateField(blank=True, null=True, verbose_name=_("date started"))
    date_abandoned = models.DateField(blank=True, null=True, verbose_name=_("date abandoned"))

    class Meta:
        verbose_name = _("Abandoned")
        verbose_name_plural = _("Abandoned")


class List(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    game_version = models.ForeignKey(GameVersion, on_delete=models.PROTECT, verbose_name=_("game version"))

    date_added = models.DateField(default=timezone.now, verbose_name=_("date added"))

    class Meta:
        abstract = True
        unique_together = ('user', 'game_version',)

    def __str__(self):
        return self.game_version.__str__()


class Wishlist(List):
    class Meta:
        verbose_name = _("Wishlist")
        verbose_name_plural = _("Wishlist")


class Interested(List):
    class Meta:
        verbose_name = _("Interested")
        verbose_name_plural = _("Interested")


class TagGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    name = models.CharField(max_length=16, verbose_name=_("name"), unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag Group")
        verbose_name_plural = _("Tag Groups")
        unique_together = ('user', 'name',)


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("user"))
    name = models.CharField(max_length=16, verbose_name=_("name"), unique=True)
    game_version = models.ManyToManyField(GameVersion, verbose_name=_("game version"))

    tag_group = models.ForeignKey(TagGroup, on_delete=models.SET_NULL, blank=True, null=True,
                                  verbose_name=_("tag group"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        unique_together = ('user', 'name',)


class Review(models.Model):
    game_version = models.ForeignKey(GameVersion, verbose_name=_("game version"), on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)

    score = models.FloatField(default=5, verbose_name=_("score"))
    text = models.TextField(verbose_name=_("text"))
    date = models.DateField(default=datetime.today(), verbose_name=_("date"))

    def __str__(self):
        return "%s - %s" % (self.user, self.game_version.parent_game.title)

    class Meta:
        verbose_name = _("Review")
        verbose_name_plural = _("Reviews")
        unique_together = ('user', 'game_version',)
