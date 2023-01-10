import queue

from generic_data_display.utilities.logger import log


class OutputQueues(object):
    def __init__(self):
        self.output_queues = {}

    def __bool__(self):
        return bool(self.output_queues)

    def __getitem__(self, name):
        if name in self.output_queues:
            return self.output_queues[name]
        raise KeyError(f"{name} was not in output_queues")

    def get_queue(self, key):
        log.debug(f"Appending output queue for {key}")
        self.add_key(key)
        push_queue = queue.Queue()
        self.output_queues[key].append(push_queue)
        return push_queue

    def add_key(self, key):
        if key not in self.output_queues:
            self.output_queues[key] = []

    def items(self):
        for key, queue_list in self.output_queues.items():
            yield key, queue_list

    def merge(self, output_queues):
        for key, queue_list in output_queues.items():
            log.debug(f"Extending output queue for {key}")
            self.add_key(key)
            self.output_queues[key].extend(queue_list)
