import logging
from tkinter import ttk

from common import COLOR_OFF, COLOR_OFF_INACTIVE, COLOR_ON, COLOR_ON_INACTIVE


class AutoclickerRow:
    def __init__(self, parent, label, initial_playstate=True) -> None:
        self.parent = parent
        self.original_label = label
        self.label = label
        self.is_playing = initial_playstate
        self.logger = logging.getLogger(
            f"{self.__class__.__name__}:{self.original_label}"
        )

        # Col 0 : Button
        self.play_button = ttk.Button(
            self.parent.frm,
            text="Pause" if self.is_playing else "Play",
            command=self.play_pause,
        )
        self.play_button.grid(column=0, row=self.parent.current_row)
        # Col 1 : Play Label
        self.play_label = ttk.Label(
            self.parent.frm,
            text="dummy text",
            background=self.get_correct_color(),
        )
        self.play_label.grid(column=1, row=self.parent.current_row)

    def play_pause(self):
        self.is_playing = not self.is_playing
        self.logger.info(f"New playstate: {self.is_playing}")
        self.play_button.config(text="Pause" if self.is_playing else "Play")
        self.set_play_label_color()
        if self.parent.is_playing and self.is_playing:
            self.timer.start()
        else:
            self.timer.pause()

    def play_pause_upstream(self):
        self.logger.info(
            f"New playstate from upstream: {self.parent.is_playing and self.is_playing}"
        )
        self.set_play_label_color()
        if self.parent.is_playing and self.is_playing:
            self.play()
        else:
            self.pause()

    def play(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def get_correct_color(self):
        if self.is_playing:
            return COLOR_ON if self.parent.is_playing else COLOR_ON_INACTIVE
        else:
            return COLOR_OFF if self.parent.is_playing else COLOR_OFF_INACTIVE

    def set_play_label_color(self):
        color = self.get_correct_color()
        self.play_label.config(background=color)

    def _format_time(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours != 0:
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        elif minutes != 0:
            return f"{int(minutes):02}:{int(seconds):02}"
        else:
            return f"{seconds:05.2f}"


