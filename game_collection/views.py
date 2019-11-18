import csv
import json

from celery.result import AsyncResult
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.shortcuts import render

from GameHoarder.settings import BASE_DIR
from game_collection.tasks import *
from game_collection.models import *


def read_csv(file):
    file_url = BASE_DIR + file

    csv_file = open(file_url)

    return list(csv.reader(csv_file, delimiter=','))


def collection_summary(request):
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom
    }
    return render(request, "collection/collection_summary.html", context)


def import_collection(request):
    if request.method == 'POST':
        custom = Tag.objects.filter(user=request.user)
        if "collection" in request.FILES:
            myfile = request.FILES['collection']
            fs = FileSystemStorage()
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)

            csv_file = read_csv(uploaded_file_url)
            if "remove-header" in request.POST:
                csv_file.pop(0)  # Removes headers

            result = verify_collection_task.delay(csv_file)

            context = {"stage": 2, 'task_id': result.task_id, "tags": custom}

            return render(request, 'collection/import_collection.html', context)

        elif "task_id" in request.POST:
            task_id = request.POST.get("task_id")
            task = AsyncResult(task_id)

            while task.status != "SUCCESS":
                pass

            context = task.get()
            context["stage"] = int(request.POST.get("stage"))
            context["tags"] = custom

            return render(request, 'collection/import_collection.html', context)

        if "titles" in request.POST:

            titles = []

            for row in request.POST.getlist("titles"):
                titles.append(json.loads(row.replace("'", '"')))

            result = import_collection_task.delay(titles, request.user.username)

            context = {"stage": 3, 'task_id': result.task_id, "tags": custom}

            return render(request, 'collection/import_collection.html', context)

    return render(request, 'collection/import_collection.html', {"stage": 1})


def import_list(request):
    if request.method == 'POST':
        custom = Tag.objects.filter(user=request.user)
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

            context = {"stage": 2, 'task_id': result.task_id, "tags": custom}

            return render(request, 'collection/import_list.html', context)

        elif "task_id" in request.POST:
            task_id = request.POST.get("task_id")
            task = AsyncResult(task_id)

            while task.status != "SUCCESS":
                pass

            context = task.get()
            context["stage"] = int(request.POST.get("stage"))
            context["tags"] = custom

            return render(request, 'collection/import_list.html', context)

        if "titles" in request.POST:

            titles = []

            for row in request.POST.getlist("titles"):
                titles.append(json.loads(row.replace("'", '"')))

            result = import_list_task.delay(titles, request.user.username)

            context = {"stage": 3, 'task_id': result.task_id}

            return render(request, 'collection/import_list.html', context)

    return render(request, 'collection/import_list.html', {"stage": 1})


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


def game_search(request):
    return render(request, 'index.html')