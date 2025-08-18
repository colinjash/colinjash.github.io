import time
import os
from picamera2 import Picamera2

# Directory to save photos (create it if it doesn't exist)
save_dir = "/var/www/html/aurora_pics/"
os.makedirs(save_dir, exist_ok=True)

# Initialize camera
picam2 = Picamera2()

# Configure for high-quality stills
still_config = picam2.create_still_configuration(main={"size": (4056, 3040), "format": "RGB888"})
picam2.configure(still_config)

# Start camera
try:
    picam2.start()
    print("Camera started successfully")
    time.sleep(2)  # Allow camera to initialize
except Exception as e:
    print(f"Error starting camera: {e}")
    exit(1)

# Capture loop
try:
    while True:
        # Generate filename with timestamp
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{save_dir}latest.jpg"
        
        # Capture and save
        picam2.capture_file(filename)
        print(f"Captured {filename}")
        
        # Wait 5 seconds before next capture
        time.sleep(5)
except KeyboardInterrupt:
    print("Capture stopped by user")
finally:
    picam2.stop()
    print("Camera stopped")
