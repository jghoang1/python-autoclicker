import logging
import sys
import time
import tkinter as tk
from tkinter import ttk

import pyautogui
from common import (
    COLOR_OFF,
    COLOR_ON,
    COLUMNS,
    DEFAULT_DELAY,
    FRAMELENGTH,
    MINHEIGHT,
    MINWIDTH,
)
from pynput.keyboard import Key, Listener
from timer_tools import Timer
from rows import AutoclickerRow, AudioTriggerRow, SequenceRow, TimerRow

os_platform = sys.platform
print(f"OS Platform (sys.platform): {os_platform}")

if os_platform == "win32":
    print("Running on Windows.")
    import pydirectinput
    input_shim = pydirectinput
elif os_platform == "linux":
    print("Running on Linux.")
elif os_platform == "darwin":  # macOS
    print("Running on macOS.")
    input_shim = pyautogui
else:
    print(f"Running on an unknown platform: {os_platform}")


input_shim.PAUSE = 0.005


class AutoClicker:
    STANDARD_BUTTONS = [
        "\t",
        "\n",
        "\r",
        " ",
        "!",
        '"',
        "#",
        "$",
        "%",
        "&",
        "'",
        "(",
        ")",
        "*",
        "+",
        ",",
        "-",
        ".",
        "/",
        "0",
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        ":",
        ";",
        "<",
        "=",
        ">",
        "?",
        "@",
        "[",
        "\\",
        "]",
        "^",
        "_",
        "`",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
        "{",
        "|",
        "}",
        "~",
        "alt",
        "altleft",
        "altright",
        "backspace",
        "capslock",
        "ctrl",
        "ctrlleft",
        "ctrlright",
        "delete",
        "down",
        "end",
        "enter",
        "esc",
        "escape",
        "f1",
        "f10",
        "f11",
        "f12",
        "f13",
        "f14",
        "f15",
        "f16",
        "f17",
        "f18",
        "f19",
        "f2",
        "f20",
        "f21",
        "f22",
        "f23",
        "f24",
        "f3",
        "f4",
        "f5",
        "f6",
        "f7",
        "f8",
        "f9",
        "final",
        "fn",
        "help",
        "home",
        "insert",
        "left",
        "modechange",
        "multiply",
        "num0",
        "num1",
        "num2",
        "num3",
        "num4",
        "num5",
        "num6",
        "num7",
        "num8",
        "num9",
        "numlock",
        "pagedown",
        "pageup",
        "pause",
        "pgdn",
        "pgup",
        "print",
        "printscreen",
        "return",
        "right",
        "scrolllock",
        "shift",
        "shiftleft",
        "shiftright",
        "space",
        "subtract",
        "tab",
        "up",
        "win",
        "winleft",
        "winright",
        "command",
        "option",
        "optionleft",
        "optionright",
    ]

    def __init__(self):
        self.logger = logging.getLogger(
            f"{self.__module__}.{self.__class__.__name__}"
        )

        # Main frame structure
        self.root = tk.Tk()

        self.root.title("Julius's Autoclicker")
        s = ttk.Style()
        s.configure(".", font=("Helvetica", 12))
        self.root.minsize(MINWIDTH, MINHEIGHT)
        self.frm = ttk.Frame(self.root)
        self.frm.grid()

        # Key press listener
        self.listener = Listener(on_press=self._key_press)
        self.listener.start()

        # Rows 0-1 Title
        self.title = tk.StringVar()
        self.title.set("An Autoclicker by Julius")
        self.title_label = ttk.Label(self.frm, textvariable=self.title)
        self.title_label.grid(column=0, row=0, columnspan=COLUMNS)

        self.title_hint = tk.StringVar()
        self.title_hint.set("press END to quit. Press ` to play/pause\n")
        self.title_label_hint = ttk.Label(
            self.frm, textvariable=self.title_hint
        )
        self.title_label_hint.grid(column=0, row=1, columnspan=COLUMNS)

        # Row 2 Mouse Position Detail
        self.label_mouse_pos = ttk.Label(self.frm, text="Mouse Position: ")
        self.label_mouse_pos.grid(
            column=0, row=2, sticky="w", columnspan=COLUMNS
        )

        # Row 3 Play Pause Button
        self.play_button = ttk.Button(
            self.frm, text="Play", command=self.play_pause
        )
        self.play_button.grid(column=0, row=3)
        self.play_label = ttk.Label(
            self.frm, text="Paused", background=COLOR_OFF
        )
        self.play_label.grid(column=1, row=3)
        self.func_label = ttk.Label(self.frm, text="Main Program")
        self.func_label.grid(column=2, row=3)

        self.current_row = 4

        self.row_modules = []
        self.is_playing = False

        self.keybinds = {
            Key.end: self.root.quit,
            "`": self.play_pause,
            "~": self.play_pause,
        }

        self.keys_to_release = ["shift", "alt", "ctrl", "w", "a", "s", "d"]
        self.clicks_to_release = ["left", "right"]

        self.update()

    def __del__(self):
        for key in self.keys_to_release:
            self.logger.info(f"Releasing {key}")
            input_shim.keyUp(key)
        for click in self.clicks_to_release:
            self.logger.info(f"Releasing {click} mouse button")
            pydirectinput.mouseUp(button=click)


    def _key_press(self, key):
        self.logger.debug(f"{key} was pressed")

        if key.__dict__.get("char") in self.keybinds:
            func = self.keybinds[key.char]
            func()

        elif key in self.keybinds:
            func = self.keybinds[key]
            func()

    def delay(self):
        time.sleep(DEFAULT_DELAY)

    def play_pause(self):
        self.is_playing = not self.is_playing
        self.logger.info(f"New playstate: {self.is_playing}")

        # Update timer rows
        for row in self.row_modules:
            row.play_pause_upstream()

        if self.is_playing:
            self.play_label.config(text="Playing", background=COLOR_ON)
            self.play_button.config(text="Pause")
            self.on_play()
        else:
            self.play_label.config(text="Paused", background=COLOR_OFF)
            self.play_button.config(text="Play")
            self.on_pause()

    def add_timer(
        self,
        duration,
        callback,
        label,
        keybind=None,
        initial_time=None,
        initial_playstate=True,
    ):
        timer = Timer(duration, callback=callback)
        if initial_time is not None:
            timer.remaining_time = initial_time
        else:
            initial_time = duration
        timer_row = TimerRow(
            self,
            timer,
            label,
            initial_time,
            initial_playstate=initial_playstate,
        )
        self.row_modules.append(timer_row)
        if keybind is not None:
            self.keybinds[keybind] = timer_row.play_pause
        return timer, timer_row

    def add_sequence(self, sequence, label, initial_playstate=True):
        sequence_row = SequenceRow(
            self, sequence, label, initial_playstate=initial_playstate
        )
        self.row_modules.append(sequence_row)
        return sequence_row

    def add_audio_trigger(self, file, callback, label, initial_playstate=True):
        audio_trigger_row = AudioTriggerRow(
            self, label, file, callback, initial_playstate=initial_playstate
        )
        self.row_modules.append(audio_trigger_row)
        return audio_trigger_row

    def on_pause(self):
        return

    def on_play(self):
        return

    def mainloop(self):
        self.root.mainloop()

    def update(self):
        # mouse position
        mouse_pos = pyautogui.position()
        self.label_mouse_pos.config(
            text=f"Mouse Position: ({mouse_pos.x}, {mouse_pos.y})"
        )

        # timer remaining times
        for row in self.row_modules:
            row.update()
        self.root.after(FRAMELENGTH, self.update)


if __name__ == "__main__":
    my_autoclicker = AutoClicker()
    my_autoclicker.add_timer(15, input_shim.rightClick, "Right Click")
    my_autoclicker.mainloop()
