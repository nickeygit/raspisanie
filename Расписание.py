#!/usr/bin/python3

import sys
sys.path.insert(0, "gui")
sys.path.insert(0, "lib")
from PyQt5.QtWidgets import QApplication
from gui.ГлавноеОкно import ГлавноеОкно
from _настройки import настройки

def старт():
    import sys
    app = QApplication(sys.argv)
    # QApplication.setQuitOnLastWindowClosed(False)
    mw = ГлавноеОкно(настройки)
    mw.show()
    sys.exit(app.exec_())

старт()