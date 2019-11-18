from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from game_database.functions import HowLongToBeatAPI, GameCollectionController
from game_database.models import Game, GameVersion, Genre, Platform


@login_required(login_url='login')
def update_games(request):
    game_versions = GameVersion.objects.filter(update=True)

    for game_version in game_versions:
        GameCollectionController.update_game_version(game_version)

    games = Game.objects.filter(update=True)

    for game in games:
        GameCollectionController.update_game(game)

    games = Game.objects.all()

    for game in games:
        HowLongToBeatAPI.update_game_hltb(game)

    return HttpResponse("OK")


@login_required(login_url='login')
def clean_orphans(request):
    orphan_platform = Platform.objects.filter(gameversion__isnull=True)
    orphan_genres = Genre.objects.filter(game__isnull=True)

    for platform in orphan_platform:
        platform.delete()

    for genre in orphan_genres:
        genre.delete()

    return HttpResponse("OK")
