from django.db import models
from django.utils.translation import ugettext_lazy as _


class Genre(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("name"), unique=True)
    db_id = models.CharField(max_length=16, verbose_name=_("DB ID"), unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")


class Company(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("name"), unique=True)
    db_id = models.CharField(max_length=16, verbose_name=_("DB ID"), unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")


class Game(models.Model):
    title = models.CharField(max_length=64, blank=True, verbose_name=_("title"))

    db_id = models.CharField(max_length=16, verbose_name=_("DB ID"), unique=True)

    main_time = models.FloatField(default=0, verbose_name=_("main time"))
    extra_time = models.FloatField(default=0, verbose_name=_("extra time"))
    completion_time = models.FloatField(default=0, verbose_name=_("completion time"))

    release_date = models.DateField(blank=True, null=True, verbose_name=_("release date"))
    description = models.TextField(verbose_name=_("description"), blank=True)
    img_url = models.CharField(max_length=128, verbose_name=_("image url"), blank=True)

    publishers = models.ManyToManyField(Company, verbose_name=_("publishers"), related_name="game_publishers",
                                        blank=True)
    developers = models.ManyToManyField(Company, verbose_name=_("developers"), related_name="game_developers",
                                        blank=True)

    genres = models.ManyToManyField(Genre, verbose_name=_("genres"))

    update = models.BooleanField(default=True, verbose_name=_("update"))

    def __str__(self):
        if self.title == "":
            return self.db_id
        else:
            return self.title

    class Meta:
        verbose_name = _("Game")
        verbose_name_plural = _("Games")


class Platform(models.Model):
    name = models.CharField(max_length=64, verbose_name=_("name"), blank=True)
    db_id = models.CharField(max_length=16, verbose_name=_("DB ID"), unique=True)

    description = models.TextField(verbose_name=_("description"), blank=True)
    img_url = models.CharField(max_length=128, verbose_name=_("image url"), blank=True)

    update = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Platform")
        verbose_name_plural = _("Platforms")


class GameVersion(models.Model):
    parent_game = models.ForeignKey(Game, on_delete=models.CASCADE)
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE)

    name = models.CharField(max_length=64, verbose_name=_("name"), blank=True)
    release_date = models.DateField(blank=True, null=True, verbose_name=_("release date"))

    db_id = models.CharField(max_length=16)

    publishers = models.ManyToManyField(Company, verbose_name=_("publishers"), related_name="version_publishers",
                                        blank=True)
    developers = models.ManyToManyField(Company, verbose_name=_("developers"), related_name="version_developers",
                                        blank=True)

    update = models.BooleanField(default=True)

    def __str__(self):
        if self.parent_game is None or self.platform is None:
            return self.db_id
        else:
            return "%s - %s" % (self.platform, self.parent_game)

    class Meta:
        verbose_name = _("Game Version")
        verbose_name_plural = _("Game Versions")
