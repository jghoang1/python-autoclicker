import logging
import re
import time
import tkinter as tk
import tkinter.ttk as ttk

import pyautogui
from audio_trigger import DEFAULT_AUDIO_RMSE_THRESHOLD, AudioTrigger
from common import *
from pynput.keyboard import Key, Listener
import logging
from timer_tools import Timer
from common import *
from audio_trigger import AudioTrigger, DEFAULT_AUDIO_RMSE_THRESHOLD
import re
import sys

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


class AudioTriggerRow(AutoclickerRow):
    def __init__(
        self,
        parent,
        label,
        audio_file,
        callback,
        input_idx=None,
        output_idx=None,
        initial_playstate=True,
    ) -> None:
        super().__init__(parent, label, initial_playstate)
        self.audio_file = audio_file
        self.callback = callback
        self.audio_trigger = AudioTrigger(
            audio_file, callback, input_idx, output_idx
        )
        self.p = self.audio_trigger.audio.p

        self.host_api_idx = self.p.get_default_host_api_info().get("index")

        self.input_idx = (
            input_idx
            if input_idx is not None
            else self.p.get_default_input_device_info().get("index")
        )
        self.output_idx = (
            output_idx
            if output_idx is not None
            else self.p.get_default_output_device_info().get("index")
        )
        self.input_name = self.p.get_device_info_by_index(self.input_idx).get(
            "name"
        )
        self.output_name = self.p.get_device_info_by_index(self.output_idx).get(
            "name"
        )

        self.input_devices = dict()
        self.output_devices = dict()
        self.input_names = []
        self.output_names = []
        self._refresh_device_list()

        # Col 1 : Play label
        self.play_label.config(text="Audio")

        # Col 2 : Function Label
        self.func_label = ttk.Label(self.parent.frm, text=label)
        self.func_label.grid(column=2, row=self.parent.current_row)

        # Col 3-4 : Input dropdown
        ttk.Label(self.parent.frm, text="Input :").grid(
            column=3, row=self.parent.current_row
        )
        self.input_var = tk.StringVar()
        self.input_var.trace_add("write", self._input_dropdown_callback)
        self.input_dropdown = tk.OptionMenu(
            self.parent.frm, self.input_var, *self.input_names
        )
        self.input_var.set(self.input_name)
        self.input_dropdown.grid(column=4, row=self.parent.current_row)

        # Col 5-6 : Output dropdown
        ttk.Label(self.parent.frm, text="Output :").grid(
            column=5, row=self.parent.current_row
        )
        self.output_var = tk.StringVar()
        self.output_var.set(self.output_name)
        self.output_var.trace_add("write", self._output_dropdown_callback)
        self.output_dropdown = tk.OptionMenu(
            self.parent.frm, self.output_var, *self.output_names
        )
        self.output_dropdown.grid(column=6, row=self.parent.current_row)

        # Col 7 : Error function
        self.err_var = tk.DoubleVar()
        self.err_label = ttk.Label(
            self.parent.frm, textvariable=self.err_var, width=5
        )
        self.err_label.grid(column=7, row=self.parent.current_row)

        # Col 8 : Threshold scale
        self.threshold_var = tk.IntVar()
        self.threshold_var.set(DEFAULT_AUDIO_RMSE_THRESHOLD)
        self.threshold_scale = tk.Scale(
            self.parent.frm,
            from_=40,
            to=0,
            variable=self.threshold_var,
            orient=tk.VERTICAL,
        )
        self.threshold_scale.grid(column=8, row=self.parent.current_row)

        self.parent.current_row += 1

    def _refresh_device_list(self):
        self.input_devices = self.audio_trigger.audio.get_input_devices()
        self.output_devices = self.audio_trigger.audio.get_output_devices()
        self.input_names = [
            dev.get("name") for dev in self.input_devices.values()
        ]
        for dev_name in self.input_names:
            if re.match("CABLE*", dev_name):
                self.logger.info(f"HIT: {dev_name}")
                self.input_names.insert(
                    0, self.input_names.pop(self.input_names.index(dev_name))
                )
                for idx, device in self.input_devices.items():
                    if (
                        device.get("name") == dev_name
                        and device.get("hostApi") == self.host_api_idx
                    ):
                        self.input_name = self.p.get_device_info_by_index(
                            idx
                        ).get("name")
                self._input_dropdown_callback
                break
        self.output_names = [
            dev.get("name") for dev in self.output_devices.values()
        ]
        self.logger.info(f"Input devices found: {self.input_names}")
        self.logger.info(f"Output devices found: {self.output_names}")

    def _input_dropdown_callback(self, var, index, mode):
        self.logger.info(f"New input value: {self.input_var.get()}")

        for idx, device in self.input_devices.items():
            self.logger.info(
                f"name: {device.get('name')} api: {device.get('hostApi')}"
            )
            if (
                device.get("name") == self.input_var.get()
                and device.get("hostApi") == self.host_api_idx
            ):
                self.audio_trigger.set_input_index(idx)
                break
        else:
            raise KeyError(
                f"Not found name : {self.input_var.get()}. hostApi: {self.host_api_idx}"
            )

    def _output_dropdown_callback(self, var, index, mode):
        self.logger.info(f"New output value: {self.output_var.get()}")

        for idx, device in self.output_devices.items():
            self.logger.info(
                f"name: {device.get('name')} api: {device.get('hostApi')}"
            )
            if (
                device.get("name") == self.output_var.get()
                and device.get("hostApi") == self.host_api_idx
            ):
                self.audio_trigger.set_output_index(idx)
                break
        else:
            raise KeyError(
                f"Not found name : {self.output_var.get()}. hostApi: {self.host_api_idx}"
            )

    def play(self):
        self.audio_trigger.is_active = True

    def pause(self):
        self.audio_trigger.is_active = False

    def update(self):
        self.audio_trigger.update()
        self.err_var.set(self.audio_trigger.err)
        self.audio_trigger.set_threshold(self.threshold_var.get())
        self.set_play_label_color()

    def get_correct_color(self):
        try:
            if self.audio_trigger.in_debounce:
                return COLOR_DEBOUNCE
        except:
            pass
        if self.is_playing:
            return COLOR_ON if self.parent.is_playing else COLOR_ON_INACTIVE
        else:
            return COLOR_OFF if self.parent.is_playing else COLOR_OFF_INACTIVE


if __name__ == "__main__":
    my_autoclicker = AutoClicker()
    my_autoclicker.add_timer(15, input_shim.rightClick, "Right Click")
    my_autoclicker.mainloop()
