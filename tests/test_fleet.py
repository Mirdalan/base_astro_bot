import unittest
import os

from .set_path import *
from base_astro_bot.database import DatabaseManager
from tests.artifacts import TEST_SHIPS


class MockUserObject:
    def __init__(self, name):
        self.id = "%s#123" % name
        self.username = name


class FleetManagerTests(unittest.TestCase):
    def setUp(self):
        self.db_name = 'test_db'
        self.mgr = DatabaseManager(self.db_name, log_file=None)

    def test_creates_and_reads_members(self):
        self.mgr.add_and_get_member(MockUserObject("jeden"))
        self.mgr.add_and_get_member(MockUserObject("dwa"))
        self.mgr.add_and_get_member(MockUserObject("trzy"))
        members = self.mgr.get_all_members()
        self.assertEqual(len(members), 3)

    def test_cannot_create_duplicate_members(self):
        self.mgr.add_and_get_member(MockUserObject("jeden"))
        self.mgr.add_and_get_member(MockUserObject("dwa"))
        self.mgr.add_and_get_member(MockUserObject("trzy"))
        self.mgr.add_and_get_member(MockUserObject("jeden"))
        self.mgr.add_and_get_member(MockUserObject("dwa"))
        self.mgr.add_and_get_member(MockUserObject("trzy"))
        members = self.mgr.get_all_members()
        self.assertEqual(len(members), 3)

    def test_update_ships(self):
        self.mgr.update_member_ships(TEST_SHIPS, MockUserObject("mird"))
        ships = self.mgr.get_all_ships()
        self.assertEqual(len(TEST_SHIPS), len(ships))

    def test_update_overwrites_ships(self):
        self.mgr.update_member_ships(TEST_SHIPS, MockUserObject("mird"))
        ships = self.mgr.get_all_ships()
        self.assertEqual(len(TEST_SHIPS), len(ships))
        self.mgr.update_member_ships(TEST_SHIPS[1:], MockUserObject("mird"))
        ships = self.mgr.get_all_ships()
        self.assertEqual(len(TEST_SHIPS[1:]), len(ships))

    def tearDown(self):
        self.mgr.sql_alchemy_session.close()
        os.remove(self.db_name)
