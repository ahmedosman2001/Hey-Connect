// Get camera and microphone
const videoElement = document.querySelector("video");

getStream()
function getStream() {
  if (window.stream) {
    window.stream.getTracks().forEach(track => {
      track.stop();
    });
  }
  navigator.mediaDevices
  .getUserMedia({ 
    video: { frameRate: { ideal: 24, max: 24 } }, // Set the desired framerate here
    audio: false 
  }) 
  .then(gotStream)
  .catch(handleError);
}

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
let displayElement = document.querySelector('#apiText');
let isRecording = false;
let previousCaptureTime = performance.now();
let frameData = []; // Array to store frame capture times and interva

async function speakMessage(text) {
  try {
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
    audio.play();
    audio.onended = captureImage(); // Call the function when the audio ends

  } catch (error) {
    console.error('Error:', error);
  }
}
function captureImage() {
  // Visualize on the canvas
  ctx.drawImage(video2, 0, 0, canvas.width, canvas.height);
  // Capture image from video tag
  ctx.drawImage(video2, 0, 0, canvas.width, canvas.height);

  // Create a FormData object to send the image
  const imageBlob = canvas.toBlob((blob) => {
    const formData = new FormData();
    formData.append('file', blob, 'image.jpg');
    formData.append('text', "Explain very briefly what you see"); // Default text
    // Send the image data to the API
    fetch('https://localhost:4000/caption', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Update image on canvas with response from API
        speakMessage(data.message);
        const img = new Image();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = data.image;
        console.log(data.message);
      })
      .catch((error) => console.error(error));
  }, 'image/jpeg');
}

// Start the process immediately
captureImage();