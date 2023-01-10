import queue
import traceback

from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from generic_data_display.utilities.logger import log


class TeeQueue(StoppableThread):
    """
    brief: Takes an input queue, pops the data, then pushes duplicate data onto multiple output queues
           On Linux systems this is similar to 'tee'
           Effectively, this duplicates input data across multiple output queues

    Note: The data that is duplicated is a shallow copy, this means that modifying the data from one output
          queue will also modify the data processed in another output queue. It is expected that output stages
          operating on tee'ed data won't modify the data popped from a tee'ed queue directly. If this expectation
          doesn't hold the data_object will need to be deep copied
    """

    def __init__(self, pop_queue, *args, **kwargs):
        super(TeeQueue, self).__init__(name="TeeQueue", *args, **kwargs)
        self.pop_queue = pop_queue
        self.push_queues = []

    def __bool__(self):
        return bool(self.push_queues)

    def get_queue(self):
        log.debug(f"Generating new push queue for {self.name}")
        push_queue = queue.Queue()
        self.push_queues.append(push_queue)
        return push_queue

    def run(self):
        try:
            while self.is_running():
                try:
                    data_object = self.pop_queue.get(block=False, timeout=None)
                except queue.Empty:
                    continue

                try:
                    with data_object.timer(self.name):
                        for push_queue in self.push_queues:
                            push_queue.put(data_object)
                except AttributeError:
                    for push_queue in self.push_queues:
                        push_queue.put(data_object)
        except:
            log.error(f"Caught exception while processing, ({self.name}):\n{traceback.format_exc()}")
