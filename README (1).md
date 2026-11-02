# AVAQ V3 — Setup and Run Guide (Windows)

This README explains how to set up AVAQ V3 from a clean Windows computer, install its Python dependencies, download the AI models, configure Sarah's Kokoro TTS, and run the assistant.

> **Important:** Follow the steps in order. Run terminal commands from the AVAQ project folder unless a step says otherwise.

## 1. What AVAQ does

AVAQ combines these components:

- **OpenCV** captures the webcam and displays the live detection window.
- **YOLO26** detects objects in the camera image.
- **OpenWakeWord** listens for the pretrained **“Hey Jarvis”** wake word.
- **Faster-Whisper** transcribes your spoken question into text.
- **Ollama + Qwen3-VL** answer the question using one current camera image and the detected object labels.
- **Kokoro TTS (Sarah voice)** speaks the answer aloud.

AVAQ does not store a rolling 150-frame buffer or an image history. It saves one current image to `avaq_live_frame.jpg` when you ask a question, then sends that image to Qwen.

## 2. Project folder structure

Create or keep this structure. The six Python files must be in the same folder:

```text
AVAQ/
├── main.py
├── config.py
├── vision.py
├── audio.py
├── assistant.py
├── tts.py
├── requirements.txt
├── README.md
├── yolo26n.pt                 # downloaded automatically by Ultralytics if absent
└── avaq_live_frame.jpg        # created/overwritten when you ask a question
```

Your Kokoro executable and its voice/model resources can remain in their existing separate folder. `config.py` must point to the correct executable.

## 3. Required software and recommended versions

Use **64-bit Windows 10 or Windows 11**.

| Software | Recommended version / requirement | Why |
|---|---|---|
| Python | **Python 3.11.x, 64-bit** | Recommended compatibility target for PyTorch, Faster-Whisper, OpenWakeWord, and ONNX Runtime |
| pip | Current version, upgraded in the setup steps | Installs Python packages |
| Git | Optional | Only needed if cloning the project from a Git repository |
| Ollama for Windows | Current stable release | Runs Qwen locally |
| Webcam and microphone | Working Windows devices | Camera input and wake-word/question audio |
| Kokoro TTS | Your existing `kokoro-tts.exe` and required model/voice files | Sarah speech output |

Downloads:
- Python: https://www.python.org/downloads/windows/
- Ollama for Windows: https://ollama.com/download/windows
- Git for Windows (optional): https://git-scm.com/download/win
- VS Code (optional): https://code.visualstudio.com/download

During Python installation, enable **Add python.exe to PATH** if the installer offers that option.

### Why Python 3.11?

This project combines several packages with compiled machine-learning dependencies. Python 3.11 64-bit is a conservative compatibility choice for Windows. Avoid using a brand-new Python release until all required wheels are available for every dependency.

## 4. Open the project folder in VS Code

1. Open VS Code.
2. Select **File → Open Folder**.
3. Select your `AVAQ` folder.
4. Open **Terminal → New Terminal**.
5. Confirm the terminal is inside the project folder:

```powershell
Get-Location
```

The displayed path should end in your `AVAQ` folder.

If you are using a different terminal, the commands below are written for **PowerShell**.

## 5. Create a virtual environment

A virtual environment keeps AVAQ's packages separate from other Python projects.

In the VS Code terminal, run:

```powershell
py -3.11 --version
```

Expected output begins with `Python 3.11`.

Create the environment:

```powershell
py -3.11 -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Your terminal prompt should now begin with `(.venv)`.

### If PowerShell blocks activation

Run this command in the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate again:

```powershell
.\.venv\Scripts\Activate.ps1
```

This changes the policy only for the current PowerShell process.

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

## 6. Create `requirements.txt`

Make sure `requirements.txt` is in the project root and contains:

```text
opencv-python
numpy
ollama
sounddevice
faster-whisper
ultralytics
openwakeword
```

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Confirm the packages can be imported:

```powershell
python -c "import cv2, numpy, ollama, sounddevice, faster_whisper, ultralytics, openwakeword; print('Python dependencies imported successfully')"
```

If installation fails, check that the virtual environment is activated and that you are using Python 3.11 64-bit.

## 7. Install and start Ollama

1. Download and install Ollama for Windows: https://ollama.com/download/windows
2. Open a new PowerShell terminal.
3. Check that Ollama is available:

```powershell
ollama --version
```

4. Download the Qwen vision-language model used by AVAQ:

```powershell
ollama pull qwen3-vl:2b-instruct
```

5. Confirm the model is installed:

```powershell
ollama list
```

The model name in the list must match `OLLAMA_MODEL` in `config.py`:

```python
OLLAMA_MODEL = "qwen3-vl:2b-instruct"
```

Ollama normally runs as a background application on Windows. If AVAQ reports that it cannot connect to Ollama, launch the Ollama application and retry.

## 8. Download the OpenWakeWord models

With the AVAQ virtual environment activated and the terminal in the project folder, run:

```powershell
python -c "import openwakeword; openwakeword.utils.download_models()"
```

AVAQ's `audio.py` requests the pretrained `hey_jarvis` wake-word model. The download command fetches OpenWakeWord's available pretrained model files.

If the wake-word model cannot be found, check that the model download completed successfully and that the code uses:

```python
Model(
    wakeword_models=["hey_jarvis"],
    inference_framework="onnx",
)
```

## 9. Check `config.py`

Open `config.py` and confirm these settings exist and match the code:

```python
# Camera
CAMERA_INDEX = 0
YOLO_CONFIDENCE = 0.40
YOLO_IMAGE_SIZE = 640

# Models
WHISPER_MODEL = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

YOLO_MODEL = "yolo26n.pt"
OLLAMA_MODEL = "qwen3-vl:2b-instruct"

# Audio
SAMPLE_RATE = 16000
BLOCK_DURATION = 0.10
MAX_RECORDING_SECONDS = 8.0
SILENCE_SECONDS = 0.8
SPEECH_THRESHOLD = 0.015
WAKEWORD_THRESHOLD = 0.5

# Image
LIVE_FRAME_PATH = BASE_DIR / "avaq_live_frame.jpg"
```

Also check the Kokoro executable path. It must point to the actual file on your computer, for example:

```python
SARAH_TTS = Path(
    r"D:\AVAQ\AVAQ_TTS\Script\kokoro-tts.exe"
)
```

Do not copy this example path blindly if your executable is stored elsewhere. Confirm the path in File Explorer.

## 10. Confirm model files and first-run downloads

- **YOLO:** `yolo26n.pt` is downloaded automatically by Ultralytics the first time `YOLO("yolo26n.pt")` runs, if it is not already available.
- **Whisper:** Faster-Whisper downloads the `base` model the first time `WhisperModel("base", ...)` is initialized.
- **Qwen:** Must be pulled with `ollama pull qwen3-vl:2b-instruct`.
- **OpenWakeWord:** Download with the command in Section 8.
- **Kokoro:** The executable and its required assets must already exist at the configured path.

First startup may take longer because model files need to download. A working internet connection is needed for these first downloads.

## 11. Run AVAQ

Every time you open a new VS Code terminal:

1. Open the AVAQ project folder.
2. Activate the virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

3. Make sure Ollama is running.
4. Start AVAQ:

```powershell
python main.py
```

### Normal operation

1. AVAQ loads the models and opens the camera window.
2. Say **“Hey Jarvis”**.
3. Pause briefly, then ask your question in English.
4. Whisper transcribes the question.
5. Qwen answers using one current camera image and YOLO's detected labels.
6. Sarah speaks the answer.
7. AVAQ returns to listening for “Hey Jarvis”.

To quit, focus the camera window and press **Q**.

## 12. Troubleshooting

### `py -3.11` is not recognized

Python 3.11 may not be installed or the Python Launcher may be unavailable. Install 64-bit Python 3.11 from https://www.python.org/downloads/windows/, then reopen the terminal.

### `Activate.ps1` is blocked

Run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### `ModuleNotFoundError`

Make sure `(.venv)` appears in the terminal prompt, then run:

```powershell
python -m pip install -r requirements.txt
```

### Camera does not open

- Close apps that may be using the webcam.
- Check that `CAMERA_INDEX = 0` is correct. If you have multiple cameras, try `1`.
- Check Windows **Settings → Privacy & security → Camera** and allow desktop apps to access the camera.

### Microphone errors or no wake-word detection

- Check Windows **Settings → Privacy & security → Microphone** and allow desktop apps to access it.
- Confirm the correct input device is selected in Windows.
- Try lowering `WAKEWORD_THRESHOLD` from `0.5` to `0.3` if “Hey Jarvis” is missed.
- Raise it to `0.6` or `0.7` if background noise triggers Avaq.
- Speak the wake word clearly, then pause before asking your question.

### Ollama connection error

Open the Ollama application and check:

```powershell
ollama list
```

If the Qwen model is missing, run:

```powershell
ollama pull qwen3-vl:2b-instruct
```

### Sarah TTS error

- Confirm `SARAH_TTS` points to the correct executable.
- Confirm Kokoro's model and voice assets are present.
- Test the executable independently using the same arguments used in `tts.py`.

### Slow response

AVAQ runs Whisper on the CPU with the `base` model and Qwen3-VL 2B through Ollama. First-run model loading can be slow. Close unnecessary applications and confirm Ollama is using the intended model.

## 13. Important notes

- AVAQ currently listens for the wake word and records the question in separate microphone streams. If your microphone driver does not allow sequential access reliably, microphone stream handling may need adjustment.
- The current wake-word and speech-recognition configuration is intended for English.
- AVAQ sends one image per question; it does not send a video or a 150-frame history.
- `avaq_live_frame.jpg` is overwritten each time a question is processed.
- Keep your TTS executable, model assets, and any credentials private. Do not commit large model files or personal camera images to a public repository.

## 14. Useful official documentation

- Python downloads: https://www.python.org/downloads/windows/
- Python virtual environments: https://docs.python.org/3.11/library/venv.html
- pip: https://pip.pypa.io/en/stable/
- OpenCV: https://opencv.org/
- Ultralytics: https://docs.ultralytics.com/
- Faster-Whisper: https://github.com/SYSTRAN/faster-whisper
- OpenWakeWord: https://github.com/dscripka/openWakeWord
- Ollama: https://ollama.com/
- Ollama model library: https://ollama.com/library
- SoundDevice: https://python-sounddevice.readthedocs.io/
