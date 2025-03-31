import tkinter as tk
import time
import sys
import threading
from pynput import mouse, keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Constants
IDLE_TIME = 5  # 5 seconds of inactivity triggers the popup
last_activity = time.time()
exit_flag = False
HEADPHONE_KEYWORDS = ["headphone", "headset", "earbuds", "airpods"]

# Initialize volume control interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Update activity timestamp
def update_activity():
    global last_activity
    last_activity = time.time()

# Mouse and Keyboard listeners
def on_move(x, y):
    update_activity()

def on_click(x, y, button, pressed):
    update_activity()

def on_press(key):
    update_activity()

# Check if the system is idle
def check_idle():
    return time.time() - last_activity > IDLE_TIME

# Check if headphones are plugged in
def headphones_plugged_in():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name():
            device_name = session.Process.name().lower()
            if any(keyword in device_name for keyword in HEADPHONE_KEYWORDS):
                return True
    return False

# Show the popup
def show_popup():
    popup = tk.Tk()
    popup.title("Check-In Required")

    # Center window
    window_width, window_height = 600, 300
    x = (popup.winfo_screenwidth() - window_width) // 2
    y = (popup.winfo_screenheight() - window_height) // 2
    popup.geometry(f"{window_width}x{window_height}+{x}+{y}")
    popup.attributes('-topmost', True)

    label = tk.Label(
        popup,
        text="Please check in at the front desk before\nusing this computer. Thank you.",
        font=("Arial", 20)
    )
    label.pack(pady=50)

    # Close popup and reset activity
    def close_popup():
        popup.destroy()
        update_activity()

    button = tk.Button(
        popup,
        text="I've Checked In",
        command=close_popup,
        font=("Arial", 16),
        width=20,
        height=2,
    )
    button.pack(pady=20)

    popup.protocol("WM_DELETE_WINDOW", lambda: None)
    popup.mainloop()

# Exit application gracefully
def exit_program():
    global exit_flag
    mouse_listener.stop()
    keyboard_listener.stop()
    exit_flag = True
    print("Application exiting...")
    sys.exit()

# Hotkey listener (Ctrl + Alt + Q)
def hotkey_listener():
    with keyboard.GlobalHotKeys({'<ctrl>+<alt>+q': exit_program}) as h:
        h.join()

# Start listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

# Run hotkey listener in background
hotkey_thread = threading.Thread(target=hotkey_listener, daemon=True)
hotkey_thread.start()

# Main loop
try:
    while not exit_flag:
        if check_idle():
            show_popup()

        # Limit volume only if headphones are NOT plugged in
        if not headphones_plugged_in():
            current_volume = volume.GetMasterVolumeLevelScalar() * 100
            if current_volume > 20:
                volume.SetMasterVolumeLevelScalar(0.2, None)  # Set volume to 20%

        time.sleep(1)
finally:
    exit_program()
