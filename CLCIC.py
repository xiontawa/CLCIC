import tkinter as tk
import time
import sys
import os
import threading
from pynput import mouse, keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import pystray
from PIL import Image, ImageDraw, ImageFont

# Constants
IDLE_TIME = 5
last_activity = time.time()
exit_flag = False
HEADPHONE_KEYWORDS = ["headphone", "headset", "earbuds", "airpods"]
tray_icon = None

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
def exit_program(icon=None, item=None):
    global exit_flag
    try:
        mouse_listener.stop()
        keyboard_listener.stop()
        if tray_icon:
            tray_icon.stop()
        exit_flag = True
        print("Application exiting...")
    except Exception as e:
        print(f"Error while exiting: {e}")
    finally:
        if icon:
            icon.stop()  # Properly stop the tray icon
        os._exit(0)  # Kill the process immediately without causing errors


# Create the system tray icon
def create_tray_icon():
    global tray_icon
    # Create a 16x16 empty icon
    from PIL import Image
    image = Image.new("RGB", (16, 16), color=(0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((2, 2), "CCC", fill=(255, 255, 255))  # Positioned slightly for centering
    
    menu = (pystray.MenuItem("Exit", exit_program),)
    tray_icon = pystray.Icon("MyApp", image, "CLCIC", menu)
    tray_icon.run()

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

# Run tray icon in a background thread
tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
tray_thread.start()

# Main loop
was_idle = False  # Track if the system was idle

try:
    while not exit_flag:
        if check_idle():
            was_idle = True  # System is idle
        
        elif was_idle:
            # User has resumed activity after being idle
            show_popup()
            was_idle = False  # Reset flag after showing the popup
        
        # Limit volume only if headphones are NOT plugged in
        if not headphones_plugged_in():
            current_volume = volume.GetMasterVolumeLevelScalar() * 100
            if current_volume > 30:
                volume.SetMasterVolumeLevelScalar(0.3, None)

        time.sleep(1)
finally:
    exit_program()
