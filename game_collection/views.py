import csv
import datetime
import json

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.utils.translation import to_locale, get_language

from game_collection.forms import *
from game_collection.tasks import *
from game_collection.models import *
from gamehoarder_site.functions import read_csv
from gamehoarder_site.models import Profile


@login_required(login_url='login')
def collection_summary(request):
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)
    context = {
        "tags": custom,
        "profile": profile
    }
    return render(request, "collection/collection_summary.html", context)


@login_required(login_url='login')
def import_collection(request):
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if "collection" in request.FILES:
            myfile = request.FILES['collection']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            csv_file = read_csv(uploaded_file_url)
            if "remove-header" in request.POST:
                csv_file.pop(0)  # Removes headers

            result = verify_collection_task.delay(csv_file)

            context = {"stage": 2, 'task_id': result.task_id, "tags": custom, "profile": profile}

            return render(request, 'collection/import_collection.html', context)

        elif "task_id" in request.POST:
            task_id = request.POST.get("task_id")
            task = AsyncResult(task_id)

            while task.status != "SUCCESS":
                pass

            context = task.get()
            context["stage"] = int(request.POST.get("stage"))
            context["tags"] = custom
            context["profile"] = profile

            return render(request, 'collection/import_collection.html', context)

        if "titles" in request.POST:

            titles = []

            for row in request.POST.getlist("titles"):
                titles.append(json.loads(row.replace("'", '"')))

            result = import_collection_task.delay(titles, request.user.username)

            context = {"stage": 3, 'task_id': result.task_id, "tags": custom, "profile": profile}

            return render(request, 'collection/import_collection.html', context)

    return render(request, 'collection/import_collection.html', {"stage": 1})


@login_required(login_url='login')
def import_list(request):
    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)
    if request.method == 'POST':
        if "list" in request.FILES:
            myfile = request.FILES['list']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            csv_file = read_csv(uploaded_file_url)
            if "remove-header" in request.POST:
                csv_file.pop(0)  # Removes headers

            # print(csv_file)

            result = verify_list_task.delay(csv_file)

            context = {"stage": 2, 'task_id': result.task_id, "tags": custom, "profile": profile}

            return render(request, 'collection/import_list.html', context)

        elif "task_id" in request.POST:
            task_id = request.POST.get("task_id")
            task = AsyncResult(task_id)

            while task.status != "SUCCESS":
                pass

            context = task.get()
            context["stage"] = int(request.POST.get("stage"))
            context["tags"] = custom
            context["profile"] = profile

            return render(request, 'collection/import_list.html', context)

        if "titles" in request.POST:

            titles = []

            for row in request.POST.getlist("titles"):
                titles.append(json.loads(row.replace("'", '"')))

            result = import_list_task.delay(titles, request.user.username)

            context = {"stage": 3, 'task_id': result.task_id, "tags": custom, "profile": profile}

            return render(request, 'collection/import_list.html', context)

    return render(request, 'collection/import_list.html', {"stage": 1})


@login_required(login_url='login')
def export_collection(request):
    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="%s_collection.csv"' % request.user.username

    writer = csv.writer(response)

    writer.writerow(["List", "Date Adquired", "Date Started", "Second Date", "Platform", "Game", "Giantbomb id",
                     "Time Played", "Time Finish", "Playstyle", "Tags"])

    queue_titles = Queue.objects.filter(user=request.user)

    for title in queue_titles:

        if title.date_adquired is not None:
            date_adquired = title.date_adquired.strftime("%Y-%m-%d")
        else:
            date_adquired = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        if title.time_played is not None:
            time_played = str(title.time_played)
        else:
            time_played = ""

        tags = ""

        row = ["Queue", date_adquired, "", "", platform, game_name, db_id,
               time_played, "", "", tags]

        writer.writerow(row)

    playing_titles = Playing.objects.filter(user=request.user)

    for title in playing_titles:

        if title.date_adquired is not None:
            date_adquired = title.date_adquired.strftime("%Y-%m-%d")
        else:
            date_adquired = ""

        if title.date_started is not None:
            date_started = title.date_started.strftime("%Y-%m-%d")
        else:
            date_started = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        if title.time_played is not None:
            time_played = str(title.time_played)
        else:
            time_played = ""

        tags = ""

        row = ["Finished", date_adquired, date_started, "", platform, game_name, db_id,
               time_played, "", "", tags]

        writer.writerow(row)

    finished_titles = Finished.objects.filter(user=request.user)

    for title in finished_titles:

        if title.date_adquired is not None:
            date_adquired = title.date_adquired.strftime("%Y-%m-%d")
        else:
            date_adquired = ""

        if title.date_started is not None:
            date_started = title.date_started.strftime("%Y-%m-%d")
        else:
            date_started = ""

        if title.date_finished is not None:
            date_finished = title.date_finished.strftime("%Y-%m-%d")
        else:
            date_finished = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        if title.time_played is not None:
            time_played = str(title.time_played)
        else:
            time_played = ""

        if title.time_to_finish is not None:
            time_finished = str(title.time_to_finish)
        else:
            time_finished = ""

        if title.playstyle is not None:
            playstyle = title.playstyle
        else:
            playstyle = ""

        tags = ""

        row = ["Finished", date_adquired, date_started, date_finished, platform, game_name, db_id,
               time_played, time_finished, playstyle, tags]

        writer.writerow(row)

    played_titles = Played.objects.filter(user=request.user)

    for title in played_titles:

        if title.date_adquired is not None:
            date_adquired = title.date_adquired.strftime("%Y-%m-%d")
        else:
            date_adquired = ""

        if title.date_started is not None:
            date_started = title.date_started.strftime("%Y-%m-%d")
        else:
            date_started = ""

        if title.date_stopped is not None:
            date_stopped = title.date_stopped.strftime("%Y-%m-%d")
        else:
            date_stopped = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        if title.time_played is not None:
            time_played = str(title.time_played)
        else:
            time_played = ""

        tags = ""

        row = ["Finished", date_adquired, date_started, date_stopped, platform, game_name, db_id,
               time_played, "", "", tags]

        writer.writerow(row)

    abandoned_titles = Abandoned.objects.filter(user=request.user)

    for title in abandoned_titles:

        if title.date_adquired is not None:
            date_adquired = title.date_adquired.strftime("%Y-%m-%d")
        else:
            date_adquired = ""

        if title.date_started is not None:
            date_started = title.date_started.strftime("%Y-%m-%d")
        else:
            date_started = ""

        if title.date_abandoned is not None:
            date_abandoned = title.date_abandoned.strftime("%Y-%m-%d")
        else:
            date_abandoned = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        if title.time_played is not None:
            time_played = str(title.time_played)
        else:
            time_played = ""

        tags = ""

        row = ["Abandoned", date_adquired, date_started, date_abandoned, platform, game_name, db_id,
               time_played, "", "", tags]

        writer.writerow(row)

    return response


@login_required(login_url='login')
def export_list(request):
    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="%s_collection.csv"' % request.user.username

    writer = csv.writer(response)

    writer.writerow(["List", "Date Added", "Platform", "Game", "Giantbomb id", "Tags"])

    insterested_list = Interested.objects.filter(user=request.user)

    for title in insterested_list:

        if title.date_added is not None:
            date_added = title.date_added.strftime("%Y-%m-%d")
        else:
            date_added = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        tags = ""

        row = ["Interested", date_added, platform, game_name, db_id, tags]

        writer.writerow(row)

    wishlist_titles = Wishlist.objects.filter(user=request.user)

    for title in wishlist_titles:

        if title.date_added is not None:
            date_added = title.date_added.strftime("%Y-%m-%d")
        else:
            date_added = ""

        platform = title.game_version.platform.name
        game_name = title.game_version.parent_game.title
        db_id = title.game_version.parent_game.db_id

        tags = ""

        row = ["Wishlist", date_added, platform, game_name, db_id, tags]

        writer.writerow(row)

    return response


@login_required(login_url='login')
def game_view(request, db_id):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            text = form['text'].value()
            score = form['score'].value()
            try:
                new_review = Review(user=request.user, text=text, score=score, game_version=GameVersion.objects.get(db_id=db_id))
                new_review.save()
            except: # Just for some cases when the browser saves the form reloading
                pass

    can_review = not (len(Review.objects.filter(user=request.user, game_version__db_id=db_id))>0)

    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)
    game_version = GameVersion.objects.get(db_id=db_id)

    title = game_version.parent_game
    genres = title.genres.all()
    publishers = title.publishers.all()
    developers = title.developers.all()

    states = [['Played'], ['Playing'], ['Finished'], ['Abandoned'], ['Queue']]

    game_version = GameVersion.objects.get(db_id=db_id)

    states[0].append(len(Played.objects.filter(game_version=game_version)))
    states[1].append(len(Playing.objects.filter(game_version=game_version)))
    states[2].append(len(Finished.objects.filter(game_version=game_version)))
    states[3].append(len(Abandoned.objects.filter(game_version=game_version)))
    states[4].append(len(Queue.objects.filter(game_version=game_version)))

    context = {
        "tags": custom,
        "profile": profile,
        "genres": genres,
        "publishers": publishers,
        "developers": developers,
        "states": states,
        "title": title,
        "game_version": game_version,
        "current_state": GameCollectionController.where_is(game_version, request.user)[0],
        "current_item": GameCollectionController.where_is(game_version, request.user)[1],
        "can_review": can_review
    }

    return render(request, 'collection/game_view.html', context)


@login_required(login_url='login')
def add_game(request, db_id):
    game_version = GameVersion.objects.get(db_id=db_id)
    user = request.user

    Interested.objects.create(game_version=game_version, user=user)

    return redirect("/%s/game/%s" % (to_locale(get_language()), db_id))


@login_required(login_url='login')
def move_game(request, db_id):
    game_version = GameVersion.objects.get(db_id=db_id)
    user = request.user
    current_item = GameCollectionController.where_is(game_version, user)[1]

    if request.method == 'POST':

        form = MoveForm(request.POST)

        print(form.errors)

        if form.is_valid():

            new_item = {
                "user": user,
                "game_version": game_version,
                "price": form.cleaned_data["price"],
                "date_adquired": datetime.datetime.strptime(form.cleaned_data['date_adquired'], "%m/%d/%Y"),
                "time_played": form.cleaned_data["time_played"],
            }

            new_state = form.cleaned_data["new_state"]

            if new_state == 1:
                Interested.objects.create(user=user, game_version=game_version)

            if new_state == 2:
                Wishlist.objects.create(user=user, game_version=game_version)

            if new_state == 3:
                Queue.objects.create(**new_item)

            elif new_state == 4:
                new_item["date_started"] = datetime.datetime.strptime(form.cleaned_data['date_started'], "%m/%d/%Y")

                Playing.objects.create(**new_item)

            elif new_state == 5:
                new_item["date_started"] = datetime.datetime.strptime(form.cleaned_data['date_started'], "%m/%d/%Y")
                new_item["date_stopped"] = datetime.datetime.strptime(form.cleaned_data['date_other'], "%m/%d/%Y")

                Played.objects.create(**new_item)

            elif new_state == 6:
                new_item["date_started"] = datetime.datetime.strptime(form.cleaned_data['date_started'], "%m/%d/%Y")
                new_item["date_finished"] = datetime.datetime.strptime(form.cleaned_data['date_other'], "%m/%d/%Y")

                new_item["time_to_finish"] = form.cleaned_data["time_other"]

                Finished.objects.create(**new_item)

            elif new_state == 7:
                new_item["date_started"] = datetime.datetime.strptime(form.cleaned_data['date_started'], "%m/%d/%Y")
                new_item["date_abandoned"] = datetime.datetime.strptime(form.cleaned_data['date_other'], "%m/%d/%Y")

                Abandoned.objects.create(**new_item)

            current_item.delete()

            return redirect("/%s/game/%s" % (to_locale(get_language()), db_id))

    else:
        form = MoveForm()

    custom = Tag.objects.filter(user=request.user)
    profile = Profile.objects.get(user=request.user)

    collection_states = ["Interested", "Wishlist", 'Queue', 'Playing', 'Played', 'Finished', 'Abandoned']

    context = {
        "tags": custom,
        "profile": profile,
        "game_version": game_version,
        "user": user,
        "form": form,
        "collection_states": collection_states,
        "current_state": GameCollectionController.where_is(game_version, user)[0],
        "current_item": current_item
    }

    return render(request, "collection/forms/move_game.html", context)
