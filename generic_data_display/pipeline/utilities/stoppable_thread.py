import threading
from generic_data_display.utilities.logger import log


class StoppableThread(threading.Thread):
    """
    Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition. Additionally calls stop
    on join
    """

    def __init__(self,  *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._running_event = threading.Event()
        self._running_event.set()

    def is_running(self):
        return self._running_event.is_set()

    def join(self, *args, **kwargs):
        self._running_event.clear()
        log.debug("thread joining: {}".format(self.name))
        super(StoppableThread, self).join(*args, **kwargs)
