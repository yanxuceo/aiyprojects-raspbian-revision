import contextlib
import itertools
import queue
import threading
import time

import board
import digitalio

class Button:
    def _trigger(self, event_queue, callback):
        try:
            while True:
                event_queue.get_nowait().set()
        except queue.Empty:
            pass

        if callback:
            callback()

    def _run(self):
        when_pressed = 0.0
        pressed = False
        while not self._done.is_set():
            now = time.monotonic()
            if now - when_pressed > self._debounce_time:
                if self._button.value == self._expected:
                    if not pressed:
                        pressed = True
                        when_pressed = now
                        self._trigger(self._pressed_queue, self._pressed_callback)
                else:
                    if pressed:
                        pressed = False
                        self._trigger(self._released_queue, self._released_callback)
            self._done.wait(0.05)

    def __init__(self, channel, edge='falling', pull_up_down='up', debounce_time=0.08):
        if pull_up_down not in ('up', 'down'):
            raise ValueError('Must be "up" or "down"')

        if edge not in ('falling', 'rising'):
            raise ValueError('Must be "falling" or "rising"')

        self._button = digitalio.DigitalInOut(getattr(board, channel))
        self._button.direction = digitalio.Direction.INPUT
        self._button.pull = digitalio.Pull.UP if pull_up_down == 'up' else digitalio.Pull.DOWN

        self._pressed_callback = None
        self._released_callback = None

        self._debounce_time = debounce_time
        self._expected = False if edge == 'falling' else True

        self._pressed_queue = queue.Queue()
        self._released_queue = queue.Queue()

        self._done = threading.Event()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def close(self):
        self._done.set()
        self._thread.join()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.close()

    def _when_pressed(self, callback):
        self._pressed_callback = callback
    when_pressed = property(None, _when_pressed)

    def _when_released(self, callback):
        self._released_callback = callback
    when_released = property(None, _when_released)

    def wait_for_press(self, timeout=None):
        event = threading.Event()
        self._pressed_queue.put(event)
        return event.wait(timeout)

    def wait_for_release(self, timeout=None):
        event = threading.Event()
        self._released_queue.put(event)
        return event.wait(timeout)

