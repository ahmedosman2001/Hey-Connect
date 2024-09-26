// Get camera and microphone
const videoElement = document.querySelector("video");
let text_for_imgcap = "Briefly Explain what you see";
let audioChunks = [];
let isRecording = false;
let currentSpeechUtterance = null;
let currentAPIRequest = null;
let currentAudio = null;
let pendingAPIRequests = [];


async function keywordDetectionCallback(detection) {
  console.log(`Porcupine detected keyword index: ${detection.label}`);
  if (detection.label == "modelParams") {
    const response1 = await fetch("https://localhost:4000/StartAudio");
    isRecording = true;
    cancelSpeechAndAPI();
    console.log("Recording started");
    navigator.mediaDevices
      .getUserMedia({ audio: true })
      .then((stream) => {
        mediaRecorder = new MediaRecorder(stream);
  
        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunks.push(event.data);
          }
        };
  
        mediaRecorder.onstop = () => {
          console.log('Recording stopped');
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
  
          // Create a FormData object to send the audio
          const formData = new FormData();
          formData.append('file', audioBlob, 'audio.wav');
  
          // Send the audio data to the API
          fetch('https://localhost:4000/whisper', {
            method: 'POST',
            body: formData,
          })
            .then((response) => response.json())
            .then((data) => {
              text_for_imgcap = data.message
              captureImage(); // Call captureImage after receiving audio response
  
              // Reset the mediaRecorder and audioChunks
              mediaRecorder = null;
              audioChunks = [];
            })
            .catch((error) => console.error(error));
        };
  
        mediaRecorder.start();
      })
      .catch((error) => console.error(error));
  } else {
    const response2 = await fetch("https://localhost:4000/StoptAudio");
    mediaRecorder.stop();
  }

}

async function initializePorcupine() {

  const porcupineModel = {
    publicPath: "static/my_model.pv",  
    customWritePath: "./my_model.pv",
    forceWrite: true,
  };

  const keywordModel = {
    base64: "Your base64 string",
    label: "modelParams",
  }


  const keywordModel_2 = {
    base64: "Your base64 string",
    label: "modelParams2",
  }

  
  const porcupine = await PorcupineWeb.PorcupineWorker.create(
    "${ACCESS_KEY}",
    [keywordModel, keywordModel_2],
    keywordDetectionCallback,
    porcupineModel
  );

  console.log("WebVoiceProcessor initializing. Microphone permissions requested ...");
  await window.WebVoiceProcessor.WebVoiceProcessor.subscribe(porcupine);
  console.log("WebVoiceProcessor ready and listening!");
}

initializePorcupine();
getStream()
function getStream() {
  if (window.stream) {
    window.stream.getTracks().forEach(track => {
      track.stop();
    });
  }
  navigator.mediaDevices
  .getUserMedia({ video: true, audio: false })
  .then(gotStream)
  .catch(handleError);
}


//For Mobile phone 
// function getStream() {
//   if (window.stream) {
//     window.stream.getTracks().forEach(track => {
//       track.stop();
//     });
//   }
//   navigator.mediaDevices.getUserMedia({
//     video: {
//       facingMode: { exact: 'environment' }, // 'environment' for back camera
//       width: { ideal: desiredWidth },
//       height: { ideal: desiredHeight }
//     },
//     audio: false
//   })
//     .then(gotStream)
//     .catch(handleError);
// }


function gotStream(stream) {
  window.stream = stream;
  videoElement.srcObject = stream;
}

function handleError(error) {
  console.error("Error: ", error);
}

const video2 = document.getElementById('leftVideo');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
let mediaRecorder;


// Function to speak a message using the Web Speech API
async function speakMessage(text) {
  try {
    if (isRecording) {
      console.log("checking if recording is true");
      text_for_imgcap = "Briefly Explain what you see";
      isRecording = false;
    }
    const tts_start = Date.now();
    const response = await fetch('https://localhost:4000/tts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: new URLSearchParams({
        'text': text
      })
    });
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const audioBlob = await response.blob();
    const audioUrl = URL.createObjectURL(audioBlob);
    const audio = new Audio(audioUrl);

    // Store the audio element for potential cancellation
    currentAudio = audio;

    audio.play();
  } catch (error) {
    console.error('Error:', error);
  }
}


function captureImage() {
  console.log(text_for_imgcap);

  // Capture image from video tag
  ctx.drawImage(video2, 0, 0, canvas.width, canvas.height);

  // Create a FormData object to send the image
  const imageBlob = canvas.toBlob((blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'image.jpg');
    formData.append('text', text_for_imgcap);

    // Create an XMLHttpRequest for better control
    const xhr = new XMLHttpRequest();
    const img_start = Date.now();
    xhr.open('POST', 'https://b326-34-105-8-242.ngrok-free.app/caption');

    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) { // Check for successful response
        const data = JSON.parse(xhr.responseText);
        console.log(data.message);
        speakMessage(data.message);

      } else {
        console.error("API request failed:", xhr.status);
      }
      pendingAPIRequests = pendingAPIRequests.filter(req => req !== xhr); // Remove from tracking
    };

    xhr.onerror = () => {
      console.error("API request error");
      pendingAPIRequests = pendingAPIRequests.filter(req => req !== xhr);
    };

    xhr.ontimeout = () => {
      console.error("API request timed out");
      pendingAPIRequests = pendingAPIRequests.filter(req => req !== xhr); 
    };

    pendingAPIRequests.push(xhr); // Track the request
    xhr.send(formData); 
  }, 'image/jpeg');
}



function cancelSpeechAndAPI() {
  if (currentAudio) {
    currentAudio.pause(); 
    currentAudio = null;
  } 

  // Cancel all pending API requests
  pendingAPIRequests.forEach(xhr => xhr.abort());
  pendingAPIRequests = []; 
}

