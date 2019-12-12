import sys, time


class ProgressBar:
    def __init__(self, work_name, volume):
        self.progress = 0
        self.volume = volume
        self.work_name = work_name
        self._last_time = time.time()
        self._last_printed_progress = 0
        self.print()

    def do_progress(self, value):
        self.progress = value
        if self._last_printed_progress < int(self.progress * 100 / self.volume) and time.time() - self._last_time >= 1:
            pass
            self.print()

    def finish(self):
        self.progress = self.volume
        self.print()
        sys.stdout.write("Complete!\r\n")
        sys.stdout.flush()

    def print(self):
        self._last_printed_progress = int(self.progress * 100 / self.volume)
        self._last_time = time.time()
        sys.stdout.write("\r%s: %d%% " % (self.work_name, self._last_printed_progress))
        sys.stdout.flush()
