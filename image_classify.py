import cv2
import requests
import torch
from transformers import AutoImageProcessor, SiglipForImageClassification
from PIL import Image
import numpy as np

# Load model and processor
model_name = "prithivMLmods/Augmented-Waste-Classifier-SigLIP2"
model = SiglipForImageClassification.from_pretrained(model_name)
processor = AutoImageProcessor.from_pretrained(model_name)

def classify_waste(image_np):
    """Classify the waste type from a numpy image array."""
    image = Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))
    inputs = processor(images=image, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax(-1).item()
    
    labels = [
        "Battery", "Biological", "Cardboard", "Clothes", "Glass",
        "Metal", "Paper", "Plastic", "Shoes", "Trash"
    ]
    return labels[predicted_class_idx]

def map_to_bin(predicted_label):
    """Map predicted label to bin type."""
    if predicted_label == "Biological":
        return "organic"
    elif predicted_label in ["Cardboard", "Glass", "Metal", "Paper", "Plastic"]:
        return "inorganic"
    else:
        # For unmatched (e.g., Battery, Clothes, Shoes, Trash), skip or handle as biomedical
        print(f"Unmatched waste: {predicted_label}. Treating as biomedical or skipping.")
        return "biomedical"  # Adjust this mapping as needed

def send_command(ip, bin_type):
    """Send HTTP command to Arduino to open the bin."""
    if bin_type is None:
        print("No bin to open.")
        return
    url = f"http://{ip}/open?bin={bin_type}"
    try:
        response = requests.get(url)
        print(f"Command sent for {bin_type} bin. Response: {response.text}")
    except Exception as e:
        print(f"Error sending command: {e}")

# Capture image from webcam
while True:
    cap = cv2.VideoCapture(1)  # 0 for default webcam
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        exit()

    print("Press 'c' to capture image, 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Failed to capture image.")
            break
        
        cv2.imshow('Webcam', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            captured_image = frame
            break
        elif key == ord('q'):
            captured_image = None
            break

    cap.release()
    cv2.destroyAllWindows()

    if captured_image is not None:
        # Classify
        predicted_label = classify_waste(captured_image)
        print(f"Predicted waste type: {predicted_label}")
        
        # Map to bin
        bin_type = map_to_bin(predicted_label)
        
        # Send command
        arduino_ip = "10.176.6.34"  # Replace with your IP
        send_command(arduino_ip, bin_type)
    else:
        print("No image captured.")