import unittest
from mock import Mock, MagicMock, patch
from PyQt5 import QtCore
from lib.Допфункции import *


class TestДополнительныхФункций(unittest.TestCase):

    def testпериодВДниЧасыМинутыСекунды(self):
        отрезок = период(days=3, hours=29, minutes=145, seconds=8)
        self.assertEqual((4, 7, 25, 8), периодВДниЧасыМинутыСекунды(отрезок))

    def testпериодВСтроку(self):
        отрезок = период(days=3, hours=29, minutes=125, seconds=8)
        self.assertEqual("4д:07ч:05м", периодВСтроку(отрезок))

        отрезок = период(days=4, hours=13, minutes=45, seconds=8)
        self.assertEqual("4д:13ч:45м", периодВСтроку(отрезок))

        отрезок = период(days=0, hours=9, minutes=35, seconds=38)
        self.assertEqual("09:35", периодВСтроку(отрезок))

    def testпериодВСтрокуиСекунды(self):
        отрезок = период(0)
        self.assertEqual("--", периодВСтрокуиСекунды(отрезок))

        отрезок = период(minutes=25, seconds=8)
        self.assertEqual("25:08", периодВСтрокуиСекунды(отрезок))

        отрезок = период(days=4, hours=9, minutes=25, seconds=8)
        self.assertEqual("4д:09:25:08", периодВСтрокуиСекунды(отрезок))

        отрезок = период(days=0, hours=9, minutes=25, seconds=8)
        self.assertEqual("09:25:08", периодВСтрокуиСекунды(отрезок))

class TestПериодическогоПроцесса(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testВсёЛиЕстьДляСозданияРеальногоТаймераИЕгоРаботы(self):
        обработчик = Mock()
        точность = QtCore.Qt.PreciseTimer

        self.периодПроцесс = ПериодическийПроцесс(1, точность, обработчик)
        self.assertIsInstance(self.периодПроцесс.таймер, QBasicTimer)
        self.assertIsInstance(self.периодПроцесс.объект, QObject)
        self.assertEqual(self.периодПроцесс.timerEvent, self.периодПроцесс.объект.timerEvent)
        self.периодПроцесс.таймер = Mock()

        self.периодПроцесс.старт()
        self.периодПроцесс.таймер.start.assert_called_with(1000, точность, self.периодПроцесс.объект)

        self.периодПроцесс.timerEvent(None)
        обработчик.assert_called_with()

        self.периодПроцесс.стоп()
        self.периодПроцесс.таймер.stop.assert_called_with()


class TestВызовСЗадержкой(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch('lib.Допфункции.QBasicTimer')
    def testВсёЛиЕстьДляСозданияРеальногоТаймераИЕгоРаботы(self, mock_qtimer):
        обработчик = Mock()
        точность = QtCore.Qt.PreciseTimer

        self.вызов = ВызовСЗадержкой(1, точность, обработчик)
        self.assertIsInstance(self.вызов.таймер, MagicMock)
        self.assertIsInstance(self.вызов.объект, QObject)
        self.assertEqual(self.вызов.timerEvent, self.вызов.объект.timerEvent)

        self.вызов.timerEvent(None)
        обработчик.assert_called_with()
        self.assertEqual(1, self.вызов.таймер.stop.call_count)

        self.вызов.стоп()
        self.assertEqual(2, self.вызов.таймер.stop.call_count)

