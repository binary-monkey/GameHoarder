from django.http import HttpResponse

from game_database.functions import GiantBombAPI, HowLongToBeatAPI
from game_database.models import Game, GameVersion, Genre, Platform


def update_games(request):
    game_versions = GameVersion.objects.filter(update=True)

    for game_version in game_versions:
        data = GiantBombAPI.load_release(game_version.db_id)["results"]
        GiantBombAPI.update_game_version(game_version, data)

    games = Game.objects.filter(update=True)

    for game in games:
        data = GiantBombAPI.load_game(game.db_id)["results"]
        GiantBombAPI.update_game(game, data)

    games = Game.objects.all()

    for game in games:
        HowLongToBeatAPI.update_game_hltb(game)

    return HttpResponse("OK")


def clean_orphans(request):
    orphan_platform = Platform.objects.filter(gameversion__isnull=True)
    orphan_genres = Genre.objects.filter(game__isnull=True)

    for platform in orphan_platform:
        platform.delete()

    for genre in orphan_genres:
        genre.delete()

    return HttpResponse("OK")
