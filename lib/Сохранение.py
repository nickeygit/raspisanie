import os
import json
from logging.handlers import RotatingFileHandler

class Хранилище():

    def __init__(self, имяФайла, колвоБекапов=10):
        self.имяФайла = имяФайла
        self.колвоБекапов = колвоБекапов
        путьКдире = os.path.dirname(имяФайла)
        try: os.makedirs(путьКдире)
        except: pass

    def сохранить(self, дерево):
        self.прокрутитьБекапы()
        self.сохранитьВФайл(self.имяФайла, дерево)

    def прокрутитьБекапы(self):
        if self.файлСуществует():
            крутильщик = RotatingFileHandler(self.имяФайла, backupCount=self.колвоБекапов)
            крутильщик.doRollover()

    def файлСуществует(self):
        return os.path.isfile(self.имяФайла)

    def сохранитьВФайл(self, имяФайла, дерево):
        f = open(имяФайла, "w")
        f.write(json.dumps(дерево, ensure_ascii=False, indent="  "))
        f.flush()
        os.fsync(f.fileno())

    def загрузитьИзФайла(self, имяФайла):
        try:
            f = open(имяФайла, "r")
        except:
            return {}
        d = f.read()
        return json.loads(d)

    def загрузить(self):
        return self.загрузитьИзФайла(self.имяФайла)
