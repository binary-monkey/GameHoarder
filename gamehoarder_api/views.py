from django.db.models import Sum
from django.http import JsonResponse

from game_collection.models import Wishlist, Interested, Queue, Playing, Played, Finished, Abandoned
from gamehoarder_site.models import Profile


def stats(request):
    count_interested = Interested.objects.all().count()
    count_wishlist = Wishlist.objects.all().count()
    count_queue = Queue.objects.all().count()
    count_playing = Playing.objects.all().count()
    count_played = Played.objects.all().count()
    count_finished = Finished.objects.all().count()
    count_abandoned = Abandoned.objects.all().count()

    games = count_interested + count_wishlist + count_queue + count_playing + count_played + count_finished + count_abandoned

    hours = 0

    # This check is needed because if the list is empty aggregate returns None
    if count_queue != 0:
        hours += float(Queue.objects.aggregate(Sum("time_played"))["time_played__sum"])
    if count_playing != 0:
        hours += float(Playing.objects.aggregate(Sum("time_played"))["time_played__sum"])
    if count_played != 0:
        hours += float(Played.objects.aggregate(Sum("time_played"))["time_played__sum"])
    if count_finished != 0:
        hours += float(Finished.objects.aggregate(Sum("time_played"))["time_played__sum"])
    if count_abandoned != 0:
        hours += float(Abandoned.objects.aggregate(Sum("time_played"))["time_played__sum"])

    data = {
        'users': Profile.objects.all().count(),
        "games": games,
        'hours': hours,
        'reviews': 3
    }
    return JsonResponse(data)


def collection_stats(request):
    user = request.user



    data = {
        "queue": Queue.objects.filter(user=user).count(),
        "playing": Playing.objects.filter(user=user).count(),
        "played": Played.objects.filter(user=user).count(),
        "finished": Finished.objects.filter(user=user).count(),
        "abandoned": Abandoned.objects.filter(user=user).count()
    }

    data["total"] = data["queue"] + data["playing"] + data["played"] + data["finished"] + data["abandoned"]

    return JsonResponse(data)

def user_stats(request):

    user = request.user

    count_interested = Interested.objects.filter(user=user).count()
    count_wishlist = Wishlist.objects.filter(user=user).count()
    count_queue = Queue.objects.filter(user=user).count()
    count_playing = Playing.objects.filter(user=user).count()
    count_played = Played.objects.filter(user=user).count()
    count_finished = Finished.objects.filter(user=user).count()
    count_abandoned = Abandoned.objects.filter(user=user).count()

    games = count_interested + count_wishlist + count_queue + count_playing + count_played + count_finished + count_abandoned

    hours = 0

    # This check is needed because if the list is empty aggregate returns None
    if count_queue != 0:
        hours += float(Queue.objects.filter(user=user).aggregate(Sum("time_played"))["time_played__sum"])
    if count_playing != 0:
        hours += float(Playing.objects.filter(user=user).aggregate(Sum("time_played"))["time_played__sum"])
    if count_played != 0:
        hours += float(Played.objects.filter(user=user).aggregate(Sum("time_played"))["time_played__sum"])
    if count_finished != 0:
        hours += float(Finished.objects.filter(user=user).aggregate(Sum("time_played"))["time_played__sum"])
    if count_abandoned != 0:
        hours += float(Abandoned.objects.filter(user=user).aggregate(Sum("time_played"))["time_played__sum"])

    data = {
        "games": games,
        "hours": hours,
        "completion_rate": round(((count_finished + count_played)*100)/games, 2)
    }

    return JsonResponse(data)
