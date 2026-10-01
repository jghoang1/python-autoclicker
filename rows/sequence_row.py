import tkinter as tk
from tkinter import ttk

from common import INPUT_SHIM as input_shim
from timer_tools import Timer
from .base import AutoclickerRow


class SequenceRow(AutoclickerRow):
    def __init__(self, parent, sequence, label, initial_playstate=True) -> None:
        super().__init__(parent, label, initial_playstate)
        self.sequence = sequence  # list of tuples [(key, time),]

        self.seq_idx = 0
        self.timer = Timer(0.01, callback=self.callback)

        # Col 1 : Play label
        self.play_label.config(
            text=self._format_time(self.timer.remaining_time)
        )

        # Col 2 : Function Label
        self.func_stringvar = tk.StringVar()
        self.func_stringvar.set(self.original_label)
        self.func_label = ttk.Label(
            self.parent.frm, textvariable=self.func_stringvar
        )
        self.func_label.grid(column=2, row=self.parent.current_row)
        # Col 3 : Reset Button
        self.reset_button = ttk.Button(
            self.parent.frm, text="Reset", command=self.reset_time
        )
        self.reset_button.grid(column=3, row=self.parent.current_row)

        self.parent.current_row += 1

    def reset_time(self):
        pass

    def callback(self):
        self.logger.info(f"Sequence callback. seq_idc: {self.seq_idx}")
        keys, duration = self.sequence[self.seq_idx]
        if isinstance(keys, str):
            keys = [keys]
        prev_keys, _ = self.sequence[(self.seq_idx - 1) % len(self.sequence)]
        if isinstance(prev_keys, str):
            prev_keys = [prev_keys]

        self.logger.info(f"Sequence callback. KeyUp: {prev_keys}")
        self.func_stringvar.set(f"{self.original_label} : {keys}")
        self.logger.info(f"Sequence callback. keyDown: {keys}")

        for prev_key in prev_keys:
            input_shim.keyUp(prev_key)
        for key in keys:
            input_shim.keyDown(key)
        
        self.timer.set_duration(duration)

        self.seq_idx = (self.seq_idx + 1) % len(self.sequence)
        self.logger.info(f"Sequence callback. new seq_idx: {self.seq_idx}")

    def play(self):
        self.timer.start()

    def pause(self):
        self.timer.pause()

    def update(self):
        self.timer.update()
        self.play_label.config(
            text=self._format_time(self.timer.remaining_time)
        )


