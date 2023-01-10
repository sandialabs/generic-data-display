from timeit import default_timer as py_timer
from math import sqrt
import datetime

from generic_data_display.utilities.logger import log


class ContextTimer:
    def __init__(self, timer, name):
        self._timer = timer
        self._name = name

    def __enter__(self):
        self._timer.start_timing(self._name)

    def __exit__(self, exc_type, exc_val, traceback):
        self._timer.stop_timing(self._name)


class Timer(object):
    def __init__(self):
        self._timing_data = {}

    def __call__(self, name):
        return ContextTimer(self, name)

    # wrap underlying timing data
    def keys(self):
        return self._timing_data.keys()

    def __getitem__(self, key):
        if key == '_Total':
            return self.total

        timing = self._timing_data[key]
        if 'end' not in timing.keys() or 'start' not in timing.keys():
            return 0.0
        return timing["end"] - timing["start"]

    def items(self):
        return ((key, self[key]) for key in self.keys())

    def start_timing(self, name):
        if name in self._timing_data:
            log.error(f'Already started timing for {name}, ignoring startTiming call')
            return
        self._timing_data[name] = {'start': py_timer(), 'end': None}
        
    def stop_timing(self, name):
        if name not in self._timing_data:
            log.error(f'Called stop_timing for {name} without corresponding start_timing({name}) call');
            return
        if self._timing_data[name]['end']:
            log.error(f'Already called stop_timing for {name}')
            return
        self._timing_data[name]['end'] = py_timer()

    def print_timing(self):
        log.info(self.log_string)

    @property
    def total(self):
        return sum(self[key] for key in self._timing_data.keys())

    @property
    def log_string(self):
        time_log = f'\n{"TIMING":-^31}\n'
        for process_name, timing in self.items():
            time_log += f'{process_name:>30}: {timing:0.5f}s\n'
        time_log += f'{"Total":>30}: {self.total:0.5f}s\n'
        time_log += 31 * '-'
        return time_log


class TimerCollection:
    def __init__(self, print_timing, print_rate_ms):
        self.print_timing = print_timing
        self._len = dict()
        self._mean = dict()
        self._m2 = dict()
        self._min = dict()
        self._max = dict()

        self.last_time_printed = datetime.datetime.min
        self.time_delta = datetime.timedelta(milliseconds=print_rate_ms)

    def store(self, timer):
        if self.print_timing:
            if datetime.datetime.now() > self.last_time_printed + self.time_delta:
                self.last_time_printed = datetime.datetime.now()
                timer.print_timing()

        for key in list(timer.keys()) + ['_Total']:
            self._len[key] = self._len.get(key, 0) + 1
            delta = timer[key] - self._mean.get(key, 0)
            self._mean[key] = self._mean.get(key, 0) + (delta / self._len[key])
            delta2 = timer[key] - self._mean[key]
            self._m2[key] = self._m2.get(key, 0) + delta * delta2

            self._min.setdefault(key, timer[key])
            self._min[key] = min(self._min[key], timer[key])
            self._max.setdefault(key, timer[key])
            self._max[key] = max(self._max[key], timer[key])

    @property
    def log_string(self):
        time_log = f'\n{"STATS":-^31}'
        time_log += f'{"AVG":-^10}'
        time_log += f'{"STD":-^10}'
        time_log += f'{"MIN":-^10}'
        time_log += f'{"MAX":-^10}\n'

        for process in self._len.keys():
            time_log += f'{process:>30}:'
            time_log += f' {self._mean.get(process, 0):0.5f}s '
            stddev = sqrt(self._m2.get(process, 0) / self._len.get(process, 1))
            time_log += f' {stddev:0.5f}s '
            time_log += f' {self._min.get(process, 0):0.5f}s '
            time_log += f' {self._max.get(process, 0):0.5f}s\n'
        time_log += 71 * '-'
        return time_log
