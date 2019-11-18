import csv
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from game_collection.models import Tag
from game_database.functions import GameHoarderDB
from game_database.models import Genre, Platform


def index(request):
    custom = Tag.objects.filter(user=request.user)

    context = {
        "tags": custom
    }
    return render(request, "index.html", context)


def friends(request):
    return render(request, "index.html")


def download_csv(request):
    if request.method == 'POST':
        response = HttpResponse(content_type='text/csv')
        data = request.POST.getlist("data")

        response['Content-Disposition'] = 'attachment; filename="%s.csv"' % request.POST.get("filename")

        writer = csv.writer(response)

        headers = json.loads(data[0].replace("'", '"'))
        writer.writerow(headers.keys())

        for row in data:
            title = json.loads(row.replace("'", '"'))

            if 'original_title' in title:
                title["game"] = title["original_title"]
                title.pop("original_title")

            writer.writerow(list(title.values()))

        return response


# @require_GET
# def search(request):
#     params = request.GET.dict()
#     return render(request, 'search/search_table.html', {'games': local_games})


def search(request):
    params = request.GET.dict()
    # if query is empty, don't search
    if not GameHoarderDB.params_empty(params):
        games = GameHoarderDB.search(params)
    else:
        games = None
    platforms = [p.get('name') for p in Platform.objects.order_by().values('name').distinct()]
    genres = [g.get('name') for g in Genre.objects.order_by().values('name').distinct()]
    return render(request, 'search/search_form.html', {
        'first_platform': platforms[0] if len(platforms) > 0 else None,
        'first_genre': genres[0] if len(genres) > 0 else None,
        'platforms': platforms[1:] if len(platforms) > 1 else [],
        'genres': genres[1:] if len(genres) > 1 else [],
        'games': games
    })
