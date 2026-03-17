import os
import cv2
import urllib.request
import numpy as np
import time

DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

number_of_classes = 26 
dataset_size = 100    

url = "http://192.168.1.3:81/stream"
print(f"Connecting to ESP32 at {url}...")

# --- DATA COLLECTION ENGINE ---
for j in range(number_of_classes):
    if not os.path.exists(os.path.join(DATA_DIR, str(j))):
        os.makedirs(os.path.join(DATA_DIR, str(j)))

    print(f'Ready for class {j}. Press "q" to start countdown.')

    # 1. Wait for user to be ready
    stream = urllib.request.urlopen(url)
    bytes_data = bytes()
    while True:
        bytes_data += stream.read(4096)
        a, b = bytes_data.find(b'\xff\xd8'), bytes_data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]; img_array = np.frombuffer(jpg, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.putText(cv2.flip(frame, 1), 'READY? Press "Q"', (50, 50), 1, 1.5, (0, 255, 0), 2)
                cv2.imshow('Collector', cv2.flip(frame, 1))
                if cv2.waitKey(1) == ord('q'): break

    # 2. Capture photos
    counter = 0
    while counter < dataset_size:
        bytes_data += stream.read(4096)
        a, b = bytes_data.find(b'\xff\xd8'), bytes_data.find(b'\xff\xd9')
        if a != -1 and b != -1:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]; img_array = np.frombuffer(jpg, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            if frame is not None:
                cv2.imwrite(os.path.join(DATA_DIR, str(j), f'{counter}.jpg'), cv2.flip(frame, 1))
                counter += 1
                cv2.imshow('Collector', cv2.flip(frame, 1))
                cv2.waitKey(1)
                
cv2.destroyAllWindows()