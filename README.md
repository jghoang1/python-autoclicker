# Python Autoclicker

A small desktop input-automation application built with Python and Tkinter.

## Features

- Configurable click actions and repeating timers
- Global keyboard controls: press `` ` `` to play or pause and `End` to quit
- Mouse-position display
- Windows support through PyDirectInput and macOS support through PyAutoGUI
- Optional audio-trigger components for custom workflows

## Requirements

- Python 3.10 or later
- macOS accessibility permission or equivalent system input-control permission

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the application:

```bash
python autoclicker.py
```

## Responsible use

This project is intended for personal productivity, accessibility, and testing workflows. Use it only where automation is permitted and in accordance with the applicable software's terms and rules.

## Tech

Python, Tkinter, PyAutoGUI, Pynput, PyDirectInput, NumPy, SciPy, and PyAudio.
