from tkinter import ttk

from .base import AutoclickerRow


class TimerRow(AutoclickerRow):
    def __init__(
        self, parent, timer, label, initial_time, initial_playstate=True
    ) -> None:
        super().__init__(parent, label, initial_playstate)
        self.timer = timer
        self.initial_time = initial_time

        # Col 1 : Play label
        self.play_label.config(
            text=self._format_time(self.timer.remaining_time)
        )

        # Col 2 : Function Label
        self.func_label = ttk.Label(self.parent.frm, text=label)
        self.func_label.grid(column=2, row=self.parent.current_row)

        # Col 3 : Reset Button
        self.reset_button = ttk.Button(
            self.parent.frm, text="Reset", command=self.reset_time
        )
        self.reset_button.grid(column=3, row=self.parent.current_row)

        self.parent.current_row += 1
        if self.timer.duration < 1:
            self.update = self._update_no_label
        else:
            self.update = self._update

    def _update_no_label(self):
        self.timer.update()

    def _update(self):
        self.timer.update()
        self.play_label.config(
            text=self._format_time(self.timer.remaining_time)
        )

    def play(self):
        self.timer.start()

    def pause(self):
        self.timer.pause()

    def reset_time(self):
        self.timer.remaining_time = self.initial_time


