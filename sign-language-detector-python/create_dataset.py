import os
import pickle
import mediapipe as mp
import cv2

print("Starting extraction... This might take a minute or two!")

# Setup MediaPipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

data = []
labels = []

# Go through every folder (0 to 25)
for dir_ in os.listdir(DATA_DIR):
    print(f"Processing Folder {dir_}...")
    folder_path = os.path.join(DATA_DIR, dir_)
    
    # Check if it's actually a directory (ignores hidden system files)
    if not os.path.isdir(folder_path):
        continue

    # Go through every picture in the folder
    for img_path in os.listdir(folder_path):
        data_aux = []
        x_ = []
        y_ = []

        img = cv2.imread(os.path.join(folder_path, img_path))
        if img is None:
            continue # Skip corrupted images

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(img_rgb)

        # If it finds a hand, extract the coordinates
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                for i in range(len(hand_landmarks.landmark)):
                    x = hand_landmarks.landmark[i].x
                    y = hand_landmarks.landmark[i].y
                    x_.append(x)
                    y_.append(y)

                # Normalize the data (makes it position-independent)
                for i in range(len(hand_landmarks.landmark)):
                    data_aux.append(hand_landmarks.landmark[i].x - min(x_))
                    data_aux.append(hand_landmarks.landmark[i].y - min(y_))

            data.append(data_aux)
            labels.append(dir_)

# Save all the extracted coordinates into a pickle file
print("Saving data to data.pickle...")
with open('data.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print("SUCCESS! data.pickle has been created.")