import time
import json
from datetime import datetime
from pathlib import Path
from picamera2 import Picamera2, controls

CONFIG_PATH = '/home/pi/camera_config.json'
OUTPUT_DIR = '/home/pi/photos/'
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

default_config = {
    'brightness': 0.5,          # Picamera2 brightness is float 0.0-1.0
    'exposure_comp': 0,         # Exposure Compensation as int
    'contrast': 0,              # Integer, typical range -100 to 100
    'sharpness': 0,             # Integer, typical range -100 to 100
    'saturation': 0,            # Integer, typical range -100 to 100
    'zoom': [0.0, 0.0, 1.0, 1.0],
    'ai_enhance': False
}

def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
            for key, val in default_config.items():
                if key not in config:
                    config[key] = val
            return config
    except Exception as e:
        print(f"Failed to load config, using defaults: {e}")
        return default_config

def apply_camera_settings(picam2, config):
    # Brightness in Picamera2 is set via controls.Brightness
    # Exposure compensation is set via controls.ExposureValue or ExposureTime adjustments
    # But Picamera2 may not have direct exposure compensation; we try ExposureTime or AnalogueGain instead

    # Clamp brightness between 0.0 and 1.0
    brightness = max(0.0, min(1.0, float(config.get('brightness', 0.5))))
    picam2.set_controls({"Brightness": brightness})

    # Contrast, Sharpness, Saturation can be set if supported:
    # Some may require tuning or be unsupported depending on camera
    picam2.set_controls({
        "Contrast": int(config.get('contrast', 0)),
        "Sharpness": int(config.get('sharpness', 0)),
        "Saturation": int(config.get('saturation', 0)),
    })

    # Zoom - crop rectangle (x, y, width, height)
    zoom = config.get('zoom', [0.0, 0.0, 1.0, 1.0])
    if len(zoom) == 4:
        picam2.set_crop(tuple(zoom))

    # Exposure Compensation is tricky in Picamera2; we emulate by adjusting ExposureTime or AnalogueGain
    # Here, just a simple implementation: positive exposure_comp increases ExposureTime
    exposure_comp = int(config.get('exposure_comp', 0))
    # Basic heuristic: base exposure time is 10000us; adjust by exposure_comp * 1000us
    base_exposure_us = 10000
    exposure_time = max(100, base_exposure_us + exposure_comp * 1000)
    picam2.set_controls({"ExposureTime": exposure_time})

def main():
    picam2 = Picamera2()
    config_still = picam2.create_still_configuration(main={"size": (1920, 1080)})
    picam2.configure(config_still)
    picam2.start()
    print("Camera started. Press Ctrl+C to exit.")

    try:
        while True:
            config = load_config()
            apply_camera_settings(picam2, config)

            filename = f"{OUTPUT_DIR}image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            picam2.capture_file(filename)
            print(f"Captured {filename} with config: {config}")

            # TODO: Implement AI enhance post-processing if config['ai_enhance'] is True

            time.sleep(12)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        picam2.stop()

if __name__ == "__main__":
    main()
