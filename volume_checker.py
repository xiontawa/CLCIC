from time import sleep
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Get the audio interface
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, 1, None)

# Get the current volume interface
volume = interface.QueryInterface(IAudioEndpointVolume)

while True:
    current_volume = volume.GetMasterVolumeLevelScalar() * 100  # Get current volume as percentage
    if current_volume > 20:
        volume.SetMasterVolumeLevelScalar(0.2, None)  # Set volume to 20%
    sleep(1)  # Wait for 1 second before checking again
