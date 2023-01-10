import queue
import traceback

from generic_data_display.pipeline.utilities.access_wrapper import ConfWrapper
from generic_data_display.pipeline.utilities.stoppable_thread import StoppableThread
from generic_data_display.pipeline.utilities.access_wrapper import MatchFailure
from generic_data_display.utilities.logger import log


class BasicPreprocessor(StoppableThread):
    """A basic implementation of a preprocessor class

    Implements the `run` method which should be similar for the majority of
    preprocessors. Subclasses are expected to override the 'process' method
    and 'close' method as needed. 'process' should expect to take in an AccessWrapper
    object.
    """

    def __init__(self, pop_queue, push_queue, *args, **kwargs):
        super(BasicPreprocessor, self).__init__(*args, **kwargs)
        self.pop_queue = pop_queue
        self.push_queue = push_queue
        self.config = {}

    def process(self, data_object):
        pass

    def close(self):
        pass

    def run(self):
        try:
            while self.is_running():
                try:
                    data_object = self.pop_queue.get(block=False, timeout=None)
                except queue.Empty:
                    continue

                with data_object.timer(self.name):
                    try:
                        for wrapper in ConfWrapper.MatchAll(self.config, data_object):
                            self.process(wrapper)
                    except MatchFailure as err:
                        log.warn(f"processor {self.name} had error: {err}")
                    except KeyError as err:
                        if str(err) != "'throttled'":
                            log.error(f"{err}; this implies the key provided was not found in your data.")
                    except ValueError as err:
                        log.error(err)
                    finally:
                        self.push_queue.put(data_object)
        except:
            log.error(f"Caught exception while processing in Basic Preprocessor ({self.name}):\n{traceback.format_exc()}")
        finally:
            log.info(f"Closing Basic Preprocessor: {self.name}")
            self.close()
