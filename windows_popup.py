import tkinter as tk
import time
from pynput import mouse, keyboard
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

IDLE_TIME = 15 * 60
MAX_VOLUME = 0.2  # 20% volume
last_activity = time.time()

def on_move(x, y):
    global last_activity
    last_activity = time.time()
    check_volume()

def on_click(x, y, button, pressed):
    global last_activity
    last_activity = time.time()
    check_volume()

def on_press(key):
    global last_activity
    last_activity = time.time()
    check_volume()

def check_idle():
    global last_activity
    current_time = time.time()
    if current_time - last_activity > IDLE_TIME:
        return True
    return False

def check_volume():
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    current_volume = volume.GetMasterVolumeLevelScalar()
    if current_volume > MAX_VOLUME:
        volume.SetMasterVolumeLevelScalar(MAX_VOLUME, None)

def show_popup():
    popup = tk.Tk()
    popup.title("Check-In Required")

    popup.attributes('-fullscreen', True)
    popup.attributes('-topmost', True)

    label = tk.Label(popup, text="Please check in at the front desk before using this computer. Thank you.", font=("Arial", 20))
    label.pack(pady=50)

    def close_popup():
        popup.destroy()
        global last_activity
        last_activity = time.time()

    button = tk.Button(popup, text="I've Checked In", command=close_popup, font=("Arial", 16))
    button.pack(pady=20)

    popup.protocol("WM_DELETE_WINDOW", lambda: None)

    popup.mainloop()

# Start listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

try:
    while True:
        if check_idle():
            show_popup()
        check_volume() # check volume every second as well.
        time.sleep(1)
except KeyboardInterrupt:
    mouse_listener.stop()
    keyboard_listener.stop()
