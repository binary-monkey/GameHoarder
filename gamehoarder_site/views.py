import csv
import json

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from game_collection.models import Tag
from game_database.models import GameVersion


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


@require_GET
def search(request):
    search_params = {
        # # key: REST param, value: model query
        'developer': 'parent_game__developers__name__contains',
        # 'genre': 'parent_game__genres__in',
        'platform': 'platform__name__iendswith',
        'publisher': 'parent_game__publishers__name__contains',
        'year': 'parent_game__release_date__year',
        'title': 'parent_game__title__contains',
    }
    # GameVersion.objects.filter(=)

    special_params = {
        # # key: special param, value: extraction function
        # 'genre': lambda x: x.split(',')
    }

    params = request.GET.dict()
    query = {}
    for k, v in search_params.items():
        # param is present and not empty
        if k in params.keys() and params.get(k):
            # run extraction function on special param
            if k in special_params.keys():
                query[v] = special_params[k](params.get(k))
            # use raw param
            else:
                query[v] = params.get(k)
    print(query)
    local_games = GameVersion.objects.filter(**query)

    for g in local_games:
        print(vars(g))
    return HttpResponse(200)

def search_form(request):
    return HttpResponse(201)
