import time
from pynput import mouse, keyboard

IDLE_TIME = 15 * 60  # 15 minutes in seconds
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

# Start listeners
mouse_listener = mouse.Listener(on_move=on_move, on_click=on_click)
keyboard_listener = keyboard.Listener(on_press=on_press)

mouse_listener.start()
keyboard_listener.start()

# Main loop (for testing)
try:
    while True:
        if check_idle():
            print("Idle detected!")  # Replace with your pop-up logic later
            #Reset the activity timer after idle.
            last_activity = time.time()
        time.sleep(1)  # Check every second
except KeyboardInterrupt:
    mouse_listener.stop()
    keyboard_listener.stop()