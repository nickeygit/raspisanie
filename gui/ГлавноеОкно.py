from PyQt5 import QtCore
from PyQt5.QtCore import QTime, QRect
from PyQt5.QtGui import QBrush, QColor, QIcon
from PyQt5.QtWidgets import QApplication, QTreeWidgetItem, QMenu, QSystemTrayIcon, QMessageBox, QInputDialog
from PyQt5.QtNetwork import QUdpSocket
import time

from gui.main import MainWindow
from lib.Расписание import *
from lib.Сохранение import *
from lib.Допфункции import *

названиеОкна = "Расписание"

колвоБекапов = 9
таймаутЗаписиПослеИзменений = 1
периодАвтоСохранения = 60
периодСчётчикаВремени = 1

цветЗадачи = {
    СостояниеЗадачи.нужноДелать: QColor('#91FF9C'),
    СостояниеЗадачи.можноДелать: QColor(QtCore.Qt.color0),
    СостояниеЗадачи.нельзяДелать: QColor('#B9B9B9')
}

текстСостояния = {
    СостояниеЗадачи.нужноДелать: "Нужно делать",
    СостояниеЗадачи.можноДелать: "Можно делать",
    СостояниеЗадачи.нельзяДелать: "Нельзя делать"
}

UDPПортВнешнихКоманд = 50000
внешняяКомандаВидимости = 'vidimostb'

период1сек = период(seconds=1)
qtime0 = QTime(0, 0)

class ГлавноеОкно(MainWindow):

    деревоЗанято = False

    def __init__(self, настройки):
        super(ГлавноеОкно, self).__init__()

        self.настройки = настройки

        self.создатьКорневуюЗадачу()
        self.создатьКонтекстноеМеню()
        self.создатьИконкиАктивности()
        self.настроитьЗаголовокДереваЗадач()
        self.настроитьОбработчикиКлавишСменыФокуса()
        self.создатьХранилище()
        self.счётчикАвтосохранения = ПериодическийПроцесс(периодАвтоСохранения, QtCore.Qt.VeryCoarseTimer, self.обработчикСчётчикаАвтосохранения)
        self.счётчикВремени = ПериодическийПроцесс(периодСчётчикаВремени, QtCore.Qt.PreciseTimer, self.обработчикСчётчикаВремени)
        self.таймерОтложеннойЗаписи = ВызовСЗадержкой(таймаутЗаписиПослеИзменений, QtCore.Qt.PreciseTimer, self.сохранитьРасписаниеСразу)
        self.создатьСистемныйЗначок()
        self.создатьСокетВнешнихКоманд()
        self.установитьРазмерыОкнаИПоместитьВЦентреРабочегоСтола()

    def создатьКорневуюЗадачу(self):
        self.расписание = Задача("Корень")
        self.расписание.корневаяЗадача = self.расписание
        self.расписание.событиеПередПереключениемЦикла = self.обработчикПередПереключениемЦикла
        self.расписание.событиеПослеПереключенияЦикла = self.обработчикПослеПереключенияЦикла
        self.соединитьЭлементИЗадачу(self.derevoZadach.invisibleRootItem(), self.расписание)

    def создатьКонтекстноеМеню(self):
        self.menu = QMenu(self)
        self.действиеИзменитьЗатраченноеВремяЗадачи = self.menu.addAction("&Изменить время")
        self.действиеИзменитьЗатраченноеВремяЗадачи.triggered.connect(self.on_izmenitbZatrachennoeVremya_triggered)
        self.действиеДобавитьЗадачу = self.menu.addAction("&Добавить задачу")
        self.действиеДобавитьЗадачу.triggered.connect(self.on_addTask_triggered)
        self.действиеУдалитьЗадачу = self.menu.addAction("&Удалить задачу")
        self.действиеУдалитьЗадачу.triggered.connect(self.on_delTask_triggered)
        self.derevoZadach.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

    def создатьИконкиАктивности(self):
        self.иконкаАктивности = {
            True: QIcon('картинки/активно.png'),
            False: QIcon('картинки/неактивно.png')
        }

    def создатьСистемныйЗначок(self):
        self.системныйЗначок = QSystemTrayIcon(self)
        self.системныйЗначок.activated.connect(self.nazhatSystemnyjZnachok)
        # self.системныйЗначок.setContextMenu(Menu)

        self.системныйЗначок.setIcon(self.иконкаАктивности[False])
        self.системныйЗначок.setToolTip('--')
        self.системныйЗначок.show()

    def создатьСокетВнешнихКоманд(self):
        self.сокетВнешнихКоманд = QUdpSocket(self)
        self.сокетВнешнихКоманд.bind(UDPПортВнешнихКоманд)
        self.сокетВнешнихКоманд.readyRead.connect(self.prinyataVnewnyayaKomanda)

    def создатьХранилище(self):
        путьКфайлу = "%s/%s" % (self.настройки['путьКдире'], self.настройки['имяФайла'])

        self.хранилище = Хранилище(путьКфайлу, колвоБекапов)
        self.загрузитьРасписание()

    def установитьРазмерыОкнаИПоместитьВЦентреРабочегоСтола(self):
        desktop = QApplication.desktop()
        screenRect = desktop.screenGeometry(desktop.primaryScreen())
        windowRect = QRect(0, 0, self.настройки['ширина'], self.настройки['высота'])

        if screenRect.width() < self.настройки['ширина']:
            windowRect.setWidth(screenRect.width())

        if screenRect.height() < self.настройки['высота']:
            windowRect.setHeight(screenRect.height())

        windowRect.moveCenter(screenRect.center())
        self.setGeometry(windowRect)

    def задатьАктивностьЭлементаШрифтом(self, элемент, активен):
        font = элемент.font(self.СТОЛБИК_ИМЕНИ)
        font.setBold(активен)
        for i in range(self.header.count()):
            элемент.setFont(i, font)

    def остановитьЗадачу(self):
        self.системныйЗначок.setIcon(self.иконкаАктивности[False])
        self.системныйЗначок.setToolTip('--')
        self.setWindowTitle(названиеОкна)
        self.счётчикВремени.стоп()
        self.счётчикАвтосохранения.стоп()
        элемент = self.бегущаяЗадача.элемент
        self.задатьАктивностьЭлементаШрифтом(элемент, False)
        self.сохранитьРасписаниеСразу()
        self.бегущаяЗадача = None

    def запуститьЗадачу(self):
        self.системныйЗначок.setIcon(self.иконкаАктивности[True])
        элемент = self.текущийЭлемент()
        self.бегущаяЗадача = элемент.задача
        self.системныйЗначок.setToolTip(self.бегущаяЗадача.имя)
        self.setWindowTitle("%s :: %s" % (self.бегущаяЗадача.имя, названиеОкна))
        self.задатьАктивностьЭлементаШрифтом(элемент, True)
        self.счётчикАвтосохранения.старт()
        self.счётчикВремени.старт()

    def prinyataVnewnyayaKomanda(self):
        while self.сокетВнешнихКоманд.hasPendingDatagrams():
            данные, хост, порт = self.сокетВнешнихКоманд.readDatagram(self.сокетВнешнихКоманд.pendingDatagramSize())
            данные = str(данные, encoding='UTF-8')
            if данные == внешняяКомандаВидимости:
                self.показатьОкно()

    def nazhatSystemnyjZnachok(self):
        self.показатьОкно()

    def показатьОкно(self):
        self.setWindowState(QtCore.Qt.WindowNoState)
        self.hide()
        self.showNormal()
        self.setWindowState(QtCore.Qt.WindowActive)

    def обработчикСчётчикаАвтосохранения(self):
        self.сохранитьРасписаниеСразу()

    def обработчикСчётчикаВремени(self):
        self.затратитьВремяНаЗадачу(self.бегущаяЗадача, период1сек)

    def обработчикПередПереключениемЦикла(self):
        self.заархивироватьРасписание()

    def обработчикПослеПереключенияЦикла(self):
        self.системныйЗначок.showMessage("Цикл завершён", "а тут какая-то статистика", QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Warning), 0)
        self.обновитьВсёРасписание()

    def заархивироватьРасписание(self):
        дерево = self.расписание.экспортДерева()
        try: os.makedirs(self.настройки['дираАрхива'])
        except: pass
        имяАрхива = "%s/%s.%s" % (self.настройки['дираАрхива'], self.настройки['имяФайла'], int(time.time()))
        self.хранилище.сохранитьВФайл(имяАрхива, дерево)

    def обновитьВсёРасписание(self):
        self.деревоЗанято = True
        for задача in self.расписание.задачи:
            self.обновитьЭлементЗадачи(задача)
        self.деревоЗанято = False

    def обновитьЭлементЗадачи(self, задача):
        self.обновитьЭлемент(задача.элемент)
        for з in задача.задачи:
            self.обновитьЭлементЗадачи(з)

    def обновитьЗатраченноеВремяЗадачи(self, задача, элемент):
        элемент.setText(self.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО, периодВСтрокуиСекунды(задача.своёЗатраченноеВремя))
        self.обновитьФонЭлемента(элемент)

    def обновитьЗатраченноеВремяГруппы(self, задача, элемент):
        элемент.setText(self.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО, периодВСтрокуиСекунды(задача.затраченноеВремя()))


    def отобразитьДеталиЗадачи(self, задача):
        self.деревоЗанято = True
        self.imyaZadachi.setText(задача.имя)
        self.kratkoeOpisanie.setText(задача.краткоеОписание)
        self.detalnoeOpisanie.setPlainText(задача.детальноеОписание)
        минимум = задача.минимальноеВремя()
        максимум = задача.максимальноеВремя()
        self.minimumFlag.setChecked(минимум is not None)
        self.maximumFlag.setChecked(максимум is not None)
        self.minimumPeriod.setEnabled(минимум is not None)
        self.maximumPeriod.setEnabled(максимум is not None)
        if минимум is not None:
            дни, часы, минуты, сек = периодВДниЧасыМинутыСекунды(минимум)
            self.minimumPeriod.setTime(QTime(часы, минуты))
        else:
            self.minimumPeriod.setTime(qtime0)

        if максимум is not None:
            дни, часы, минуты, сек = периодВДниЧасыМинутыСекунды(максимум)
            self.maximumPeriod.setTime(QTime(часы, минуты))
        else:
            self.maximumPeriod.setTime(qtime0)
        self.деревоЗанято = False

    def сохранитьРасписание(self):
        if self.деревоЗанято: return
        self.таймерОтложеннойЗаписи.старт()

    def сохранитьРасписаниеСразу(self):
        if self.деревоЗанято: return
        print("СОХРАНЯЮ")
        дерево = self.расписание.экспортДерева()
        self.хранилище.сохранить(дерево)

    def загрузитьРасписание(self):
        дерево = self.хранилище.загрузить()
        self.загрузитьРасписаниеИзДерева(дерево)

    def загрузитьРасписаниеИзДерева(self, дерево):
        self.деревоЗанято = True
        self.расписание.загрузитьИзДерева(дерево)
        for задача in self.расписание.задачи:
            self.создатьЭлементЗадачи(self.derevoZadach.invisibleRootItem(), задача)
        self.derevoZadach.setFocus(QtCore.Qt.OtherFocusReason)
        if self.расписание.задачи:
            self.derevoZadach.setCurrentItem(self.расписание.задачи[0].элемент)
        self.деревоЗанято = False

    def создатьЭлементЗадачи(self, родительскийЭлемент, задача):
        элемент = self.создатьЭлемент(родительскийЭлемент, задача)
        for з in задача.задачи:
            self.создатьЭлементЗадачи(элемент, з)

    def обновитьЭлемент(self, элемент):
        self.обновитьФонЭлемента(элемент)
        self.обновитьВремяЭлемента(элемент)

    def создатьЭлемент(self, родительскийЭлемент, задача):
        элемент = QTreeWidgetItem(родительскийЭлемент)
        родительскийЭлемент.setExpanded(1)
        self.соединитьЭлементИЗадачу(элемент, задача)
        self.задатьВыравниваниеЭлемента(элемент)
        self.задатьНазваниеЭлемента(элемент, задача.имя)
        self.задатьКраткоеОписаниеЭлемента(элемент, задача.краткоеОписание)
        self.задатьДетальноеОписаниеЭлемента(элемент, задача.детальноеОписание)
        self.рекурсивноОбновитьВременаЭлементовВыше(элемент)
        self.обновитьЭлемент(элемент)
        return элемент

    def соединитьЭлементИЗадачу(self, элемент, задача):
        элемент.задача = задача
        задача.элемент = элемент
        задача.предыдущееСостояние = задача.состояние()

    def обновитьФонЭлемента(self, элемент):
        состояние = элемент.задача.состояние()
        кистьФона = QBrush(цветЗадачи[состояние])
        for i in range(self.header.count()):
            элемент.setBackground(i, кистьФона)

    def задатьВыравниваниеЭлемента(self, элемент):
        элемент.setTextAlignment(self.СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        элемент.setTextAlignment(self.СТОЛБИК_СВОЁ_ЗАТРАЧЕНО, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        элемент.setTextAlignment(self.СТОЛБИК_МАКСИМУМА, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        элемент.setTextAlignment(self.СТОЛБИК_МИНИМУМА, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

    def задатьНазваниеЭлемента(self, элемент, название):
        элемент.setText(self.СТОЛБИК_ИМЕНИ, название)
        элемент.задача.задатьИмя(название)
        self.сохранитьРасписание()

    def задатьКраткоеОписаниеЭлемента(self, элемент, описание):
        элемент.задача.задатьКраткоеОписание(описание)
        self.сохранитьРасписание()

    def задатьДетальноеОписаниеЭлемента(self, элемент, описание):
        элемент.задача.задатьДетальноеОписание(описание)
        self.сохранитьРасписание()

    def изменитьЗатраченноеВремяЗадачи(self):
        минут, результат = QInputDialog.getInt(self, "Количество минут +/-", "Минут:", -5)
        if not результат:
            return
        элемент = self.текущийЭлемент()
        self.затратитьВремяНаЗадачу(элемент.задача, период(seconds=минут * 60))
        self.сохранитьРасписание()

    def затратитьВремяНаЗадачу(self, задача, период):
        задача.затратитьВремя(период)
        self.обновитьСостояниеЗадачи(задача)
        self.обновитьЗатраченноеВремяЗадачи(задача, задача.элемент)
        self.рекурсивноОбновитьЗатраченноеВремяГруппы(задача.элемент)

    def обновитьСостояниеЗадачи(self, задача):
        состояние = задача.состояние()
        # print ("Состояния:", задача.своёЗатраченноеВремя, состояние, задача.предыдущееСостояние)
        if состояние != задача.предыдущееСостояние:
            self.системныйЗначок.showMessage(текстСостояния[состояние], str(задача), QSystemTrayIcon.MessageIcon(QSystemTrayIcon.Warning), 0)
        задача.предыдущееСостояние = состояние

    def удалитьЗадачу(self):
        if QMessageBox.question(self, "Подтверждение", "Удалить задачу?",
                QMessageBox.Yes | QMessageBox.No) != QMessageBox.Yes:
            return

        try: элемент = self.derevoZadach.selectedItems()[0]
        except: return

        if элемент.задача == self.бегущаяЗадача:
            self.остановитьЗадачу()

        self.очиститьДеталиЗадачи()
        parent = self.получитьРодителяЭлемента(элемент)
        parent.задача.удалитьВложеннуюЗадачу(элемент.задача)
        parent.removeChild(элемент)
        self.сохранитьРасписание()

    def создатьЗадачу(self, родительскаяЗадача=None):
        if родительскаяЗадача:
            задача = родительскаяЗадача.создатьЗадачу("")
        else:
            задача = self.расписание.создатьЗадачу("")
        return задача

    def очиститьДеталиЗадачи(self):
        self.деревоЗанято = True
        self.kratkoeOpisanie.clear()
        self.imyaZadachi.clear()
        self.detalnoeOpisanie.clear()
        self.minimumFlag.setChecked(False)
        self.maximumFlag.setChecked(False)
        self.maximumPeriod.setTime(qtime0)
        self.minimumPeriod.setTime(qtime0)
        self.деревоЗанято = False

