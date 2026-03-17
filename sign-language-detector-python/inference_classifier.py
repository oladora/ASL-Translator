import pickle
import cv2
import mediapipe as mp
import numpy as np
import urllib.request

# 1. LOAD THE BRAIN
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# 2. SETUP EYES (ESP32-CAM)
url = "http://192.168.1.3:81/stream"
print(f"Connecting to ESP32 at {url}...")
stream = urllib.request.urlopen(url)
bytes_data = bytes()

# 3. SETUP AI & UI
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, min_detection_confidence=0.3)

# Dictionary for all 26 letters
labels_dict = {i: chr(65 + i) for i in range(26)}

while True:
    bytes_data += stream.read(4096)
    a = bytes_data.find(b'\xff\xd8')
    b = bytes_data.find(b'\xff\xd9')
    
    if a != -1 and b != -1:
        if a < b:
            jpg = bytes_data[a:b+2]
            bytes_data = bytes_data[b+2:]
            img_array = np.frombuffer(jpg, dtype=np.uint8)
            
            if img_array.size > 0:
                frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
                
                # --- SAFETY GATE: ONLY PROCEED IF THE IMAGE IS REAL ---
                if frame is not None:
                    frame = cv2.flip(frame, 1)
                    frame = cv2.resize(frame, (800, 600))
                    
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    results = hands.process(frame_rgb)

                    prediction_text = "..."

                    if results.multi_hand_landmarks:
                        for hand_landmarks in results.multi_hand_landmarks:
                            # Draw futuristic lines
                            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(255, 255, 0), thickness=2, circle_radius=4),
                                mp_drawing.DrawingSpec(color=(255, 0, 255), thickness=2))

                            data_aux = []
                            x_ = []
                            y_ = []

                            for i in range(len(hand_landmarks.landmark)):
                                x = hand_landmarks.landmark[i].x
                                y = hand_landmarks.landmark[i].y
                                x_.append(x)
                                y_.append(y)

                            for i in range(len(hand_landmarks.landmark)):
                                data_aux.append(hand_landmarks.landmark[i].x - min(x_))
                                data_aux.append(hand_landmarks.landmark[i].y - min(y_))

                            # Only predict if we have the correct 42 coordinates
                            if len(data_aux) == 42:
                                prediction = model.predict([np.asarray(data_aux)])
                                prediction_text = labels_dict[int(prediction[0])]

                    # --- SLEEK PLM UI OVERLAY ---
                    overlay = frame.copy()
                    cv2.rectangle(overlay, (20, 20), (350, 120), (30, 30, 30), -1)
                    cv2.rectangle(overlay, (20, 20), (350, 120), (0, 215, 255), 3) 
                    frame = cv2.addWeighted(overlay, 0.75, frame, 0.25, 0)

                    cv2.putText(frame, f"SIGN: {prediction_text}", (42, 92), 
                                cv2.FONT_HERSHEY_DUPLEX, 2.0, (0, 0, 0), 6)
                    cv2.putText(frame, f"SIGN: {prediction_text}", (40, 90), 
                                cv2.FONT_HERSHEY_DUPLEX, 2.0, (255, 255, 255), 3)

                    cv2.imshow('ASL Detector', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
        else:
            bytes_data = bytes_data[a:]

cv2.destroyAllWindows()