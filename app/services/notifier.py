import winsound
from pathlib import Path
from plyer import notification

SOUND_PATH = Path(__file__).parent / "notificationSound.wav"


def fire_toast(title: str, message: str):
    notification.notify(
        title=title,
        message=message,
        app_name="Asteria",
        timeout=5
    )

    if SOUND_PATH.exists():
        winsound.PlaySound(str(SOUND_PATH), winsound.SND_FILENAME | winsound.SND_ASYNC)