# Create your tests here.

from django.test import TestCase

from game_database.functions import GameCollectionController, HowLongToBeatAPI
from game_database.models import Platform


class HLTBTest(TestCase):

    def setUp(self):

        pc = Platform.objects.create(name="PC")

        self.game = GameCollectionController.create_game(1539, pc).parent_game

        # Removing times for update test
        self.game.main_time = 0
        self.game.extra_time = 0
        self.game.completion_time = 0

    def test_load_times(self):

        times = HowLongToBeatAPI.load_times(self.game)

        self.assertTrue(isinstance(times.gameplay_main, str))
        self.assertTrue(isinstance(times.gameplay_main_extra, str))
        self.assertTrue(isinstance(times.gameplay_completionist, str))

    def test_update_times(self):
        times = HowLongToBeatAPI.load_times(self.game)

        if str(times.gameplay_main) != "-1":
            main_time = times.gameplay_main.replace("½", ".5")
        else:
            main_time = 0

        if str(times.gameplay_main_extra) != "-1":
            extra_time = times.gameplay_main_extra.replace("½", ".5")
        else:
            extra_time = 0

        if str(times.gameplay_completionist) != "-1":
            completion_time = times.gameplay_completionist.replace("½", ".5")
        else:
            completion_time = 0

        HowLongToBeatAPI.update_game_hltb(self.game)

        self.assertEquals(self.game.main_time, float(main_time))
        self.assertEquals(self.game.extra_time, float(extra_time))
        self.assertEquals(self.game.completion_time, float(completion_time))
