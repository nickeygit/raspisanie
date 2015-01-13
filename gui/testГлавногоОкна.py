import os
import unittest
import tempfile
import time
from mock import Mock, patch
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QInputDialog

from gui import ГлавноеОкно as ОМ
from lib.Допфункции import *

class TestГлавногоОкна(unittest.TestCase):

    настройки = {
        "имяФайла": "расписание",
        "путьКдире": "/tmp/",
        "дираАрхива": "/tmp/архив/",
        "ширина": 1000,
        "высота": 700
    }

    def setUp(self):
        self.app = QApplication(['',])
        with patch.object(ОМ.ГлавноеОкно, 'загрузитьРасписание'):
            x, ОМ.путьКфайлу = tempfile.mkstemp(suffix='.расписание', prefix="тест-")
            self.файлДерева = ОМ.путьКфайлу
            try: os.remove(self.файлДерева)
            except: pass
            self.окно = ОМ.ГлавноеОкно(self.настройки)

    def tearDown(self):
        try: os.remove(self.файлДерева)
        except: pass
        os.system('rm -rf %s &>/dev/null' % self.окно.настройки['дираАрхива'])

    def testСозданияРасписанияИзДерева(self):

        def найтиЭлементПоИмени(имя):
            for элемент in всеэлементы:
                if элемент.задача.имя == имя:
                    return элемент

        def проверитьВыравниваниеЭлемента(элемент):
            выравнивание = int(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.assertEqual(выравнивание, элемент.textAlignment(ОМ.ГлавноеОкно.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО))
            self.assertEqual(выравнивание, элемент.textAlignment(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
            self.assertEqual(выравнивание, элемент.textAlignment(ОМ.ГлавноеОкно.СТОЛБИК_МАКСИМУМА))

        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1", "l": [
                        {'n': "Задача-1-1", "x": {"s": 3600*3}, "l": [
                            {'n': "Задача-1-1-1", ">": {"d": 2, "s": 3600*4}, "<": {"d": 1}, "ko": "что-то короткое",
                                "do": "что-то подлиннее"},
                            {'n': "Задача-1-1-2", "x": {"s": 3600*9}},
                            {'n': "Задача-1-1-3", ">": {"s": 3600*3}, "<": {"s": 3600*5}},
                            ]
                        },
                        ]
                    },
                ]
            }
        self.окно.загрузитьРасписаниеИзДерева(дерево)

        всеэлементы = self.окно.derevoZadach.findItems('.*', QtCore.Qt.MatchRegExp | QtCore.Qt.MatchRecursive)

        родитель = self.окно.derevoZadach.invisibleRootItem()
        self.assertEqual(родитель.задача.имя, "Корень")

        элемент = найтиЭлементПоИмени('Задача-1')
        self.assertEqual(None, элемент.parent())
        self.assert_(элемент.isExpanded())
        проверитьВыравниваниеЭлемента(элемент)
        self.assertEqual('Задача-1', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ИМЕНИ))
        self.assertEqual('--', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual('12:00:00', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО))

        родитель = элемент
        элемент = найтиЭлементПоИмени('Задача-1-1')
        self.assertEqual(родитель, элемент.parent())
        self.assert_(элемент.isExpanded())
        проверитьВыравниваниеЭлемента(элемент)
        self.assertEqual('Задача-1-1', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ИМЕНИ))
        self.assertEqual('03:00:00', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual('12:00:00', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО))

        родитель = элемент
        элемент = найтиЭлементПоИмени('Задача-1-1-1')
        self.assertEqual(родитель, элемент.parent())
        проверитьВыравниваниеЭлемента(элемент)
        self.assertEqual('Задача-1-1-1', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ИМЕНИ))
        self.assertEqual('--', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual('--', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО))
        self.assertEqual('2д:04ч:00м', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_МАКСИМУМА))
        self.assertEqual('1д:00ч:00м', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_МИНИМУМА))
        self.assertEqual("что-то подлиннее", элемент.задача.детальноеОписание)
        self.assertEqual("что-то короткое", элемент.задача.краткоеОписание)

        элемент = найтиЭлементПоИмени('Задача-1-1-2')
        self.assertEqual(родитель, элемент.parent())
        проверитьВыравниваниеЭлемента(элемент)
        self.assertEqual('Задача-1-1-2', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ИМЕНИ))
        self.assertEqual('09:00:00', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))

        элемент = найтиЭлементПоИмени('Задача-1-1-3')
        self.assertEqual(родитель, элемент.parent())
        проверитьВыравниваниеЭлемента(элемент)
        self.assertEqual('Задача-1-1-3', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ИМЕНИ))
        self.assertEqual('--', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual('--', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО))
        self.assertEqual('05:00', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_МАКСИМУМА))
        self.assertEqual('05:00', элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_МИНИМУМА))

    def testФункцииСохраненияРасписанияСразу(self):
        self.assertIsInstance(self.окно.хранилище, ОМ.Хранилище)

        self.окно.расписание.экспортДерева = Mock(return_value='это дерево')
        self.окно.хранилище.сохранить = Mock()

        self.окно.сохранитьРасписаниеСразу()

        self.assertEqual(1, self.окно.расписание.экспортДерева.call_count)
        self.assertEqual('это дерево', self.окно.хранилище.сохранить.call_args[0][0])

    def testФункцииСохраненияРасписанияСЗадержкой(self):
        self.assertIsInstance(self.окно.таймерОтложеннойЗаписи, ОМ.ВызовСЗадержкой)
        self.assertEqual(ОМ.таймаутЗаписиПослеИзменений, self.окно.таймерОтложеннойЗаписи.период)
        self.assertEqual(self.окно.сохранитьРасписаниеСразу, self.окно.таймерОтложеннойЗаписи.обработчик)

        self.окно.таймерОтложеннойЗаписи.старт = Mock()

        self.окно.сохранитьРасписание()

        self.assertEqual(1, self.окно.таймерОтложеннойЗаписи.старт.call_count)

    def testСохраненияРазВМинутуПриАктивнойЗадачеИПриОстановке(self):
        self.assertIsInstance(self.окно.счётчикАвтосохранения, ОМ.ПериодическийПроцесс)
        self.assertEqual(ОМ.периодАвтоСохранения, self.окно.счётчикАвтосохранения.период)
        self.assertEqual(self.окно.обработчикСчётчикаАвтосохранения, self.окно.счётчикАвтосохранения.обработчик)

        self.окно.счётчикАвтосохранения.старт = Mock()
        self.окно.счётчикАвтосохранения.стоп = Mock()

        # грузим одну задачу и запускаем её
        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1" },
                        ]
                    }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        self.окно.derevoZadach.setCurrentItem(self.окно.расписание.задачи[0].элемент)
        self.окно.запуститьЗадачу()

        # бегущаяЗадача должна быть установлена
        self.assertEqual(self.окно.расписание.задачи[0], self.окно.бегущаяЗадача)

        # таймер, вызывающий сохранение должен быть запущен
        self.assertEqual(1, self.окно.счётчикАвтосохранения.старт.call_count)

        # получатель событий таймера должен вызывать ф-цию сохранения
        self.окно.сохранитьРасписаниеСразу = Mock()
        self.окно.обработчикСчётчикаАвтосохранения()
        self.assertEqual(1, self.окно.сохранитьРасписаниеСразу.call_count)

        # при остановке задачи таймер тоже должен быть остановлен
        self.окно.остановитьЗадачу()
        self.assertEqual(1, self.окно.счётчикАвтосохранения.стоп.call_count)

        self.assertEqual(2, self.окно.сохранитьРасписаниеСразу.call_count)

        # бегущаяЗадача должна быть обнулена
        self.assertEqual(None, self.окно.бегущаяЗадача)

    def testСчётаВремениПриАктивнойЗадаче(self):
        self.assertIsInstance(self.окно.счётчикВремени, ОМ.ПериодическийПроцесс)
        self.assertEqual(ОМ.периодСчётчикаВремени, self.окно.счётчикВремени.период)
        self.assertEqual(self.окно.обработчикСчётчикаВремени, self.окно.счётчикВремени.обработчик)

        self.окно.счётчикВремени.старт = Mock()
        self.окно.счётчикВремени.стоп = Mock()

        # грузим одну задачу и запускаем её
        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1", "<": { "s": 1*60 } },
                        ]
                    }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        self.окно.derevoZadach.setCurrentItem(self.окно.расписание.задачи[0].элемент)
        self.окно.запуститьЗадачу()

        # таймер, вызывающий сохранение должен быть запущен
        self.assertEqual(1, self.окно.счётчикВремени.старт.call_count)

        # счётчик времени должен обновлять время в дереве
        self.окно.обновитьЗатраченноеВремяЗадачи = Mock()
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы = Mock()
        self.окно.обработчикСчётчикаВремени()
        self.assertEqual(1, self.окно.обновитьЗатраченноеВремяЗадачи.call_count)
        self.assertEqual(1, self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы.call_count)

        # при остановке задачи таймер тоже должен быть остановлен
        self.окно.расписание.экспортДерева = Mock(return_value='это дерево')
        self.окно.хранилище.сохранить = Mock()

        self.окно.остановитьЗадачу()
        self.assertEqual(1, self.окно.счётчикВремени.стоп.call_count)

    def testФлагаРазграниченияЧтенияЗаписиДерева(self):
        self.assertEqual(False, self.окно.деревоЗанято)

        self.окно.таймерОтложеннойЗаписи.старт = Mock()

        self.окно.сохранитьРасписание()
        self.assertEqual(1, self.окно.таймерОтложеннойЗаписи.старт.call_count)

        self.окно.деревоЗанято = True

        self.окно.сохранитьРасписание()
        self.assertEqual(1, self.окно.таймерОтложеннойЗаписи.старт.call_count)

        # загрузка устанавливает этот флаг
        self.окно.хранилище.загрузить = Mock()
        self.окно.расписание.загрузитьИзДерева = Mock()
        self.окно.деревоЗанято = None

        self.окно.загрузитьРасписаниеИзДерева({})

        self.assertEqual(False, self.окно.деревоЗанято)

    def testИзменениеСостоянияИЦветаФонаЗадачиСТечениемВремени(self):
        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1", "<": {"d": 1}, ">": {"d": 3} },
                    {'n': "Задача-2", "<": {"d": 1} },
                        ]
                    }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        элемент = self.окно.расписание.задачи[0].элемент
        задача = элемент.задача
        self.assertEqual(ОМ.СостояниеЗадачи.нужноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нужноДелать].name(), элемент.background(0).color().name())

        задача.затратитьВремя(период(2))
        self.окно.обновитьЗатраченноеВремяЗадачи(задача, элемент)
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы(элемент)
        self.assertEqual(ОМ.СостояниеЗадачи.можноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.можноДелать].name(), элемент.background(0).color().name())

        задача.затратитьВремя(период(2))
        self.окно.обновитьЗатраченноеВремяЗадачи(задача, элемент)
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы(элемент)
        self.assertEqual(ОМ.СостояниеЗадачи.нельзяДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нельзяДелать].name(), элемент.background(0).color().name())

    def testИзменениеТекущегоИПредыдущегоСостоянияИЦветаФонаЗадачиСУведомлениемПриИзмененииОграничений(self):
        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1", "<": {"s": 1*60}, "x": {"s": 3*60}, ">": {"s": 5*60} },
                    {'n': "Задача-2", "<": {"d": 1} },
                        ]
                    }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        элемент = self.окно.расписание.задачи[0].элемент
        self.окно.derevoZadach.setCurrentItem(элемент)

        задача = элемент.задача
        print(задача)
        print(элемент)
        self.assertEqual(ОМ.СостояниеЗадачи.можноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.можноДелать].name(), элемент.background(0).color().name())

        self.окно.системныйЗначок.showMessage = Mock()

        self.окно.minimumFlag.setChecked(True)

        self.окно.minimumPeriod.setTime(QTime(0, 4))
        self.assertEqual(ОМ.СостояниеЗадачи.нужноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нужноДелать].name(), элемент.background(0).color().name())
        self.assertEqual(1, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.нужноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])

        self.окно.minimumPeriod.setTime(QTime(0, 1))
        self.assertEqual(ОМ.СостояниеЗадачи.можноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.можноДелать].name(), элемент.background(0).color().name())
        self.assertEqual(2, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.можноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])


        self.окно.maximumFlag.setChecked(True)

        self.окно.maximumPeriod.setTime(QTime(0, 2))
        self.assertEqual(ОМ.СостояниеЗадачи.нельзяДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нельзяДелать].name(), элемент.background(0).color().name())
        self.assertEqual(3, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.нельзяДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])

        self.окно.maximumPeriod.setTime(QTime(0, 5))
        self.assertEqual(ОМ.СостояниеЗадачи.можноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.можноДелать].name(), элемент.background(0).color().name())
        self.assertEqual(4, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.можноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])

    def testСистемногоЗначкаИУведомленийОСменеСтатусаАктивнойЗадачи(self):
        self.assertIsInstance(self.окно.системныйЗначок, QSystemTrayIcon)
        self.assertEqual(True, self.окно.системныйЗначок.isVisible())

        дерево = {'n': "Корень", "l": [ {'n': "Задача-1", "<": {"s": 1 }, ">": {"s": 3} }, {'n': "Задача-2", "<": {"s": 1 } }] }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        self.окно.derevoZadach.setCurrentItem(self.окно.расписание.задачи[0].элемент)
        задача = self.окно.расписание.задачи[0]
        self.окно.бегущаяЗадача = задача

        self.assertEqual(ОМ.СостояниеЗадачи.нужноДелать, задача.предыдущееСостояние)

        self.окно.обновитьЗатраченноеВремяЗадачи = Mock()
        self.окно.системныйЗначок.showMessage = Mock()
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы = Mock()

        self.окно.обработчикСчётчикаВремени()
        self.assertEqual(1, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.можноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])

        self.окно.обработчикСчётчикаВремени()
        self.assertEqual(1, self.окно.системныйЗначок.showMessage.call_count)

        self.окно.обработчикСчётчикаВремени()
        self.assertEqual(2, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.нельзяДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])

    def testУведомленийОПереключенияхЦикла(self):
        дерево = {'n': "Корень", "l": [ {'n': "Задача-1", "<": {"s": 2 }, }, ] }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        self.окно.derevoZadach.setCurrentItem(self.окно.расписание.задачи[0].элемент)
        задача = self.окно.расписание.задачи[0]
        self.окно.бегущаяЗадача = задача

        self.окно.обновитьЗатраченноеВремяЗадачи = Mock()
        self.окно.системныйЗначок.showMessage = Mock()
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы = Mock()

        self.окно.обработчикСчётчикаВремени()
        self.assertEqual(0, self.окно.системныйЗначок.showMessage.call_count)

        self.окно.обработчикСчётчикаВремени()
        self.assertEqual(1, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual("Цикл завершён", self.окно.системныйЗначок.showMessage.call_args[0][0])

    def testМенюИзмененияВремениМеняетЗатраченноеВремяСостояниеИЦветФонаЗадачиИСохраняет(self):
        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1", "<": {"s": 5*60}, ">": {"s": 15*60} },
                    {'n': "Задача-2", "<": {"d": 1} },
                        ]
                    }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        элемент = self.окно.расписание.задачи[0].элемент
        self.окно.derevoZadach.setCurrentItem(элемент)
        задача = элемент.задача

        self.окно.системныйЗначок.showMessage = Mock()
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы = Mock()
        self.окно.сохранитьРасписание = Mock()

        self.assertEqual(период(0), задача.своёЗатраченноеВремя)
        self.assertEqual('--', элемент.text(self.окно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual(ОМ.СостояниеЗадачи.нужноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нужноДелать].name(), элемент.background(0).color().name())

        with patch.object(ОМ.QInputDialog, 'getInt', Mock(return_value=(6, True))) as mock_getInt:
            self.окно.действиеИзменитьЗатраченноеВремяЗадачи.trigger()
            self.assertEqual(1, mock_getInt.call_count)
        self.assertEqual(период(seconds=6*60), задача.своёЗатраченноеВремя)
        self.assertEqual('06:00', элемент.text(self.окно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual(ОМ.СостояниеЗадачи.можноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.можноДелать].name(), элемент.background(0).color().name())
        self.assertEqual(1, self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы.call_count)
        self.assertEqual(1, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.можноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])
        self.assertEqual(1, self.окно.сохранитьРасписание.call_count)

        with patch.object(ОМ.QInputDialog, 'getInt', Mock(return_value=(10, True))) as mock_getInt:
            self.окно.действиеИзменитьЗатраченноеВремяЗадачи.trigger()
            self.assertEqual(1, mock_getInt.call_count)
        self.assertEqual(период(seconds=16*60), задача.своёЗатраченноеВремя)
        self.assertEqual('16:00', элемент.text(self.окно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual(ОМ.СостояниеЗадачи.нельзяДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нельзяДелать].name(), элемент.background(0).color().name())
        self.assertEqual(2, self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы.call_count)
        self.assertEqual(2, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.нельзяДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])
        self.assertEqual(2, self.окно.сохранитьРасписание.call_count)

        with patch.object(ОМ.QInputDialog, 'getInt', Mock(return_value=(-9, True))) as mock_getInt:
            self.окно.действиеИзменитьЗатраченноеВремяЗадачи.trigger()
            self.assertEqual(1, mock_getInt.call_count)
        self.assertEqual(период(seconds=7*60), задача.своёЗатраченноеВремя)
        self.assertEqual('07:00', элемент.text(self.окно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual(ОМ.СостояниеЗадачи.можноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.можноДелать].name(), элемент.background(0).color().name())
        self.assertEqual(3, self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы.call_count)
        self.assertEqual(3, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.можноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])
        self.assertEqual(3, self.окно.сохранитьРасписание.call_count)

        with patch.object(ОМ.QInputDialog, 'getInt', Mock(return_value=(-4, True))) as mock_getInt:
            self.окно.действиеИзменитьЗатраченноеВремяЗадачи.trigger()
            self.assertEqual(1, mock_getInt.call_count)
        self.assertEqual(период(seconds=3*60), задача.своёЗатраченноеВремя)
        self.assertEqual('03:00', элемент.text(self.окно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
        self.assertEqual(ОМ.СостояниеЗадачи.нужноДелать, задача.состояние())
        self.assertEqual(ОМ.цветЗадачи[ОМ.СостояниеЗадачи.нужноДелать].name(), элемент.background(0).color().name())
        self.assertEqual(4, self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы.call_count)
        self.assertEqual(4, self.окно.системныйЗначок.showMessage.call_count)
        self.assertEqual(ОМ.текстСостояния[ОМ.СостояниеЗадачи.нужноДелать], self.окно.системныйЗначок.showMessage.call_args[0][0])
        self.assertEqual(4, self.окно.сохранитьРасписание.call_count)

    def testАктивностьЗадачиОтражаетсяВСистемномЗначкеАНазваниеВПодсказкеИВЗаголовкеОкна(self):
        self.assertIsInstance(self.окно.иконкаАктивности[True], QIcon)
        self.assertIsInstance(self.окно.иконкаАктивности[False], QIcon)

        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1" },
                        ]
                    }
        self.окно.загрузитьРасписаниеИзДерева(дерево)
        self.окно.derevoZadach.setCurrentItem(self.окно.расписание.задачи[0].элемент)

        self.assertTrue(self.окно.системныйЗначок.isVisible())
        self.assertEqual('--', self.окно.системныйЗначок.toolTip())
        self.assertEqual(ОМ.названиеОкна, self.окно.windowTitle())

        self.окно.счётчикАвтосохранения = Mock()
        self.окно.счётчикВремени = Mock()
        self.окно.системныйЗначок = Mock()

        self.окно.запуститьЗадачу()
        self.assertEqual(self.окно.иконкаАктивности[True], self.окно.системныйЗначок.setIcon.call_args[0][0])
        self.assertEqual('Задача-1', self.окно.системныйЗначок.setToolTip.call_args[0][0])
        self.assertEqual('Задача-1 :: %s' % ОМ.названиеОкна, self.окно.windowTitle())

        self.окно.остановитьЗадачу()
        self.assertEqual(self.окно.иконкаАктивности[False], self.окно.системныйЗначок.setIcon.call_args[0][0])
        self.assertEqual('--', self.окно.системныйЗначок.setToolTip.call_args[0][0])
        self.assertEqual(ОМ.названиеОкна, self.окно.windowTitle())

    def testОбновленияЭлементовПриПереключенииЦикла(self):

        def найтиЭлементПоИмени(имя):
            for элемент in всеэлементы:
                if элемент.задача.имя == имя:
                    return элемент

        def проверитьЭлемент(элемент):
            self.assertEqual(периодВСтрокуиСекунды(элемент.задача.своёЗатраченноеВремя),
                             элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО))
            self.assertEqual(периодВСтрокуиСекунды(элемент.задача.затраченноеВремя()),
                             элемент.text(ОМ.ГлавноеОкно.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО))
            self.assertEqual(ОМ.цветЗадачи[элемент.задача.состояние()].name(), элемент.background(0).color().name())


        дерево = {'n': "Корень", "l": [
                    {'n': "Задача-1", "l": [
                        {'n': "Задача-1-1", "l": [
                            {'n': "Задача-1-1-1", "<": {"s": 4*60}, "x": {"s": 7*60}, ">": {"s": 9*60}},
                            {'n': "Задача-1-1-2",                   "x": {"s": 5*60}},
                            {'n': "Задача-1-1-3", "<": {"s": 3*60}, "x": {"s": 9*60}, ">": {"s": 6*60}},
                            ]
                        },
                        ]
                    },
                    {'n': "Задача-2", "l": [
                        {'n': "Задача-2-1", "l": [
                            {'n': "Задача-2-1-1", "<": {"s": 1*60}, "x": {"s": 3*60}, ">": {"s": 2*60}},
                            {'n': "Задача-2-1-2",                   "x": {"s": 7*60}, ">": {"s": 4*60}},
                            {'n': "Задача-2-1-3", "<": {"s": 4*60}, "x": {"s": 4*60-1}},
                            ]
                        },
                        ]
                    },
                ]
            }
        self.окно.загрузитьРасписаниеИзДерева(дерево)

        всеэлементы = self.окно.derevoZadach.findItems('.*', QtCore.Qt.MatchRegExp | QtCore.Qt.MatchRecursive)

        проверитьЭлемент(найтиЭлементПоИмени('Задача-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1-2'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1-3'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1-2'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1-3'))

        элемент = найтиЭлементПоИмени('Задача-2-1-3')
        self.окно.derevoZadach.setCurrentItem(элемент)

        self.окно.счётчикАвтосохранения = Mock()
        self.окно.счётчикВремени = Mock()
        self.окно.системныйЗначок = Mock()
        self.окно.системныйЗначок.showMessage = Mock()

        self.окно.запуститьЗадачу()

        self.окно.обработчикСчётчикаВремени()

        self.assertEqual("Цикл завершён", self.окно.системныйЗначок.showMessage.call_args[0][0])

        self.assertEqual(период(seconds=3*60), self.окно.расписание.задачи[0].затраченноеВремя())
        self.assertEqual(период(seconds=4*60), self.окно.расписание.задачи[1].затраченноеВремя())
        self.assertEqual(период(0), элемент.задача.своёЗатраченноеВремя)

        проверитьЭлемент(найтиЭлементПоИмени('Задача-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1-2'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-1-1-3'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1-1'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1-2'))
        проверитьЭлемент(найтиЭлементПоИмени('Задача-2-1-3'))

    def testСкладированияФайловДереваПередПереключениемЦикла(self):
        дерево = {'n': "Корень", "l": [ {'n': "Задача-1", "<": {"s": 2 }, }, ] }

        unixВремяАрхива = int(time.time())

        self.окно.загрузитьРасписаниеИзДерева(дерево)
        self.окно.derevoZadach.setCurrentItem(self.окно.расписание.задачи[0].элемент)
        задача = self.окно.расписание.задачи[0]
        self.окно.бегущаяЗадача = задача

        self.окно.обновитьЗатраченноеВремяЗадачи = Mock()
        self.окно.системныйЗначок.showMessage = Mock()
        self.окно.рекурсивноОбновитьЗатраченноеВремяГруппы = Mock()

        self.окно.обработчикСчётчикаВремени()
        self.окно.обработчикСчётчикаВремени()

        имяАрхива = "%s/%s.%s" % (self.окно.настройки['дираАрхива'], self.окно.настройки['имяФайла'], unixВремяАрхива)

        архивноеДерево = self.окно.хранилище.загрузитьИзФайла(имяАрхива)
        дерево['l'][0]['x'] = {'s': 2 }
        self.assertDictEqual(дерево, архивноеДерево)
