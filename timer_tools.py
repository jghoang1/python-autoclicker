import time
import logging


class Timer:
    def __init__(self, duration, repeats=True, callback=None) -> None:
        self.logger = logging.getLogger(
            f"{self.__module__}.{self.__class__.__name__}"
        )
        self.duration = duration
        self.repeats = repeats
        self.callback = callback

        self.remaining_time = self.duration
        self.prev_t = time.time()
        self.is_active = False

    def __repr__(self) -> str:
        return f"Timer({self.duration})"

    def start(self):
        self.logger.info("Starting timer")
        self.is_active = True

    def reset(self):
        self.logger.info("Resetting timer")
        self.is_active = False
        self.remaining_time = self.duration

    def set_duration(self, duration, reset=False):
        self.duration = duration
        if reset:
            self.logger.info(f"Resetting timer with new duration {duration}")
            self.remaining_time = self.duration
            self.is_active = self.repeats

    def set_callback(self, callback, reset=False):
        self.callback = callback
        if reset:
            self.logger.info(f"Resetting timer with new callback {callback}")
            self.remaining_time = self.callback
            self.is_active = self.repeats

    def pause(self):
        self.logger.info("Pausing timer")
        self.is_active = False

    def update(self):
        t = time.time()
        dt = t - self.prev_t

        if self.is_active:
            self.remaining_time -= dt

            if self.remaining_time <= 0:
                # hit end of timer
                self.logger.info(
                    f"Hit callback in {self}. Calling {self.callback.__name__}"
                )
                self.callback()
                # reset timer
                self.remaining_time = self.duration
                self.is_active = self.is_active and self.repeats

        self.prev_t = t
