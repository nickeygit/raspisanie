from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QTime
from PyQt5.QtWidgets import QMainWindow, QHeaderView, QTreeWidget, QTreeWidgetItem,\
        QLineEdit, QPlainTextEdit
from Ui_main import Ui_MainWindow

from lib.Допфункции import *

период0 = период(0)

class MainWindow(QMainWindow, Ui_MainWindow):

    СТОЛБИК_ИМЕНИ = 0
    СТОЛБИК_ВСЕГО_ЗАТРАЧЕНО = 1
    СТОЛБИК_СВОЁ_ЗАТРАЧЕНО = 2
    СТОЛБИК_МАКСИМУМА = 3
    СТОЛБИК_МИНИМУМА = 4

    бегущаяЗадача = None

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def настроитьЗаголовокДереваЗадач(self):
        self.header = self.derevoZadach.header()
        for i in range(self.header.count()):
            self.header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

    def настроитьОбработчикиКлавишСменыФокуса(self):
        self.derevoZadach.keyPressEvent = self.on_derevoZadach_keyPressEvent
        self.imyaZadachi.keyPressEvent = self.on_imyaZadachi_keyPressEvent
        self.kratkoeOpisanie.keyPressEvent = self.on_kratkoeOpisanie_keyPressEvent
        self.detalnoeOpisanie.keyPressEvent = self.on_detalnoeOpisanie_keyPressEvent

    def текущийЭлемент(self):
        return self.derevoZadach.currentItem()

    def получитьРодителяЭлемента(self, элемент):
        return элемент.parent() or self.derevoZadach.invisibleRootItem()

    @pyqtSlot('QPoint')
    def on_derevoZadach_customContextMenuRequested(self, point):
        globalPoint = self.derevoZadach.mapToGlobal(point)
        self.menu.popup(globalPoint)

    @pyqtSlot(QTreeWidgetItem, QTreeWidgetItem)
    def on_derevoZadach_currentItemChanged(self, новый, предыдущий):
        элемент = self.текущийЭлемент()
        if элемент:
            self.разрешитьиОтобразитьДеталиЗадачи(элемент.задача)
        else:
            self.запретитьиОчиститьДеталиЗадачи()

    def разрешитьиОтобразитьДеталиЗадачи(self, задача):
        self.задатьСостояниеЭлементовДеталей(True)
        self.отобразитьДеталиЗадачи(задача)

    def запретитьиОчиститьДеталиЗадачи(self):
        self.задатьСостояниеЭлементовДеталей(False)
        self.очиститьДеталиЗадачи()

    def задатьСостояниеЭлементовДеталей(self, состояние):
        self.startStopKnopka.setEnabled(состояние)
        self.kratkoeOpisanie.setEnabled(состояние)
        self.imyaZadachi.setEnabled(состояние)
        self.minimumFlag.setEnabled(состояние)
        self.maximumFlag.setEnabled(состояние)
        if not состояние:
            self.maximumPeriod.setEnabled(состояние)
            self.minimumPeriod.setEnabled(состояние)
        self.detalnoeOpisanie.setEnabled(состояние)


    def on_derevoZadach_keyPressEvent(self, событие):
        key = событие.key()
        if key == QtCore.Qt.Key_Return and событие.modifiers() == QtCore.Qt.ShiftModifier:
            self.imyaZadachi.setFocus(QtCore.Qt.OtherFocusReason)
            self.imyaZadachi.selectAll()
        elif key == QtCore.Qt.Key_Return:
            self.on_startStopKnopka_clicked()
        elif key == QtCore.Qt.Key_Delete:
            self.удалитьЗадачу()
        elif key == QtCore.Qt.Key_Escape:
            self.hide()
        elif key == QtCore.Qt.Key_Left:
            элемент = self.текущийЭлемент()
            if (len(элемент.задача.задачи) == 0 or not элемент.isExpanded()) and элемент.parent():
                self.derevoZadach.setCurrentItem(элемент.parent())
            else:
                QTreeWidget.keyPressEvent(self.derevoZadach, событие)
        elif key == QtCore.Qt.Key_Right:
            элемент = self.текущийЭлемент()
            if len(элемент.задача.задачи) and элемент.isExpanded():
                self.derevoZadach.setCurrentItem(элемент.задача.задачи[0].элемент)
            else:
                QTreeWidget.keyPressEvent(self.derevoZadach, событие)
        else:
            QTreeWidget.keyPressEvent(self.derevoZadach, событие)


    @pyqtSlot('QString')
    def on_imyaZadachi_textEdited(self, имя):
        if self.текущийЭлемент() is None:
            return
        self.задатьНазваниеЭлемента(self.текущийЭлемент(), имя)

    def on_imyaZadachi_keyPressEvent(self, событие):
        if событие.key() == QtCore.Qt.Key_Escape:
            self.derevoZadach.setFocus(QtCore.Qt.OtherFocusReason)
        elif событие.key() == QtCore.Qt.Key_Return:
            self.kratkoeOpisanie.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            QLineEdit.keyPressEvent(self.imyaZadachi, событие)


    @pyqtSlot('QString')
    def on_kratkoeOpisanie_textEdited(self, описание):
        if self.текущийЭлемент() is None:
            return
        self.задатьКраткоеОписаниеЭлемента(self.текущийЭлемент(), описание)

    def on_kratkoeOpisanie_keyPressEvent(self, событие):
        if событие.key() == QtCore.Qt.Key_Escape:
            self.derevoZadach.setFocus(QtCore.Qt.OtherFocusReason)
        elif событие.key() == QtCore.Qt.Key_Return:
            self.detalnoeOpisanie.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            QLineEdit.keyPressEvent(self.kratkoeOpisanie, событие)


    @pyqtSlot()
    def on_detalnoeOpisanie_textChanged(self):
        if self.деревоЗанято: return
        if self.текущийЭлемент() is None:
            return
        self.задатьДетальноеОписаниеЭлемента(self.текущийЭлемент(), self.detalnoeOpisanie.toPlainText())

    def on_detalnoeOpisanie_keyPressEvent(self, событие):
        if событие.key() == QtCore.Qt.Key_Escape:
            self.derevoZadach.setFocus(QtCore.Qt.OtherFocusReason)
        else:
            QPlainTextEdit.keyPressEvent(self.detalnoeOpisanie, событие)

    @pyqtSlot(int)
    def on_minimumFlag_stateChanged(self, состояние):
        if self.деревоЗанято: return
        if состояние == QtCore.Qt.Checked:
            новыйПериод = период0
        else:
            новыйПериод = None
        self.minimumPeriod.setEnabled(новыйПериод is not None)
        self.задатьМинимальноеВремяЭлемента(новыйПериод)

    @pyqtSlot(QTime)
    def on_minimumPeriod_timeChanged(self, новоеВремя):
        if self.деревоЗанято: return
        новыйПериод = период(hours=новоеВремя.hour(), minutes=новоеВремя.minute())
        self.задатьМинимальноеВремяЭлемента(новыйПериод)

    def задатьМинимальноеВремяЭлемента(self, новыйПериод):
        элемент = self.текущийЭлемент()
        элемент.задача.задатьМинимальноеВремя(новыйПериод)
        self.обновитьСостояниеЗадачи(элемент.задача)
        self.рекурсивноОбновитьВременаЭлементовВыше(элемент)
        self.сохранитьРасписание()

    @pyqtSlot('int')
    def on_maximumFlag_stateChanged(self, состояние):
        if self.деревоЗанято: return
        if состояние == QtCore.Qt.Checked:
            новыйПериод = период0
        else:
            новыйПериод = None
        self.maximumPeriod.setEnabled(новыйПериод is not None)
        self.задатьМаксимальноеВремяЭлемента(новыйПериод)

    @pyqtSlot(QTime)
    def on_maximumPeriod_timeChanged(self, новоеВремя):
        if self.деревоЗанято: return
        новыйПериод = период(hours=новоеВремя.hour(), minutes=новоеВремя.minute())
        self.задатьМаксимальноеВремяЭлемента(новыйПериод)

    def задатьМаксимальноеВремяЭлемента(self, новыйПериод):
        элемент = self.текущийЭлемент()
        элемент.задача.задатьМаксимальноеВремя(новыйПериод)
        self.обновитьСостояниеЗадачи(элемент.задача)
        self.рекурсивноОбновитьВременаЭлементовВыше(элемент)
        self.сохранитьРасписание()

    def рекурсивноОбновитьВременаЭлементовВыше(self, элемент):
        while элемент is not None:
            self.обновитьВремяЭлемента(элемент)
            элемент = элемент.parent()

    def рекурсивноОбновитьЗатраченноеВремяГруппы(self, элемент):
        while элемент is not None:
            self.обновитьЗатраченноеВремяГруппы(элемент.задача, элемент)
            элемент = элемент.parent()

    def обновитьВремяЭлемента(self, элемент):
        задача = элемент.задача
        self.обновитьЗатраченноеВремяЗадачи(задача, элемент)
        self.обновитьЗатраченноеВремяГруппы(задача, элемент)
        минимум = задача.минимальноеВремя()
        максимум = задача.максимальноеВремя()
        if минимум is not None:
            элемент.setText(self.СТОЛБИК_МИНИМУМА, периодВСтроку(минимум))
        else:
            элемент.setText(self.СТОЛБИК_МИНИМУМА, "")
        if максимум is not None:
            элемент.setText(self.СТОЛБИК_МАКСИМУМА, периодВСтроку(максимум))
        else:
            элемент.setText(self.СТОЛБИК_МАКСИМУМА, "")


    @pyqtSlot()
    def on_novayaVlozhennayaZadachaMenu_triggered(self):
        self.добавитьВложенныйЭлементЗадачи()

    @pyqtSlot()
    def on_novayaVlozhennayaZadacha_clicked(self):
        self.добавитьВложенныйЭлементЗадачи()

    def on_izmenitbZatrachennoeVremya_triggered(self, checked):
        self.изменитьЗатраченноеВремяЗадачи()

    def on_addTask_triggered(self, checked):
        self.добавитьНовыйЭлементЗадачи()

    @pyqtSlot()
    def on_udalitZadachuMenu_triggered(self):
        self.удалитьЗадачу()

    def on_delTask_triggered(self, checked):
        self.удалитьЗадачу()

    @pyqtSlot()
    def on_novayaZadachaMenu_triggered(self):
        self.добавитьНовыйЭлементЗадачи()

    @pyqtSlot()
    def on_novayaZadachaKnopka_clicked(self):
        self.добавитьНовыйЭлементЗадачи()

    @pyqtSlot()
    def on_startStopKnopka_clicked(self):
        self.стартСтопЗадача()

    @pyqtSlot(QTreeWidgetItem, int)
    def on_derevoZadach_itemDoubleClicked(self, элемент, столбец):
        self.стартСтопЗадача()

    def стартСтопЗадача(self):
        бегущаяЗадача = self.бегущаяЗадача
        if бегущаяЗадача is not None:
            self.остановитьЗадачу()
            if бегущаяЗадача != self.текущийЭлемент().задача:
                self.запуститьЗадачу()
        else:
            self.запуститьЗадачу()

    def добавитьВложенныйЭлементЗадачи(self):
        try: родительскийЭлемент = self.derevoZadach.selectedItems()[0]
        except: родительскийЭлемент = None
        self.добавитьЭлементЗадачиКРодителю(родительскийЭлемент)

    def добавитьНовыйЭлементЗадачи(self):
        try: родительскийЭлемент = self.derevoZadach.selectedItems()[0].parent()
        except: родительскийЭлемент = None
        self.добавитьЭлементЗадачиКРодителю(родительскийЭлемент)

    def добавитьЭлементЗадачиКРодителю(self, родительскийЭлемент):
        if родительскийЭлемент:
            элемент = QTreeWidgetItem(родительскийЭлемент)
            родительскийЭлемент.setExpanded(1)
            задача = self.создатьЗадачу(родительскийЭлемент.задача)
            self.соединитьЭлементИЗадачу(элемент, задача)
        else:
            элемент = QTreeWidgetItem(self.derevoZadach)
            задача = self.создатьЗадачу()
            self.соединитьЭлементИЗадачу(элемент, задача)
        self.задатьВыравниваниеЭлемента(элемент)
        self.задатьНазваниеЭлемента(элемент, "Задача")
        self.derevoZadach.setCurrentItem(элемент)
        self.обновитьВремяЭлемента(элемент)
        self.derevoZadach.setFocus(QtCore.Qt.OtherFocusReason)
        self.сохранитьРасписание()

