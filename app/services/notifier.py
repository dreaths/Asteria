import winsound
from pathlib import Path
from plyer import notification
import sys

def get_asset_path(filename: str) -> Path:  
    """Returns correct path whether running packaged or in dev."""
    if getattr(sys, 'frozen', False):
        base = Path(sys._MEIPASS)  
    else:
        base = Path(__file__).parent
    return base / "services" / filename

SOUND_PATH = get_asset_path("notificationSound.wav")       
PRIORITY_SOUND_PATH = get_asset_path("prioritySound.wav")

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