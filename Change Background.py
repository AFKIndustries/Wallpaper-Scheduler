import os
import time
import ctypes
from datetime import datetime, timedelta

BACKGROUND_FOLDER = "Backgrounds"

# Set wallpaper (Windows)
def set_wallpaper(path):
    abs_path = os.path.abspath(path)
    ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)

# Parse HH-MM from filename
def parse_time(filename):
    try:
        return datetime.strptime(filename.split(".")[0], "%H-%M").time()
    except ValueError:
        return None

# Get all images with scheduled times
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
    min_delta = timedelta(days=2)  # large initial delta

    for img_time, img_path in images:
        img_dt = datetime.combine(now.date(), img_time)
        if img_dt < now:
            img_dt += timedelta(days=1)  # schedule for next day if passed
        delta = img_dt - now
        if delta < min_delta:
            min_delta = delta
            next_img = (img_dt, img_path)
    return next_img

def main():
    images = get_scheduled_images()
    if not images:
        print("No valid images found in the folder.")
        return

    while True:
        next_img_dt, next_img_path = get_next_image(images)
        wait_seconds = (next_img_dt - datetime.now()).total_seconds()
        print(f"Next wallpaper: {next_img_path} at {next_img_dt.time()}, waiting {int(wait_seconds)} seconds")
        time.sleep(wait_seconds)
        set_wallpaper(next_img_path)

if __name__ == "__main__":
    main()


