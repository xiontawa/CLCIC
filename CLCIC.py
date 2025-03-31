import tkinter as tk
import time
import sys
import threading
from pynput import mouse, keyboard
import pystray
from PIL import Image, ImageDraw
from time import sleep
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Constants and initializations
IDLE_TIME = 5 * 1  # 5 seconds of inactivity triggers the popup
last_activity = time.time()
mouse_listener = None
keyboard_listener = None
tray_icon = None
exit_flag = False

# Initialize the volume control interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Mouse and Keyboard listeners for idle detection
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

# Popup dialog for check-in
def show_popup():
    popup = tk.Tk()
    popup.title("Check-In Required")

    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()

    window_width = 600
    window_height = 300
    x = (screen_width / 2) - (window_width / 2)
    y = (screen_height / 2) - (window_height / 2)

    popup.geometry(f"{window_width}x{window_height}+{int(x)}+{int(y)}")
    popup.attributes('-topmost', True)

    label = tk.Label(popup, text="Please check in at the front desk before\nusing this computer. Thank you.", font=("Arial", 20))
    label.pack(pady=50)

    def close_popup():
        popup.destroy()
        global last_activity
        last_activity = time.time()

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

# Exit program functionality
def exit_program(icon, item):
    global mouse_listener, keyboard_listener, tray_icon, exit_flag
    if mouse_listener:
        mouse_listener.stop()
        print("Mouse listener stopped.")
    if keyboard_listener:
        keyboard_listener.stop()
        print("Keyboard listener stopped.")
    if tray_icon:
        tray_icon.stop()
        print("Tray icon stopped.")
    exit_flag = True
    print("Exit flag set.")

# Tray icon creation
def create_tray_icon():
    global tray_icon
    try:
        image = Image.open("icon.png")
    except FileNotFoundError:
        image = Image.new('RGB', (16, 16), color=(128, 128, 128))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), 'App', fill='black')

    menu = (pystray.MenuItem('Exit', exit_program),)
    tray_icon = pystray.Icon("name", image, "My Application", menu)
    tray_icon.run()

# Start listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

# Start the tray icon thread
tray_thread = threading.Thread(target=create_tray_icon)
tray_thread.start()

# Main loop
try:
    while not exit_flag:
        # Check for idle time and show popup if needed
        if check_idle():
            show_popup()

        # Volume control logic (ensures volume doesn't go above 20%)
        current_volume = volume.GetMasterVolumeLevelScalar() * 100  # Get current volume as percentage
        if current_volume > 20:
            volume.SetMasterVolumeLevelScalar(0.2, None)  # Set volume to 20%

        time.sleep(1)  # Sleep for 1 second to avoid high CPU usage
except KeyboardInterrupt:
    exit_program(None, None)

sys.exit()
