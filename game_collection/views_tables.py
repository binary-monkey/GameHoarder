from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from game_collection.models import Finished, Abandoned, Played, Playing, Queue, Interested, Wishlist, Tag
from game_database.models import Genre, Platform
from gamehoarder_site.models import Profile
from django.http import JsonResponse
from game_database.functions import GameHoarderDB

def ajax_tables(request):
    # multiple-choice values
    choices = ['genres', 'platforms']
    # all values except those
    params = {k: v for k, v in request.GET.dict().items() if k[:-2] not in choices}
    del params['_']
    type_table = params['type']
    del params['type']
    for choice in choices:
        if f'{choice}[]' in request.GET.keys():
            params[choice] = request.GET.getlist(f'{choice}[]')

    new = []
    if not GameHoarderDB.params_empty(params):
        games = GameHoarderDB.table_filter(params)

        initial = None
        if type_table=="Interested":
            initial = Interested.objects.filter(user=request.user)
        elif type_table=="Wishlist":
            initial = Wishlist.objects.filter(user=request.user)
        elif type_table=="Queue":
            initial = Queue.objects.filter(user=request.user)
        elif type_table=="Playing":
            initial = Playing.objects.filter(user=request.user)
        elif type_table=="Finished":
            initial = Finished.objects.filter(user=request.user)
        elif type_table=="Played":
            initial = Played.objects.filter(user=request.user)
        elif type_table=="Abandoned":
            initial = Abandoned.objects.filter(user=request.user)
        else:
            tag = Tag.objects.get(name=type_table, user=request.user)
            initial = tag.game_version.all()
        for i in initial:
            if i.game_version in games:
                new.append(i.game_version.db_id)
    else:
        games = None

    context = {'new_titles': new}
    return JsonResponse(context)

@login_required(login_url='login')
def queue_table(request):
    titles = Queue.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "titles": titles,
        "profile": profile
    }

    return render(request, "collection/tables/queue_table.html", context)


@login_required(login_url='login')
def playing_table(request):
    titles = Playing.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "titles": titles,
        "profile": profile
    }

    return render(request, "collection/tables/playing_table.html", context)


@login_required(login_url='login')
def finished_table(request):
    titles = Finished.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "titles": titles,
        "profile": profile
    }
    return render(request, "collection/tables/finished_table.html", context)


@login_required(login_url='login')
def played_table(request):
    titles = Played.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "titles": titles,
        "profile": profile
    }

    return render(request, "collection/tables/played_table.html", context)


@login_required(login_url='login')
def abandoned_table(request):
    titles = Abandoned.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "titles": titles,
        "profile": profile
    }

    return render(request, "collection/tables/abandoned_table.html", context)


@login_required(login_url='login')
def insterested_table(request):
    titles = Interested.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)
    platforms = [p.get('name') for p in Platform.objects.order_by().values('name').distinct()]
    genres = [g.get('name') for g in Genre.objects.order_by().values('name').distinct()]
    context = {
        "tags": custom,
        "list_type": "interested",
        "titles": titles,
        "profile": profile,
        'first_platform': platforms[0] if len(platforms) > 0 else None,
        'first_genre': genres[0] if len(genres) > 0 else None,
        'platforms': platforms[1:] if len(platforms) > 1 else [],
        'genres': genres[1:] if len(genres) > 1 else [],
    }

    return render(request, "collection/tables/list_table.html", context)


@login_required(login_url='login')
def wishlist_table(request):
    titles = Wishlist.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "list_type": "interested",
        "titles": titles,
        "profile": profile
    }

    return render(request, "collection/tables/list_table.html", context)


@login_required(login_url='login')
def tag_table(request):
    custom = Tag.objects.filter(user=request.user)
    tag = Tag.objects.get(name=request.GET['tag'], user=request.user)
    games = tag.game_version.all()
    profile = Profile.objects.get(user=request.user)

    context = {
        "tags": custom,
        "list_type": "interested",
        "titles": games,
        "profile": profile
    }

    return render(request, "collection/tables/tag_table.html", context)
