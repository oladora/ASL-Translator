import cv2
import mediapipe as mp
import math
import urllib.request
import numpy as np

print("1. Starting Capstone System (Bypass Mode)...")

# --- HELPER FUNCTION ---
def calc_dist(lm1, lm2):
    return math.hypot(lm1.x - lm2.x, lm1.y - lm2.y)

# 1. SETUP EYES (Manual Byte Stream)
url = "http://192.168.1.3:81/stream"
print(f"2. Manually connecting to {url}...")

try:
    stream = urllib.request.urlopen(url)
    print("3. Stream opened successfully! Loading AI...")
except Exception as e:
    print(f"ERROR: Could not connect to ESP32. Is it plugged in? Error: {e}")
    exit()

# 2. SETUP AI
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils
dot_spec = mp_draw.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=4)
line_spec = mp_draw.DrawingSpec(color=(255, 0, 255), thickness=2)

print("4. AI Loaded! Window opening now...")

bytes_data = bytes()

while True:
    # Read the raw data chunks from the Wi-Fi
    bytes_data += stream.read(4096)
    
    # Find the start and end of a JPEG image
    a = bytes_data.find(b'\xff\xd8')
    b = bytes_data.find(b'\xff\xd9')
    
    if a != -1 and b != -1:
        jpg = bytes_data[a:b+2]
        bytes_data = bytes_data[b+2:]
        
        # Decode the raw bytes into a picture OpenCV can use
        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
        
        if frame is not None:
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (800, 600)) 
            
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            current_letter = "..."

            if results.multi_hand_landmarks:
                for hand_lms in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS, dot_spec, line_spec)

                    lm = hand_lms.landmark
                    
                    fingers = [
                        1 if lm[8].y < lm[6].y else 0,   
                        1 if lm[12].y < lm[10].y else 0, 
                        1 if lm[16].y < lm[14].y else 0, 
                        1 if lm[20].y < lm[18].y else 0  
                    ]
                    
                    thumb_open = calc_dist(lm[4], lm[17]) > calc_dist(lm[5], lm[17])

                    if fingers == [1, 1, 1, 1]:
                        current_letter = "C" if thumb_open else "B"
                    elif fingers == [0, 1, 1, 1]:
                        current_letter = "F" if calc_dist(lm[4], lm[8]) < 0.05 else "W"
                    elif fingers == [1, 1, 1, 0]: current_letter = "W"
                    elif fingers == [1, 1, 0, 0]:
                        if lm[8].x > lm[12].x: current_letter = "R"
                        elif calc_dist(lm[8], lm[12]) < 0.05: current_letter = "U"
                        else: current_letter = "K" if lm[4].y < lm[6].y else "V"
                    elif fingers == [1, 0, 0, 0]:
                        if thumb_open: current_letter = "L"
                        else: current_letter = "X" if lm[8].y > lm[7].y else "D" 
                    elif fingers == [0, 0, 0, 1]:
                        current_letter = "Y" if thumb_open else "I" 
                    elif fingers == [0, 0, 0, 0]:
                        if thumb_open: current_letter = "A"
                        else:
                            if lm[4].y > lm[12].y: current_letter = "E" 
                            elif calc_dist(lm[4], lm[10]) < 0.06: current_letter = "N" 
                            elif calc_dist(lm[4], lm[14]) < 0.06: current_letter = "M" 
                            elif calc_dist(lm[4], lm[6]) < 0.06: current_letter = "T" 
                            else: current_letter = "S" 

                    if calc_dist(lm[4], lm[8]) < 0.05 and calc_dist(lm[4], lm[12]) < 0.05:
                        current_letter = "O"
                        
                    if abs(lm[8].x - lm[5].x) > abs(lm[8].y - lm[5].y):
                        if fingers[1] == 1: current_letter = "H"
                        elif fingers[1] == 0 and fingers[0] == 1: current_letter = "G"

            # --- UI OVERLAY ---
            overlay = frame.copy()
            cv2.rectangle(overlay, (20, 20), (350, 120), (30, 30, 30), -1)
            cv2.rectangle(overlay, (20, 20), (350, 120), (0, 215, 255), 3) 
            frame = cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)

            cv2.putText(frame, f"SIGN: {current_letter}", (42, 92), 
                        cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 0), 6)
            cv2.putText(frame, f"SIGN: {current_letter}", (40, 90), 
                        cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 3)

            cv2.imshow("ASL Detector", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'): 
                break

cv2.destroyAllWindows()