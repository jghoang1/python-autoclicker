import random
import sys
import time

import pyautogui

COLUMNS = 8
MINHEIGHT = 150
MINWIDTH = 300

COLOR_ON = "#88FF88"
COLOR_OFF = "#FF8888"
COLOR_ON_INACTIVE = "#80b080"
COLOR_OFF_INACTIVE = "#a07070"
COLOR_DEBOUNCE = "#e7eb7f"

FRAMERATE = 50
FRAMELENGTH = 1000 // 50
DEFAULT_DELAY = 0.10  # seconds


def get_input_shim():
    os_platform = sys.platform
    print(f"OS Platform (sys.platform): {os_platform}")

    input_shim = None
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
    return input_shim


INPUT_SHIM = get_input_shim()


def move_and_click(
    x: int,
    y: int,
    clicks: int = 1,
    interval: float = 0.5,
    max_dx: int = 0,
    max_dy: int = 0,
    pause_after: float = 0.1,
    duration_min: float = 0.0,
    duration_max: float = 1.0,
) -> None:
    duration = random.uniform(duration_min, duration_max)
    dx = random.randrange(-max_dx, max_dx) if max_dx else 0
    dy = random.randrange(-max_dy, max_dy) if max_dy else 0
    pyautogui.moveTo(
        x + dx, y + dy, duration=duration, tween=pyautogui.easeInOutQuad
    )
    INPUT_SHIM.click(x + dx, y + dy, clicks=clicks, interval=interval)
    time.sleep(pause_after)

def move_to(
    x: int,
    y: int,
    max_dx: int = 0,
    max_dy: int = 0,
    pause_after: float = 0.1,
    duration_min: float = 0.0,
    duration_max: float = 1.0,
) -> None:
    duration = random.uniform(duration_min, duration_max)
    dx = random.randrange(-max_dx, max_dx) if max_dx else 0
    dy = random.randrange(-max_dy, max_dy) if max_dy else 0
    pyautogui.moveTo(
        x + dx, y + dy, duration=duration, tween=pyautogui.easeInOutQuad
    )
    time.sleep(pause_after)
