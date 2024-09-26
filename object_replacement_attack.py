import os
import cv2
from ultralytics import YOLO
import supervision as sv
from PIL import Image
import torch
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
from diffusers import StableDiffusionInpaintPipeline

# --- Model Setup (Download only once) ---
def setup_models():
    """Downloads and sets up models if not already present."""
    if not os.path.exists("yolov8s-world.pt"):
        os.system("wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s-world.pt") 

    if not os.path.exists("../checkpoints/sam2_hiera_large.pt"):
        os.mkdir("../checkpoints/")
        os.system("wget -P ../checkpoints/ https://dl.fbaipublicfiles.com/segment_anything_2/072824/sam2_hiera_large.pt")

    # You might need additional setup for Stable Diffusion if it's not cached locally
    # (e.g., checking for model files and downloading if necessary)

# Call the setup function to ensure models are ready
setup_models()

# --- Object Replacement Attack ---
def replace_object(image_path, target_object, replacement_object):
    """
    Replaces a target object in an image with a specified replacement object.

    Args:
        image_path (str): Path to the input image.
        target_object (str): Class name of the object to be replaced.
        replacement_object (str): Text prompt for the replacement object.

    Returns:
        None: Saves the modified image as "modified_image.png".
    """
    # 1. Object Detection (YOLO)
    model = YOLO("yolov8s-world.pt")
    image = cv2.imread(image_path)
    model.set_classes([target_object]) 
    results = model(image)[0]
    detections = sv.Detections.from_ultralytics(results)

    # 2. Segmentation (SAM2)
    sam2_checkpoint = "../checkpoints/sam2_hiera_large.pt"
    model_cfg = "sam2_hiera_l.yaml"
    sam2_model = build_sam2(model_cfg, sam2_checkpoint, device="cuda")
    predictor = SAM2ImagePredictor(sam2_model)
    input_boxes = detections.xyxy
    predictor.set_image(image)
    masks, _, _ = predictor.predict(
        point_coords=None,
        point_labels=None,
        box=input_boxes,
        multimask_output=False,
    )

    # 3. Object Replacement (Stable Diffusion)
    device = "cuda"
    pipe = StableDiffusionInpaintPipeline.from_pretrained(
        "stabilityai/stable-diffusion-2-inpainting", torch_dtype=torch.float16
    ).to(device)

    prompt = replacement_object  # Prompt for the new object
    image = Image.open(image_path)
    edited = pipe(prompt=prompt, image=image, mask_image=masks).images[0]
    edited.save("modified_image.png")

# --- User Input ---
image_path = input("Enter the path to the image: ")
target_object = input("Enter the target object class name (e.g., 'person', 'dog'): ")
replacement_object = input("Enter the prompt for the replacement object (e.g., 'cat', 'a red apple'): ")

replace_object(image_path, target_object, replacement_object)
print("Modified image saved as 'modified_image.png'") 