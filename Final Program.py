import os
import time
import ctypes
import threading
from datetime import datetime, timedelta
from PIL import Image
import pystray

BACKGROUND_FOLDER = "Backgrounds"
ICON_FILE = "icon.png"  # or "icon.ico"

# ------------------- Wallpaper Functions ------------------- #
def set_wallpaper(path):
    abs_path = os.path.abspath(path)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)

def parse_time(filename):
    try:
        return datetime.strptime(filename.split(".")[0], "%H-%M").time()
    except ValueError:
        return None

def get_scheduled_images():
    scheduled = []
    for file in os.listdir(BACKGROUND_FOLDER):
        if file.lower().endswith(".jpg"):
            img_time = parse_time(file)
            if img_time:
                scheduled.append((img_time, os.path.join(BACKGROUND_FOLDER, file)))
    return scheduled

def get_next_image(images):
    now = datetime.now()
    next_img = None
    min_delta = timedelta(days=2)
    for img_time, img_path in images:
        img_dt = datetime.combine(now.date(), img_time)
        if img_dt < now:
            img_dt += timedelta(days=1)
        delta = img_dt - now
        if delta < min_delta:
            min_delta = delta
            next_img = (img_dt, img_path)
    return next_img

# ------------------- Scheduler Thread ------------------- #
def wallpaper_scheduler(stop_event):
    images = get_scheduled_images()
    if not images:
        print("No valid images found in the folder.")
        return
    while not stop_event.is_set():
        next_img_dt, next_img_path = get_next_image(images)
        wait_seconds = (next_img_dt - datetime.now()).total_seconds()
        # If stop requested, break early
        if wait_seconds > 0:
            # Sleep in small intervals to allow quitting immediately
            for _ in range(int(wait_seconds)):
                if stop_event.is_set():
                    return
                time.sleep(1)
        set_wallpaper(next_img_path)

# ------------------- System Tray ------------------- #
def create_tray_icon(stop_event):
    # Load icon
    if os.path.exists("icon.ico"):
        icon_image = Image.open("icon.ico")
    else:
        icon_image = Image.open("icon.png")

    def quit_action(icon, item):
        stop_event.set()
        icon.stop()  # closes the tray icon

    menu = pystray.Menu(pystray.MenuItem("Quit", quit_action))
    tray_icon = pystray.Icon("WallpaperScheduler", icon_image, "Wallpaper Scheduler", menu)
    tray_icon.run()

# ------------------- Main ------------------- #
if __name__ == "__main__":
    stop_event = threading.Event()

    # Start scheduler thread
    scheduler_thread = threading.Thread(target=wallpaper_scheduler, args=(stop_event,), daemon=True)
    scheduler_thread.start()

    # Start tray icon (blocking)
    create_tray_icon(stop_event)
