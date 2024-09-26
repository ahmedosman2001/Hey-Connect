import torch
import os
from PIL import Image
from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from transformers import pipeline, LlavaNextProcessor, LlavaNextForConditionalGeneration
from transformers.utils import is_flash_attn_2_available
from werkzeug.utils import secure_filename
from customTextToSpeech import Dimits
from flask_cors import CORS

# Image captioning setup
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
processor = LlavaNextProcessor.from_pretrained("llava-hf/llava-v1.6-vicuna-13b-hf")
model = LlavaNextForConditionalGeneration.from_pretrained(
    "llava-hf/llava-v1.6-vicuna-13b-hf",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    load_in_4bit=True,
)

# Speech-to-text setup
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device="cuda:0",
    model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
)

# Text-to-speech setup
dt = Dimits("en_US-amy-low")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('query-based_interaction_use_case.html')

@app.route('/auto')
def auto():
    return render_template('passive_description_use_case.html')

@app.route('/StartAudio')
def startaudio():
    print("START")
    return "Hello, Start!"

@app.route('/StoptAudio')
def stopaudio():
    print("STOP")
    return "Hello, Stop!"

@app.route("/whisper", methods=["POST"])
def whisper():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No file selected for uploading."}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        outputs = pipe(filepath, chunk_length_s=30, batch_size=30, return_timestamps=False)
        return jsonify({"message": outputs["text"]})


@app.route("/caption", methods=["POST"])
def caption():
    if 'file' not in request.files or 'text' not in request.form:
        return jsonify({"message": "Missing file or text in the request."}), 400
    
    file = request.files['file']
    prompt_text = request.form['text'] 

    if file.filename == '':
        return jsonify({"message": "No file selected for uploading."}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image = Image.open(filepath).convert("RGB")

        # Use the provided prompt_text instead of the hardcoded one
        conversation = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text}, # Dynamic prompt
                    {"type": "image"},
                ],
            },
        ]
        
        prompt = processor.apply_chat_template(conversation, add_generation_prompt=True)
        inputs = processor(images=image, text=prompt, return_tensors="pt").to("cuda:0")
        output = model.generate(**inputs, max_new_tokens=100)
        decoded_output = processor.decode(output[0], skip_special_tokens=True)

        # Extract text after "ASSISTANT:"
        assistant_index = decoded_output.find("ASSISTANT:")
        if assistant_index != -1:
            caption_text = decoded_output[assistant_index + len("ASSISTANT:"):].strip()  # Use strip() instead of trim()
        else:
            caption_text = decoded_output  # Fallback if "ASSISTANT:" is not found

        return jsonify({"message": caption_text})


@app.route("/tts", methods=["POST"])
def tts():
    if 'text' not in request.form:
        return jsonify({"message": "No text part in the request."}), 400
    text = request.form['text']
    out_bin = dt.text_2_audio_file(text, "test", "wav")  # Replace with your TTS logic
    return Response(out_bin, mimetype="audio/wav")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port="4000", debug=True, ssl_context=('ssl/server.crt', 'ssl/server.key'))


