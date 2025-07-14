import time
import json
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2

CONFIG_PATH = '/home/pi/camera_config.json'
OUTPUT_DIR = '/home/pi/photos/'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

default_config = {
    "brightness": 0.5,   # normalized (0.0 - 1.0)
    "exposure_time": None,  # microseconds or None for auto
    "analogue_gain": None,  # None for auto
    "zoom": [0.0, 0.0, 1.0, 1.0]  # (x, y, width, height)
}

if not Path(CONFIG_PATH).exists():
    with open(CONFIG_PATH, "w") as f:
        json.dump(default_config, f)

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return default_config

def set_camera_params(cam, config):
    # Brightness is not direct; use controls
    controls = {}
    if config.get("exposure_time") is not None:
        controls["ExposureTime"] = int(config["exposure_time"])
    if config.get("analogue_gain") is not None:
        controls["AnalogueGain"] = float(config["analogue_gain"])
    if controls:
        cam.set_controls(controls)
    # Set brightness via tuning gamma (not direct)
    cam.set_controls({"Brightness": float(config.get("brightness", 0.5))})
    # Set zoom (crop)
    x, y, w, h = config.get("zoom", [0.0, 0.0, 1.0, 1.0])
    cam.set_crop((x, y, w, h))

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (1920, 1080)})
    picam2.configure(config)
    picam2.start()
    try:
        while True:
            curr_config = load_config()
            set_camera_params(picam2, curr_config)
            filename = f"{OUTPUT_DIR}image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            picam2.capture_file(filename)
            print(f"Captured {filename} with {curr_config}")
            time.sleep(12)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()