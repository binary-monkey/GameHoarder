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
        hours += float(Played.objects.aggregate(Sum("time_played"))["time_played__sum"])
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
