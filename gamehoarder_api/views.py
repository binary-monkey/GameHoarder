import json

from django.contrib.auth import authenticate
from django.contrib.auth.models import User, Group
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from game_collection.models import Wishlist, Interested, Queue, Playing, Played, Finished, Abandoned, Review
from gamehoarder_site.models import Profile


def return_options(allowed_methods):
    response = HttpResponse()
    response['allow'] = ','.join(allowed_methods)

    return response


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
        'reviews': Review.objects.all().count()
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
        "completion_rate": round(((count_finished + count_played) * 100) / games, 2)
    }

    return JsonResponse(data)


# @login_required
def user_view(request, username):
    user = User.objects.all().get(username=username)

    data = {
        "id": user.pk,
        "username": user.username,
        "email": user.email,
        "group": Group.objects.all().get(user=user).name
    }

    response = JsonResponse(data)

    response['Access-Control-Allow-Origin'] = '*'

    return response


# @login_required
def user_list(request):
    users = User.objects.all().values("id", "username", "email", "groups__name")

    response = JsonResponse({"data": list(users)})
    response['Access-Control-Allow-Origin'] = '*'

    return response


@csrf_exempt
# @login_required
def edit_user(request):
    if request.method == "OPTIONS":
        response = return_options(["post", "options"])

    elif request.method == "POST":
        post_data = json.loads(str(request.body, encoding='utf-8'))
        print(post_data)
        user = User.objects.all().get(username=post_data["username"])
        new_group = Group.objects.get(name=post_data["group"])

        current_group = user.groups.all()[0]  # A user should only be in 1 group

        if new_group != current_group:
            user.groups.clear()

            new_group.user_set.add(user)

            if new_group.name == "admin":
                user.is_staff = True
            else:
                user.is_staff = False

            user.save()

        response = HttpResponse(status=200)

    else:
        response = HttpResponse(status=405)

    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
    response[
        'Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"

    return response


@csrf_exempt
# @login_required
def delete_user(request):
    if request.method == "OPTIONS":
        response = return_options(["post", "options"])

    elif request.method == "POST":
        post_data = json.loads(str(request.body, encoding='utf-8'))

        user = User.objects.all().get(username=post_data["username"])

        user.delete()

        response = HttpResponse(status=200)

    else:
        response = HttpResponse(status=405)

    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
    response[
        'Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"

    return response


@csrf_exempt
def login(request):
    if request.method == "OPTIONS":
        response = return_options(["post", "options"])

    elif request.method == "POST":
        post_data = json.loads(str(request.body, encoding='utf-8'))

        user = authenticate(username=post_data["username"], password=post_data["password"])
        if user is not None:
            response = HttpResponse(status=200)
        else:
            response = HttpResponse(status=401)

    else:
        response = HttpResponse(status=405)

    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = "GET,POST,PUT,DELETE,OPTIONS"
    response[
        'Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"

    return response
