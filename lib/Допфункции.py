from datetime import timedelta as период
from PyQt5.QtCore import QBasicTimer, QObject


def периодВДниЧасыМинутыСекунды(период):
    return период.days, период.seconds//3600, (период.seconds//60)%60, период.seconds%60

def периодВСтроку(период):
    дни, часы, минуты, сек = периодВДниЧасыМинутыСекунды(период)
    if часы < 10:
        часы = "0%s" % часы
    if минуты < 10:
        минуты = "0%s" % минуты

    if дни == 0:
        return "%s:%s" % (часы, минуты)
    else:
        return "%sд:%sч:%sм" % (дни, часы, минуты)

def периодВСтрокуиСекунды(период):
    дни, часы, минуты, сек = периодВДниЧасыМинутыСекунды(период)
    if часы < 10:
        часы = "0%s" % часы
    if минуты < 10:
        минуты = "0%s" % минуты
    if сек < 10:
        сек = "0%s" % сек

    if дни == 0:
        if часы == минуты == сек == "00":
            return "--"
        elif часы == "00":
            return "%s:%s" % (минуты, сек)
        else:
            return "%s:%s:%s" % (часы, минуты, сек)
    else:
        return "%sд:%s:%s:%s" % (дни, часы, минуты, сек)


class ПериодическийПроцесс():

    def __init__(self, период, точность, обработчик):
        self.таймер = QBasicTimer()
        self.период = период
        self.точность = точность
        self.обработчик = обработчик
        self.объект = QObject()
        self.объект.timerEvent = self.timerEvent

    def старт(self):
        self.таймер.start(self.период*1000, self.точность, self.объект)

    def timerEvent(self, event):
        self.обработчик()

    def стоп(self):
        self.таймер.stop()

class ВызовСЗадержкой(ПериодическийПроцесс):

    def __init__(self, период, точность, обработчик):
        super(ВызовСЗадержкой, self).__init__(период, точность, обработчик)

    def timerEvent(self, event):
        super(ВызовСЗадержкой, self).timerEvent(event)
        self.стоп()

