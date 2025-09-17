

// ----- OCR Function -----
const imageInput = document.getElementById('imageInput');
const ocrResult = document.getElementById('ocrResult');

imageInput.addEventListener('change', () => {
    const file = imageInput.files[0];
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();

    if (["png", "jpg", "jpeg"].includes(ext)) {
        // ----- OCR for Images -----
        ocrResult.textContent = "Processing image...";
        Tesseract.recognize(file, 'eng', { logger: m => console.log(m) })
            .then(({ data: { text } }) => {
                ocrResult.textContent = text;
                userInput.value = text;
                speakFileContent(text); // 🔊 read file aloud
            });

    } else if (ext === "pdf") {
        // ----- PDF Reading -----
        ocrResult.textContent = "Processing PDF...";
        readPDF(file);

    } else if (ext === "txt") {
        // ----- Plain Text -----
        const reader = new FileReader();
        reader.onload = e => {
            ocrResult.textContent = e.target.result;

        };
        reader.readAsText(file);

    } else if (ext === "docx") {
        // ----- Word Docx -----
        ocrResult.textContent = "Processing Word document...";
        readDocx(file);

    } else {
        ocrResult.textContent = "⚠️ Unsupported file type.";
    }
});


// ----- Chat Function -----
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');
const chatBox = document.getElementById('chatBox');

const conversation = []; // store conversation history



async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    conversation.push({ sender: 'user', message: text });
    updateChat();

    try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });

        if (!response.ok) {
            // If Flask returns error status (like 500)
            const errorText = await response.text();
            conversation.push({ sender: 'ai', message: "⚠️ Error from server: " + errorText });
            updateChat();
            return;
        }

        const data = await response.json();
        const aiMessage = data.response || "⚠️ No reply received from chatbot";
        conversation.push({ sender: 'ai', message: aiMessage });
        updateChat();
        speak(aiMessage); // voice output
    } catch (err) {
        // Network / CORS / connection errors
        conversation.push({ sender: 'ai', message: "⚠️ Connection error: " + err.message });
        updateChat();
        speak(message)
    }

    userInput.value = "";
}


// Send on button click
sendBtn.addEventListener('click', sendMessage);

// Send on Enter key press
userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

function updateChat() {
    chatBox.textContent = ""; // clear
    conversation.forEach(msg => {
        const senderClass = msg.sender === 'user' ? 'user' : 'ai';
        chatBox.innerHTML += `<span class="${senderClass}">${msg.sender.toUpperCase()}: ${msg.message}</span>\n`;
    });
    chatBox.scrollTop = chatBox.scrollHeight; // scroll to bottom
}

// VOICES
let voices = [];

function loadVoices() {
    voices = speechSynthesis.getVoices();
    const voiceSelect = document.getElementById("voiceSelect");

    voiceSelect.innerHTML = "";
    voices.forEach((voice, i) => {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = voice.name + " (" + voice.lang + ")";
        voiceSelect.appendChild(option);
    });
}

speechSynthesis.onvoiceschanged = loadVoices;
// Get selected voice
function getSelectedVoice() {
    const voiceSelect = document.getElementById("voiceSelect");
    return voices[voiceSelect?.value] || null;
}

//A.I voice/Reader
function speak(text) {
   if (!text) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    const selectedVoice = getSelectedVoice();
    if (selectedVoice) utterance.voice = selectedVoice;
    utterance.rate = 1;   // speed control
    utterance.pitch = 1;  // pitch control
    speechSynthesis.speak(utterance);
}

//file reader
function speakFileContent(text) {
     if (!text) return;
    speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'en-US';
    const selectedVoice = getSelectedVoice();
    if (selectedVoice) utterance.voice = selectedVoice;
    utterance.rate = 1;
    utterance.pitch = 1;
    speechSynthesis.speak(utterance);
}


function pauseSpeech() {
    if (speechSynthesis.speaking && !speechSynthesis.paused) {
        speechSynthesis.pause();
        console.log("Speech paused");
    }
}

function resumeSpeech() {
    if (speechSynthesis.paused) {
        speechSynthesis.resume();
        console.log("Speech resumed");
    }
}

function stopSpeech() {
    if (speechSynthesis.speaking) {
        speechSynthesis.cancel();
        console.log("Speech stopped");
    }
}

function populateVoiceList() {
    voices = speechSynthesis.getVoices();
    const voiceSelect = document.getElementById("voiceSelect");
    voiceSelect.innerHTML = "";
    voices.forEach((voice, i) => {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = voice.name + " (" + voice.lang + ")";
        voiceSelect.appendChild(option);
    });
}

speechSynthesis.onvoiceschanged = populateVoiceList;

function speakFileContent(text) {
    const voiceSelect = document.getElementById("voiceSelect");
    const selectedVoice = voices[voiceSelect.value];
    const utterance = new SpeechSynthesisUtterance(text);
    if (selectedVoice) utterance.voice = selectedVoice;
    speechSynthesis.speak(utterance);
}

//PDF HANDLER
async function readPDF(file) {
    const fileReader = new FileReader();
    fileReader.onload = async function() {
        const typedarray = new Uint8Array(this.result);

        const pdf = await pdfjsLib.getDocument(typedarray).promise;
        let textContent = "";

        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const text = await page.getTextContent();
            text.items.forEach(item => {
                textContent += item.str + " ";
            });
        }

        document.getElementById("ocrResult").textContent = textContent;
speakFileContent(textContent)
    };
    fileReader.readAsArrayBuffer(file);
}

//DOCX SUPPORT

function readDocx(file) {
    const reader = new FileReader();
    reader.onload = function(event) {
        mammoth.extractRawText({ arrayBuffer: event.target.result })
            .then(function(result) {
                ocrResult.textContent = result.value;
                speakFileContent(result.value);

            })
            .catch(err => {
                ocrResult.textContent = "⚠️ Error reading DOCX: " + err;
            });
    };
    reader.readAsArrayBuffer(file);
}

