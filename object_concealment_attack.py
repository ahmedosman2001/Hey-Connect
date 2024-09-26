import os
import cv2
from ultralytics import YOLO
import supervision as sv
import numpy as np

# --- Model Setup (Download only once) ---
def setup_models():
    """Downloads the YOLO model if not already present."""
    if not os.path.exists("yolov8s-world.pt"):
        os.system("wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s-world.pt")

# Call the setup function to ensure the model is ready
setup_models()

# --- Object Concealment Attack ---
def conceal_object(image_path, target_object, noise_density):
    """
    Conceals a target object in an image by adding noise to its bounding box.

    Args:
        image_path (str): Path to the input image.
        target_object (str): Class name of the object to be concealed.
        noise_density (float): Percentage of noise to be added (0.0 to 1.0).

    Returns:
        None: Saves the modified image as "modified_image.png".
    """
    # 1. Object Detection (YOLO)
    model = YOLO("yolov8s-world.pt")
    image = cv2.imread(image_path)
    model.set_classes([target_object])  
    results = model(image)[0]
    detections = sv.Detections.from_ultralytics(results)

    # 2. Noise Generation and Application
    for box in detections.xyxy:
        x_min, y_min, x_max, y_max = map(int, box)
        bbox_width = x_max - x_min
        bbox_height = y_max - y_min

        # Generate noise
        noise = np.random.randn(bbox_height, bbox_width, 3) * 255 * noise_density

        # Add noise to the bounding box region
        image[y_min:y_max, x_min:x_max] = image[y_min:y_max, x_min:x_max] + noise.astype(np.uint8)

    # Clip pixel values to valid range (0-255)
    image = np.clip(image, 0, 255).astype(np.uint8)

    cv2.imwrite("modified_image.png", image)

# --- User Input ---
image_path = input("Enter the path to the image: ")
target_object = input("Enter the target object class name (e.g., 'person', 'dog'): ")
noise_density = float(input("Enter the noise density (0.0 to 1.0): "))

conceal_object(image_path, target_object, noise_density)
print("Modified image saved as 'modified_image.png'")