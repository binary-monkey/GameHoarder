from datetime import datetime
from enum import Enum

import requests
import unidecode
from howlongtobeatpy import HowLongToBeat

from GameHoarder.settings import API_KEY, DEV_MAIL
from game_database.models import Genre, Game, GameVersion, Platform, Company

BASE_URL = "https://www.giantbomb.com/api/"

HEADERS = {
    'User-Agent': 'GameCollection 1.0',
    'From': DEV_MAIL
}


class ResourceType(Enum):
    GAME = "game"
    RELEASE = "release"
    PLATFORM = "platform"


class GiantBombAPI:

    @staticmethod
    def load_json(resource_url, params):
        request_url = BASE_URL + resource_url

        r = requests.get(url=request_url, headers=HEADERS, params=params)
        # print(r.url)
        return r.json()

    @staticmethod
    def search(query, resource, limit):
        params = {
            "api_key": API_KEY,
            "format": "json",
            "query": query,
            "resources": resource,
            "limit": limit,
            "field_list": "platforms,id,name"
        }

        return GiantBombAPI.load_json("search", params)["results"]

    @staticmethod
    def search_platform(platform_name):

        filter_field = "filter=name:%s" % platform_name

        params = {
            "api_key": API_KEY,
            "format": "json",
            "filter": filter_field,
        }

        data = GiantBombAPI.load_json("platforms", params)["results"]

        for result in data:
            if result["name"] == platform_name:
                return result

        return None

    @staticmethod
    def search_game(game_title, limit, platform_id=None):
        data = GiantBombAPI.search(game_title, "game", limit)

        if platform_id is not None:
            for result in data:
                platforms = result["platforms"]
                if platforms is not None:
                    for platform_data in platforms:
                        if platform_data["id"] == platform_id:
                            return result
        else:
            return data

        return None

    @staticmethod
    def search_releases(game_id, platform_id, limit):

        filter_field = "game:%s&filter=platform:%s" % (game_id, platform_id)

        params = {
            "api_key": API_KEY,
            "format": "json",
            "limit": limit,
            "filter": filter_field,
        }

        return GiantBombAPI.load_json("releases", params)["results"]

    @staticmethod
    def load(resource_id, resource):

        if resource == ResourceType.GAME:
            resource_url = "game/3030-%s" % resource_id
            params = {
                "api_key": API_KEY,
                "format": "json",
            }

        elif resource == ResourceType.RELEASE:
            resource_url = "release/3050-%s" % resource_id
            params = {
                "api_key": API_KEY,
                "format": "json",
            }

        elif resource == ResourceType.PLATFORM:
            resource_url = "platform/3045-%s" % resource_id
            params = {
                "api_key": API_KEY,
                "format": "json",
            }

        else:
            return None

        return GiantBombAPI.load_json(resource_url, params)["results"]


class HowLongToBeatAPI:
    @staticmethod
    def load_times(game):
        # This will remove accents
        stripped_title = unidecode.unidecode(game.title)

        results = HowLongToBeat().search(stripped_title)

        max_sim = -1
        best_element = None
        for element in results:
            if element.similarity > max_sim:
                max_sim = element.similarity
                best_element = element

        # print("Pulled times for %s: [ %s, %s, %s]" % (
        #     game.title, best_element.gameplay_main, best_element.gameplay_main_extra,
        #     best_element.gameplay_completionist))

        return best_element

    @staticmethod
    def update_game_hltb(game):

        times = HowLongToBeatAPI.load_times(game)

        if times is not None:
            if str(times.gameplay_main) != "-1":
                game.main_time = float(times.gameplay_main.replace("½", ".5"))

            if str(times.gameplay_main_extra) != "-1":
                game.extra_time = float(times.gameplay_main_extra.replace("½", ".5"))

            if str(times.gameplay_completionist) != "-1":
                game.completion_time = float(times.gameplay_completionist.replace("½", ".5"))

            game.save()
            return True

        return False


class GameCollectionController:

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
