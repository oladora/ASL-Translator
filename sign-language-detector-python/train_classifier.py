import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

print("Loading the skeleton data...")

# Load the data
data_dict = pickle.load(open('./data.pickle', 'rb'))

# --- THE FIX: Fix inhomogeneous shapes ---
# We force every hand to only have 42 landmarks (the first hand detected)
fixed_data = []
for entry in data_dict['data']:
    fixed_data.append(entry[:42]) # Only take the first 42 coordinates

data = np.asarray(fixed_data)
labels = np.asarray(data_dict['labels'])

print(f"Data fixed! Total samples: {len(data)}")
print("Splitting into training and testing sets...")

# Split the data
x_train, x_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, shuffle=True, stratify=labels)

print("Training the Random Forest model...")

# Create and train
model = RandomForestClassifier()
model.fit(x_train, y_train)

# Test
y_predict = model.predict(x_test)
score = accuracy_score(y_predict, y_test)

print(f"Done! The AI model is {score * 100:.2f}% accurate!")

# Save the brain
with open('model.p', 'wb') as f:
    pickle.dump({'model': model}, f)

print("Saved successfully as 'model.p'.")