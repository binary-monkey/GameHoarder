from datetime import datetime
from enum import Enum

import requests
import unidecode
from howlongtobeatpy import HowLongToBeat

from GameHoarder.settings import API_KEY
from game_database.models import Genre, Game, GameVersion

BASE_URL = "https://www.giantbomb.com/api/"

HEADERS = {
    'User-Agent': 'GameCollection 1.0',
    'From': 'jailander@protonmail.com'  # This is another valid field
}


class ResourceType(Enum):
    GAME = "game"
    RELEASE = "release"


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
    def search_game(game_title, platform_name, limit):
        data = GiantBombAPI.search(game_title, "game", limit)

        for result in data:

            platforms = result["platforms"]
            if platforms is not None:
                for platform_data in platforms:
                    if platform_data["name"] == platform_name:
                        return result

        return None

    @staticmethod
    def search_releases(game_id, platform, limit):

        filter_field = "game:%s&filter=platform:%s" % (game_id, platform)

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
    def create_game(db_id, platform):
        game = Game.objects.create(db_id=db_id)

        GameCollectionController.update_game(game)
        HowLongToBeatAPI.update_game_hltb(game)

        game_version = GameCollectionController.create_gameversion(game, platform)

        return game_version

    @staticmethod
    def create_gameversion(game, platform):
        results = GiantBombAPI.search_releases(game.db_id, platform, 1)

        if len(results) > 0:
            version_data = results[0]
            game_version = GameVersion.objects.create(parent_game=game, platform=platform, db_id=version_data["id"])
            GameCollectionController.update_game_version(game_version, version_data)

            return game_version
        else:
            # In some weird cases a game does not have a game version in it
            return GameVersion.objects.create(parent_game=game, platform=platform)

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
                genre_name = genre["name"]

                if Genre.objects.filter(name=genre_name).exists():
                    game.genres.add(Genre.objects.get(name=genre_name))
                else:
                    game.genres.add(Genre.objects.create(name=genre_name))

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

        if "release_date" in data:
            string_date = data["release_date"]
            if string_date is not None:
                game_version.release_date = datetime.strptime(string_date, '%Y-%m-%d %H:%M:%S')

        game_version.update = False
        game_version.save()
