import sys
import time

class Progressor:
    def __init__(self, work_name, volume, printer):
        self.progress = 0
        self.volume = volume
        self.printer = printer
        self.work_name = work_name

    def do_progress(self, value):
        """
        :param value: целое значение, объем выполненной работы
        Вызывает переданную при инициализации функцию printer от себя, для отрисовки нового прогресса
        """
        self.progress = value
        self.printer(self)


def consoleProgress(progressor):
    sys.stdout.write("\r%s: %d%% " % (progressor.work_name,  int(progressor.progress * 100 / progressor.volume)))
    if progressor.volume == progressor.progress:
        sys.stdout.write("Complete!\r\n")
    sys.stdout.flush()


if __name__ == "__main__":
    pr = Progressor("Reading", 80, consoleProgress)
    for i in range(80 + 1):
        time.sleep(0.05)
        pr.do_progress(i)

    pr = Progressor("Unpacking", 80, consoleProgress)
    for i in range(80 + 1):
        time.sleep(0.05)
        pr.do_progress(i)
