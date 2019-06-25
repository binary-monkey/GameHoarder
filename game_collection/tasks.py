from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.contrib.auth.models import User

from game_collection.models import Tag, Finished, Queue, Playing, Abandoned, Played, Interested, Wishlist
from game_database.functions import GiantBombAPI, GameCollectionController
from game_database.models import Platform, Game, GameVersion


@shared_task(bind=True)
def verify_collection_task(self, csv_file):
    imported_id = 0
    imported_search = 0
    failed = 0

    id_titles = []
    searched_titles = []
    error_search = []
    failed_titles = []

    progress_recorder = ProgressRecorder(self)
    total_titles = len(csv_file)

    for i in range(total_titles):

        row = csv_file[i]

        title = {
            "list": row[0].strip(),
            "date_adquired": row[1].strip(),
            "date_started": row[2].strip(),
            "second_date": row[3].strip(),
            "platform": row[4].strip(),
            "name": row[5].strip().replace("'", ""),
            "id": row[6].strip(),
            "time_played": row[7].strip(),
            "time_to_finish": row[8].strip(),
            "playstyle": row[9].strip(),
            "tags": row[10].strip()
        }

        if title["id"] == "":

            platform_name = title["platform"]
            original_name = title["name"]

            result = GiantBombAPI.search_game(original_name, platform_name, 10)
            if result is not None:

                title["id"] = result["id"]
                title["name"] = result["name"].replace("'", "")

                if original_name.lower() == title["name"].lower():
                    searched_titles.append(title)
                else:
                    title["original_name"] = original_name
                    error_search.append(title)

                imported_search += 1
            else:

                failed_titles.append(title)
                failed += 1

        else:
            id_titles.append(title)
            imported_id += 1

        progress_recorder.set_progress(i + 1, total_titles)

    context = {
        "imported_id": imported_id,
        "imported_search": imported_search,
        "failed": failed,
        "id_titles": id_titles,
        "searched_titles": searched_titles,
        "error_search": error_search,
        "failed_titles": failed_titles
    }

    return context


@shared_task(bind=True)
def verify_list_task(self, csv_file):
    imported_id = 0
    imported_search = 0
    failed = 0

    id_titles = []
    searched_titles = []
    error_search = []
    failed_titles = []

    progress_recorder = ProgressRecorder(self)
    total_titles = len(csv_file)

    for i in range(total_titles):

        row = csv_file[i]

        title = {
            "list": row[0].strip(),
            "date_added": row[1].strip(),
            "platform": row[2].strip(),
            "name": row[3].strip().replace("'", ""),
            "id": row[4].strip(),
            "tags": row[5].strip()
        }

        if title["id"] == "":

            platform_name = title["platform"]
            original_name = title["name"]

            result = GiantBombAPI.search_game(original_name, platform_name, 10)
            if result is not None:

                title["id"] = result["id"]
                title["name"] = result["name"].replace("'", "")

                if original_name.lower() == title["name"].lower():
                    searched_titles.append(title)
                else:
                    title["original_name"] = original_name
                    error_search.append(title)

                imported_search += 1
            else:

                failed_titles.append(title)
                failed += 1

        else:
            id_titles.append(title)
            imported_id += 1

        progress_recorder.set_progress(i + 1, total_titles)

    context = {
        "imported_id": imported_id,
        "imported_search": imported_search,
        "failed": failed,
        "id_titles": id_titles,
        "searched_titles": searched_titles,
        "error_search": error_search,
        "failed_titles": failed_titles
    }

    return context


@shared_task(bind=True)
def import_collection_task(self, titles, username):
    progress_recorder = ProgressRecorder(self)

    total_titles = len(titles)

    queue_titles = 0
    playing_titles = 0
    finished_titles = 0
    played_titles = 0
    abandoned_titles = 0

    failed_titles = 0

    for i in range(total_titles):
        title = titles[i]
        user = User.objects.get(username=username)

        if not Platform.objects.filter(name=title["platform"]).exists():
            Platform.objects.create(name=title["platform"])

        platform = Platform.objects.get(name=title["platform"])

        if not Game.objects.filter(db_id=title["id"]).exists():
            GameCollectionController.create_game(title["id"], platform)

        game = Game.objects.get(db_id=title["id"])

        if not GameVersion.objects.filter(parent_game=game, platform=platform).exists():
            GameCollectionController.create_gameversion(game=game, platform=platform)

        game_version = GameVersion.objects.get(parent_game=game, platform=platform)

        collection_entry = {
            "user": user,
            "game_version": game_version,
        }

        if title["date_adquired"] != "":
            collection_entry["date_adquired"] = title["date_adquired"]
        if title["time_played"] != "":
            collection_entry["time_played"] = title["time_played"]

        for tag_name in title["tags"].split(";"):
            if not Tag.objects.filter(name=tag_name, user=user).exists():
                Tag.objects.create(name=tag_name, user=user)

            tag = Tag.objects.get(name=tag_name, user=user)
            tag.game_version.add(game_version)
            tag.save()

        list_type = title["list"].upper()

        if list_type == "QUEUE":
            if not Queue.objects.filter(user=user, game_version=game_version).exists():
                Queue.objects.create(**collection_entry)
                queue_titles += 1

        elif list_type == "PLAYING":

            if title["date_started"] != "":
                collection_entry["date_started"] = title["date_started"]

            if not Playing.objects.filter(user=user, game_version=game_version).exists():
                Playing.objects.create(**collection_entry)
                playing_titles += 1

        elif list_type == "FINISHED":

            if title["date_started"] != "":
                collection_entry["date_started"] = title["date_started"]
            if title["second_date"] != "":
                collection_entry["date_finished"] = title["second_date"]
            if title["time_to_finish"] != "":
                collection_entry["time_to_finish"] = title["time_to_finish"]
            if title["playstyle"] != "":
                collection_entry["playstyle"] = title["playstyle"]

            if not Finished.objects.filter(user=user, game_version=game_version).exists():
                Finished.objects.create(**collection_entry)
                finished_titles += 1

        elif list_type == "PLAYED":

            if title["date_started"] != "":
                collection_entry["date_started"] = title["date_started"]
            if title["second_date"] != "":
                collection_entry["date_stopped"] = title["second_date"]

            if not Played.objects.filter(user=user, game_version=game_version).exists():
                Played.objects.create(**collection_entry)
                played_titles += 1

        elif list_type == "ABANDONED":

            if title["date_started"] != "":
                collection_entry["date_started"] = title["date_started"]
            if title["second_date"] != "":
                collection_entry["date_abandoned"] = title["second_date"]

            if not Abandoned.objects.filter(user=user, game_version=game_version).exists():
                Abandoned.objects.create(**collection_entry)
                abandoned_titles += 1
        else:
            failed_titles += 1

        progress_recorder.set_progress(i + 1, total_titles)

    context = {
        "total_titles": total_titles,
        "queue_titles": queue_titles,
        "playing_titles": playing_titles,
        "finished_titles": finished_titles,
        "played_titles": played_titles,
        "abandoned_titles": abandoned_titles,
        "failed_titles": failed_titles
    }

    return context


@shared_task(bind=True)
def import_list_task(self, titles, username):
    progress_recorder = ProgressRecorder(self)

    total_titles = len(titles)

    interested_titles = 0
    wishlist_titles = 0

    failed_titles = 0

    for i in range(total_titles):
        title = titles[i]
        user = User.objects.get(username=username)

        if not Platform.objects.filter(name=title["platform"]).exists():
            Platform.objects.create(name=title["platform"])

        platform = Platform.objects.get(name=title["platform"])

        if not Game.objects.filter(db_id=title["id"]).exists():
            GameCollectionController.create_game(title["id"], platform)

        game = Game.objects.get(db_id=title["id"])

        if not GameVersion.objects.filter(parent_game=game, platform=platform).exists():
            GameCollectionController.create_gameversion(game=game, platform=platform)

        game_version = GameVersion.objects.get(parent_game=game, platform=platform)

        list_entry = {
            "user": user,
            "game_version": game_version,
        }

        if title["date_added"] != "":
            list_entry["date_added"] = title["date_added"]

        for tag_name in title["tags"].split(";"):
            if not Tag.objects.filter(name=tag_name, user=user).exists():
                Tag.objects.create(name=tag_name, user=user)

            tag = Tag.objects.get(name=tag_name, user=user)
            tag.game_version.add(game_version)
            tag.save()

        list_type = title["list"].upper()

        if list_type == "INTERESTED":
            if not Interested.objects.filter(user=user, game_version=game_version).exists():
                Interested.objects.create(**list_entry)
                interested_titles += 1

        elif list_type == "WISHLIST":
            if not Wishlist.objects.filter(user=user, game_version=game_version).exists():
                Wishlist.objects.create(**list_entry)
                wishlist_titles += 1
        else:
            failed_titles += 1

        progress_recorder.set_progress(i + 1, total_titles)

    context = {
        "total_titles": total_titles,
        "interested_titles": interested_titles,
        "wishlist_titles": wishlist_titles,
        "failed_titles": failed_titles
    }

    return context
