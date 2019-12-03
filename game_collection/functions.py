from datetime import datetime

from game_collection.models import Played, Playing, Finished, Abandoned, Interested, Wishlist, Queue
from game_database.functions import GiantBombAPI, ResourceType, HowLongToBeatAPI
from game_database.models import Company, GameVersion, Platform, Game, Genre


class GameCollectionController:

    @staticmethod
    def where_is(game_version, user):
        if Played.objects.filter(game_version=game_version, user=user).exists():
            return ["PLAYED", Played.objects.get(game_version=game_version, user=user)]
        elif Playing.objects.filter(game_version=game_version, user=user).exists():
            return ["PLAYING", Playing.objects.get(game_version=game_version, user=user)]
        elif Finished.objects.filter(game_version=game_version, user=user).exists():
            return ["FINISHED", Finished.objects.get(game_version=game_version, user=user)]
        elif Abandoned.objects.filter(game_version=game_version, user=user).exists():
            return ["ABANDONED", Abandoned.objects.get(game_version=game_version, user=user)]
        elif Queue.objects.filter(game_version=game_version, user=user).exists():
            return ["QUEUE", Queue.objects.get(game_version=game_version, user=user)]
        elif Wishlist.objects.filter(game_version=game_version, user=user).exists():
            return ["WISHLIST", Wishlist.objects.get(game_version=game_version, user=user)]
        elif Interested.objects.filter(game_version=game_version, user=user).exists():
            return ["INTERESTED", Interested.objects.get(game_version=game_version, user=user)]

        return None

    @staticmethod
    def create_platform(db_id):
        platform = Platform.objects.create(db_id=db_id)

        GameCollectionController.update_platform(platform)

        return platform

    @staticmethod
    def create_game(db_id, platform):
        game = Game.objects.create(db_id=db_id)

        GameCollectionController.update_game(game)
        HowLongToBeatAPI.update_game_hltb(game)

        game_version = GameCollectionController.create_gameversion(game, platform)

        return game_version

    @staticmethod
    def create_gameversion(game, platform):
        results = GiantBombAPI.search_releases(game.db_id, platform.db_id, 1)

        if len(results) > 0:
            version_data = results[0]
            game_version = GameVersion.objects.create(parent_game=game, platform=platform, db_id=version_data["id"])
            GameCollectionController.update_game_version(game_version, version_data)

            return game_version
        else:
            # In some weird cases a game does not have a game version in it
            return GameVersion.objects.create(parent_game=game, platform=platform)

    @staticmethod
    def update_platform(platform):
        data = GiantBombAPI.load(platform.db_id, ResourceType.PLATFORM)

        if "name" in data:
            platform.name = data["name"]

        if "deck" in data:
            platform.description = data["deck"]

        if "image" in data:
            if "original_url" in data["image"]:
                platform.img_url = data["image"]["original_url"]

        platform.update = False
        platform.save()

    @staticmethod
    def update_game(game):

        data = GiantBombAPI.load(game.db_id, ResourceType.GAME)

        if "name" in data:
            game.title = data["name"]

        if "original_release_date" in data:
            string_date = data["original_release_date"]
            if string_date is not None:
                game.release_date = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')

        if "genres" in data:
            game.genres.clear()

            for genre in data["genres"]:
                genre_id = genre["id"]

                if Genre.objects.filter(db_id=genre_id).exists():
                    game.genres.add(Genre.objects.get(db_id=genre_id))
                else:
                    game.genres.add(Genre.objects.create(db_id=genre_id, name=genre["name"]))

        if "deck" in data:
            game.description = data["deck"]

        if "image" in data:
            if "original_url" in data["image"]:
                game.img_url = data["image"]["original_url"]

        if "publishers" in data:
            game.publishers.clear()

            if data["publishers"] is not None:
                for company in data["publishers"]:
                    company_id = company["id"]

                    if Company.objects.filter(db_id=company_id).exists():
                        game.publishers.add(Company.objects.get(db_id=company_id))
                    else:
                        game.publishers.add(Company.objects.create(db_id=company_id, name=company["name"]))

        if "developers" in data:
            game.developers.clear()

            if data["developers"] is not None:
                for company in data["developers"]:
                    company_id = company["id"]

                    if Company.objects.filter(db_id=company_id).exists():
                        game.developers.add(Company.objects.get(db_id=company_id))
                    else:
                        game.developers.add(Company.objects.create(db_id=company_id, name=company["name"]))

        game.update = False
        game.save()

    @staticmethod
    def update_game_version(game_version, data=None):

        if data is None:
            results = GiantBombAPI.search_releases(game_version.parent_game.db_id, game_version.platform, 1)

            if len(results) > 0:
                data = results[0]

            else:
                data = None

        if "name" in data:
            game_version.name = data["name"]

        if "release_date" in data:
            string_date = data["release_date"]
            if string_date is not None:
                game_version.release_date = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')

        if "publishers" in data:
            game_version.publishers.clear()

            if data["publishers"] is not None:
                for company in data["publishers"]:
                    company_id = company["id"]

                    if Company.objects.filter(db_id=company_id).exists():
                        game_version.publishers.add(Company.objects.get(db_id=company_id))
                    else:
                        game_version.publishers.add(Company.objects.create(db_id=company_id, name=company["name"]))

        if "developers" in data:
            game_version.developers.clear()

            if data["developers"] is not None:
                for company in data["developers"]:
                    company_id = company["id"]

                    if Company.objects.filter(db_id=company_id).exists():
                        game_version.developers.add(Company.objects.get(db_id=company_id))
                    else:
                        game_version.developers.add(Company.objects.create(db_id=company_id, name=company["name"]))

        game_version.update = False
        game_version.save()
