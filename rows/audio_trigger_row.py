import re
import tkinter as tk
from tkinter import ttk

from audio_trigger import AudioTrigger, DEFAULT_AUDIO_RMSE_THRESHOLD
from common import COLOR_DEBOUNCE, COLOR_OFF, COLOR_OFF_INACTIVE, COLOR_ON, COLOR_ON_INACTIVE
from .base import AutoclickerRow


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


