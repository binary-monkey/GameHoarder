from django.shortcuts import render

from game_collection.models import Finished, Abandoned, Played, Playing, Queue, Interested, Wishlist, Tag


def queue_table(request):
    titles = Queue.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "titles": titles
    }

    return render(request, "collection/tables/queue_table.html", context)


def playing_table(request):
    titles = Playing.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "titles": titles
    }

    return render(request, "collection/tables/playing_table.html", context)


def finished_table(request):
    titles = Finished.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "titles": titles
    }

    return render(request, "collection/tables/finished_table.html", context)


def played_table(request):
    titles = Played.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "titles": titles
    }

    return render(request, "collection/tables/played_table.html", context)


def abandoned_table(request):
    titles = Abandoned.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "titles": titles
    }

    return render(request, "collection/tables/abandoned_table.html", context)


def insterested_table(request):
    titles = Interested.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "list_type": "interested",
        "titles": titles
    }

    return render(request, "collection/tables/list_table.html", context)


def wishlist_table(request):
    titles = Wishlist.objects.filter(user=request.user)
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom,
        "list_type": "wishlist",
        "titles": titles
    }

    return render(request, "collection/tables/list_table.html", context)


def tag_table(request):
    custom = Tag.objects.filter(user=request.user)
    tag = Tag.objects.get(name=request.GET['tag'], user=request.user)
    games = tag.game_version.all()
    context = {
        "tags": custom,
        "list_type": tag.name,
        "titles": games
    }

    return render(request, "collection/tables/tag_table.html", context)
