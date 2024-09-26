# Hey-Connect

This project implements close-to-real-time image captioning system and two types of adversarial attacks: object concealment and object replacement. It utilizes various open-source AI models, including YOLO-world for object detection, Segment Anything Model 2 (SAM 2) for image segmentation, Stable Diffusion for image generation, and LLaVA for image captioning.

### Features

*   **Close-to-real-time Image Captioning:** Captures images and provides captions describing the scene.
*   **Speech Integration:** Includes speech-to-text (Whisper) and text-to-speech (Piper TTS) for audio interaction.
*   **Object Concealment Attack:** Strategically adds noise to target objects, concealing them from the captioning model.
*   **Object Replacement Attack:** Substitutes target objects with fabricated alternatives, generating inaccurate captions.

### Requirements

*   Python 3.7 or higher
*   CUDA-enabled GPU (recommended)
*   Picovoice Account (for wake word detection)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/Hey-Connect.git
    cd Hey-Connect
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Picovoice:**

    *   Create a free account on [Picovoice](https://picovoice.ai).
    *   Follow the Porcupine Web quick start guide ([https://picovoice.ai/docs/quick-start/porcupine-web/](https://picovoice.ai/docs/quick-start/porcupine-web/)) to obtain your Access Key
    *   Place the required files in the `static` folder of the project.
    *   Replace `${ACCESS_KEY}` in `query-based_interaction_use_case.js` with your actual Access Key.
    *   Train two wake word models, one for "start audio" and another for "stop audio". download them as base64 and replace the placeholders in `query-based_interaction_use_case.js`.

### Usage

#### 1. Image Captioning API

*   Run the Flask API:

    ```bash
    python app.py
    ```

*   The API will be accessible at `https://localhost:4000` (using SSL).

#### 2. Client Interfaces

*   Open either `passive_description_use_case.html` or `query-based_interaction_use_case.html` in a web browser.

    *   **Passive Description:** Provides continuous captions of the video feed.
    *   **Query-Based Interaction:** Allows users to ask questions about the scene using the wake words.

#### 3. Adversarial Attacks

*   Run the attack scripts from the command line:

    *   **Object Concealment:**

        ```bash
        python object_concealment_attack.py
        ```

        *   Enter the image path, target object class name, and noise density (0.0-1.0) as prompted.

    *   **Object Replacement:**

        ```bash
        python object_replacement_attack.py
        ```

        *   Enter the image path, target object class name, and a text prompt for the replacement object.

*   The modified images will be saved as "modified\_image.png".

### Examples

**Object Concealment:**

```bash
python object_concealment_attack.py
Enter the path to the image: image.jpg
Enter the target object class name: person
Enter the noise density (0.0 to 1.0): 0.7
```

**Object Replacement:**

```bash
python object_replacement_attack.py
Enter the path to the image: image.jpg
Enter the target object class name: dog
Enter the prompt for the replacement object: cat
```

### Notes

*   Ensure that your webcam and microphone are properly configured and accessible.
*   The attack scripts require a Good GPU with CUDA-enabled for optimal performance.
*   You can experiment with different prompts for the object replacement attack to achieve various results.

### Acknowledgments

This project utilizes the following open-source libraries and models:

*   YOLO-World
*   Ultralytics
*   Segment Anything Model 2 (SAM 2)
*   Stable Diffusion
*   LLaVA
*   Whisper
*   Piper TTS
*   Picovoice

