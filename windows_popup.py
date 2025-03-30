import tkinter as tk
import time
from pynput import mouse, keyboard

IDLE_TIME = 15 * 60
last_activity = time.time()

def on_move(x, y):
    global last_activity
    last_activity = time.time()

def on_click(x, y, button, pressed):
    global last_activity
    last_activity = time.time()

def on_press(key):
    global last_activity
    last_activity = time.time()

def check_idle():
    global last_activity
    current_time = time.time()
    if current_time - last_activity > IDLE_TIME:
        return True
    return False

def show_popup():
    popup = tk.Tk()
    popup.title("Check-In Required")

    # Make the window full screen and on top
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

    # Disable window controls (close, minimize, etc.)
    popup.protocol("WM_DELETE_WINDOW", lambda: None) #Disables the close button.

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
        time.sleep(1)
except KeyboardInterrupt:
    mouse_listener.stop()
    keyboard_listener.stop()