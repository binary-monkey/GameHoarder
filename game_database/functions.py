from datetime import datetime
from enum import Enum

import requests
import unidecode
from howlongtobeatpy import HowLongToBeat

from GameHoarder.settings import API_KEY, DEV_MAIL
from game_collection.models import Interested, Wishlist, Queue, Abandoned, Finished, Playing, Played
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

class GameHoarderDB:

    @staticmethod
    def _local_search(params):
        search_params = {
            # # key: REST param, value: model query
            'developer': 'parent_game__developers__name__contains',
            'genres': 'parent_game__genres__name__in',
            'platform': 'platform__name__iendswith',
            'publisher': 'parent_game__publishers__name__contains',
            'year': 'parent_game__release_date__year',
            'title': 'parent_game__title__contains',
        }
        # GameVersion.objects.filter(=)

        query = {}
        for k, v in search_params.items():
            # param is present and not empty
            if k in params.keys() and params.get(k):
                query[v] = params.get(k)
        local_games = GameVersion.objects.filter(**query)
        return local_games

    @staticmethod
    def search(params, use_api=False):
        # para evitar repetir versiones presentes en la DB local y remota,
        # utilizaremos el nombre_padre+nombre como identificador único
        #
        # podría realizarse con sets y no dicts, pero corremos el riesgo
        # de que un cambio en campos como el resumen del juego o el tiempo
        # de juego cree duplicados
        local_games = GameHoarderDB._local_search(params)
        local_games_dict = {
            f'{x.parent_game.title}{x.name}': x for x in local_games
        }
        # TODO: extender búsqueda externa a más campos que 'title'
        remote_games_dict = {}
        if use_api and params.get('title'):
            remote_games = GiantBombAPI.search_game(game_title=params.get('title'), limit=5)
            for game in remote_games:
                for platform in game.get("platforms"):
                    platforms = Platform.objects.filter(db_id=platform.get('id'))
                    # evitar repetir búsquedas
                    if len(platforms) == 0:
                        p = GameCollectionController.create_platform(platform.get('id'))
                        p.save()
                        games = Game.objects.filter(db_id=game.get('id'))
                        # evitar repetir búsquedas
                        if len(games) == 0:
                            g = GameCollectionController.create_game(game.get('id'), p)
                            g.save()
                            remote_games_dict[f'{g.parent_game.title}{g.name}'] = g
        # unir diccionarios, dando preferencia a elementos de la DB local
        return {**remote_games_dict, **local_games_dict}.values()

    @staticmethod
    def table_filter(params):
        search_params = {
            # # key: REST param, value: model query
            'developer': 'parent_game__developers__name__contains',
            'genres': 'parent_game__genres__name__in',  # TODO: correct filter for genres
            'platform': 'platform__name__iendswith',
            'publisher': 'parent_game__publishers__name__contains',
            'year': 'parent_game__release_date__year',
            'title': 'parent_game__title__contains',
        }
        # GameVersion.objects.filter(=)

        query = {}
        for k, v in search_params.items():
            # param is present and not empty
            if k in params.keys() and params.get(k):
                query[v] = params.get(k)
        local_games = GameVersion.objects.filter(**query)
        local_games_dict = {
            f'{x.parent_game.title}{x.name}': x for x in local_games
        }
        return {**local_games_dict}.values()

    @staticmethod
    def params_empty(params):
        for _, v in params.items():
            if v:
                return False
        return True
