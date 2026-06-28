from winotify import Notification, audio


def fire_toast(title: str, message: str):
    toast = Notification(
        app_id="Asteria",
        title=title,
        msg=message,
        duration="short"
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()