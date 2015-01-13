import unittest
import tempfile
from mock import patch

from lib.Сохранение import *

class TestХранилища(unittest.TestCase):

    def setUp(self):
        self.дерево = {'test': 'data1', 'test2': 'data2', 'somelist': [3, 4, {"д":5, "с": 500} ] }
        self.дерево2 = {'test': 'data1', 'test2': 'data2', 'test3': 'data3'}
        x, self.файлДерева = tempfile.mkstemp(suffix='.расписание', prefix="тест-")
        self.колвоБекапов = 10
        os.remove(self.файлДерева)
        with patch('lib.Сохранение.os.makedirs') as mock_makedirs:
            self.хранилище = Хранилище(self.файлДерева, self.колвоБекапов)
            self.assertEqual('/tmp', mock_makedirs.call_args[0][0])

    def tearDown(self):
        try: os.remove(self.файлДерева)
        except: pass

    def testСохраненияДерева(self):
        self.хранилище.сохранить(self.дерево)
        f = open(self.файлДерева, "r")
        self.assertEqual(json.dumps(self.дерево, ensure_ascii=False, indent="  "), f.read())

    def testЗагрузкиДерева(self):
        f = open(self.файлДерева, "w")
        f.write(json.dumps(self.дерево, ensure_ascii=False, indent="  "))
        f.close()
        self.assertDictEqual(self.дерево, self.хранилище.загрузить())

    def testЗагрузкиДерева_КогдаНетФайла_ВозвращаетПустоеДерево(self):
        self.assertDictEqual({}, self.хранилище.загрузить())

    def testБекапов(self):
        self.хранилище.сохранить(self.дерево2)
        self.хранилище.сохранить(self.дерево)

        хранилище2 = Хранилище("%s.1" % self.файлДерева, self.колвоБекапов)
        self.assertDictEqual(self.дерево2, хранилище2.загрузить())
        os.remove("%s.1" % self.файлДерева)
