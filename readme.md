# OpenVoice Voice Cloner

A Python-based voice cloning application built with **OpenVoice V2** and **MeloTTS**.

The application allows you to generate speech from text using a reference voice and supports multiple languages through a simple command-line interface. The project is designed to run on **CPU**, so a dedicated NVIDIA GPU is not required.

## Features

* Voice cloning using **OpenVoice V2**
* Text-to-speech generation using **MeloTTS**
* Multilingual support:

  * English
  * Spanish
  * French
  * Chinese
  * Japanese
  * Korean
* Voice reference extraction from an audio file
* Adjustable speech speed
* Interactive command-line interface
* CPU execution
* No dedicated graphics card required
* Automatic creation of the output directory
* Original OpenVoice demonstration resources included

## Project Structure

```text
OpenVoice-Voice-Cloner/
│
├── app.py
├── test_clone.py
├── download_checkpoints.py
├── requirements-full.txt
├── .gitignore
│
├── openvoice/
│   ├── api.py
│   ├── se_extractor.py
│   ├── models.py
│   ├── modules.py
│   └── ...
│
├── checkpoints_v2/
│   ├── converter/
│   │   ├── config.json
│   │   └── checkpoint.pth
│   │
│   └── base_speakers/
│       └── ses/
│           ├── en-au.pth
│           ├── en-br.pth
│           ├── en-default.pth
│           ├── en-india.pth
│           ├── en-newest.pth
│           ├── en-us.pth
│           ├── es.pth
│           ├── fr.pth
│           ├── jp.pth
│           ├── kr.pth
│           └── zh.pth
│
├── resources/
│   ├── demo_speaker0.mp3
│   ├── demo_speaker1.mp3
│   ├── demo_speaker2.mp3
│   ├── example_reference.mp3
│   └── ...
│
└── outputs/
```

## Requirements

The current working environment was developed and tested with:

* Windows
* Python 3.9.0
* PyTorch 1.13.1 CPU
* TorchAudio 0.13.1 CPU
* NumPy 1.22.0
* Librosa 0.9.1

A dedicated GPU is **not required** for the current version of the application.

The application automatically detects whether CUDA is available, but the current tested configuration uses CPU execution.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/pedronav17/OpenVoice-Voice-Cloner.git
cd OpenVoice-Voice-Cloner
```

### 2. Create a virtual environment

On Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install the dependencies

```powershell
python -m pip install -r requirements-full.txt
```

> The project was developed and tested with Python 3.9.0. Using the same Python version is recommended for the most predictable results.

## Checkpoints

The project requires the OpenVoice V2 converter checkpoint and MeloTTS speaker embeddings.

The repository includes the small configuration files and MeloTTS speaker embedding files required by the application.

The main OpenVoice V2 checkpoint is intentionally excluded from Git because of its size.

The file expected by the application is:

```text
checkpoints_v2/converter/checkpoint.pth
```

The included `download_checkpoints.py` script can be used to download the required OpenVoice checkpoints.

```powershell
python download_checkpoints.py
```

After downloading, verify that the following file exists:

```text
checkpoints_v2/converter/checkpoint.pth
```

## Adding a Voice Reference

The voice that will be cloned must be placed inside:

```text
resources/
```

For example:

```text
resources/
└── my_voice.mp3
```

The application scans the `resources` folder and displays the available audio files when it starts.

When running the application, you will see something similar to:

```text
Archivos de referencia disponibles:
--------------------------------------------------
1. demo_speaker0.mp3
2. demo_speaker1.mp3
3. demo_speaker2.mp3
4. example_reference.mp3
5. my_voice.mp3

Selecciona el número del audio de referencia:
```

Simply enter the number corresponding to the voice you want to use.

### Supported audio extensions

The application searches for the following file extensions:

```text
.mp3
.wav
.m4a
.flac
```

These formats are supported by the current file-selection code. The project has not necessarily been individually tested with every listed format.

## Running the Application

From the project directory:

```powershell
.\.venv\Scripts\python.exe .\app.py
```

Alternatively, if the virtual environment is activated:

```powershell
python app.py
```

The application will guide you through the process:

1. Select the reference audio.
2. Select the target language.
3. Enter the text to synthesize.
4. Set the speech speed.
5. Extract the reference voice characteristics.
6. Generate the base speech with MeloTTS.
7. Apply the cloned voice using OpenVoice V2.

## Output Files

Generated audio files are stored in:

```text
outputs/
```

The application automatically creates this directory if it does not already exist.

The final cloned voice is generated as:

```text
outputs/voice_cloned.wav
```

A temporary intermediate file is also created:

```text
outputs/tmp.wav
```

The `outputs/` directory is excluded from Git because generated audio files are local results and should not be committed to the repository.

## Testing

The project also includes:

```text
test_clone.py
```

This script provides a simple fixed test configuration and can be used to verify that the OpenVoice V2 voice conversion pipeline is working correctly.

Run it with:

```powershell
.\.venv\Scripts\python.exe .\test_clone.py
```

The test uses a predefined reference audio file and generates the result in:

```text
outputs/voice_cloned.wav
```

## CPU Execution

One of the goals of this project is to provide a practical voice cloning setup that can run without a dedicated graphics card.

The tested environment uses:

```text
Device: CPU
PyTorch: 1.13.1+cpu
```

This makes the project suitable for computers without an NVIDIA GPU, although processing times can be significantly longer than on systems with compatible GPU acceleration.

## Important Notes

* The project has been developed and tested on Windows.
* Python 3.9.0 is the version used during development.
* CPU execution is supported and was the primary tested configuration.
* Processing time depends on the computer hardware and the length of the reference audio and generated text.
* The `outputs/` and `processed/` directories are generated locally and are excluded from version control.
* Personal voice recordings should not be committed to the repository.

## Original OpenVoice Resources

The project retains the original demonstration resources distributed with OpenVoice inside the `resources/` directory.

These include demonstration audio files and documentation/illustration assets used by the original project.

## Project Status

**Working prototype**

The current version successfully performs:

```text
Reference Audio
       │
       ▼
Voice Feature Extraction
       │
       ▼
MeloTTS Text-to-Speech
       │
       ▼
OpenVoice V2 Voice Conversion
       │
       ▼
Generated WAV Audio
```

The next stage of development is to improve the user interface and make the application easier to use without requiring command-line interaction.
