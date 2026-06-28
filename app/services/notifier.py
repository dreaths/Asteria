import winsound
from pathlib import Path
from plyer import notification

SOUND_PATH = Path(__file__).parent / "notificationSound.wav"
PRIORITY_SOUND_PATH = Path(__file__).parent / "prioritySound.wav"

def fire_toast(title: str, message: str, is_priority: bool = False):
    notification.notify(
        title=title,
        message=message,
        app_name="Asteria",
        timeout=5
    )
    sound = PRIORITY_SOUND_PATH if is_priority else SOUND_PATH
    if SOUND_PATH.exists():
        winsound.PlaySound(str(sound), winsound.SND_FILENAME)  