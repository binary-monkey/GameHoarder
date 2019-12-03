from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from game_collection.models import Finished, Abandoned, Played, Playing, Queue, Interested, Wishlist, Tag
from gamehoarder_site.models import Profile


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

    context = {
        "tags": custom,
        "list_type": "interested",
        "titles": titles,
        "profile": profile
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
