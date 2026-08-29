import os
import sys
import subprocess
import torch


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHECKPOINT_DIR = os.path.join(
    BASE_DIR,
    "checkpoints_v2",
    "converter"
)

SPEAKERS_DIR = os.path.join(
    BASE_DIR,
    "checkpoints_v2",
    "base_speakers",
    "ses"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

RESOURCES_DIR = os.path.join(
    BASE_DIR,
    "resources"
)

DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def check_files():

    checkpoint = os.path.join(
        CHECKPOINT_DIR,
        "checkpoint.pth"
    )

    config = os.path.join(
        CHECKPOINT_DIR,
        "config.json"
    )

    # --------------------------------------------------------
    # Si falta el checkpoint o la configuración,
    # ejecutar automáticamente el descargador.
    # --------------------------------------------------------

    if (
        not os.path.isfile(checkpoint)
        or not os.path.isfile(config)
    ):

        print()
        print("=" * 60)
        print("OPENVOICE V2 MODELS NOT FOUND")
        print("=" * 60)
        print()
        print("The automatic download will be performed.")
        print()

        download_script = os.path.join(
            BASE_DIR,
            "download_checkpoints.py"
        )

        if not os.path.isfile(download_script):
            raise FileNotFoundError(
                "download_checkpoints.py was not found:\n"
                f"{download_script}"
            )

        result = subprocess.run(
            [sys.executable, download_script],
            cwd=BASE_DIR
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Downloading the OpenVoice V2 models"
                "It was not completed correctly."
            )

    # --------------------------------------------------------
    # Comprobar nuevamente después de la descarga
    # --------------------------------------------------------

    if not os.path.isfile(checkpoint):
        raise FileNotFoundError(
            "The OpenVoice V2 checkpoint was not found:\n"
            f"{checkpoint}"
        )

    if not os.path.isfile(config):
        raise FileNotFoundError(
            "config.json was not found:\n"
            f"{config}"
        )

    print("[OK] Available OpenVoice V2 models.")


def get_reference_files():

    files = []

    if not os.path.isdir(RESOURCES_DIR):
        return files

    for filename in os.listdir(RESOURCES_DIR):

        if filename.lower().endswith(
            (".mp3", ".wav", ".m4a", ".flac")
        ):
            files.append(filename)

    files.sort()

    return files


def select_reference_audio():

    print()
    print("Reference files available:")
    print("-" * 50)

    files = get_reference_files()

    if not files:
        print("No audio files were found.")
        raise FileNotFoundError(
            "Place an audio file in the resources folder."
        )

    for index, filename in enumerate(files, start=1):
        print(f"{index}. {filename}")

    print()

    while True:

        choice = input(
            "Select the reference audio number: "
        ).strip()

        try:
            index = int(choice) - 1

            if 0 <= index < len(files):
                return os.path.join(
                    RESOURCES_DIR,
                    files[index]
                )

        except ValueError:
            pass

        print("Invalid option. Please try again.")


def select_language():

    languages = {
        "1": ("EN", "English"),
        "2": ("ES", "Spanish"),
        "3": ("FR", "French"),
        "4": ("ZH", "Chinese"),
        "5": ("JP", "Japanese"),
    }

    print()
    print("Available languages:")
    print("-" * 50)

    for key, value in languages.items():
        print(f"{key}. {value[1]}")

    print()

    while True:

        choice = input(
            "Select language:"
        ).strip()

        if choice in languages:
            return languages[choice]

        print("Invalid option. Please try again.")


def get_speed():

    print()
    print("Speech speed.")
    print("Example: 1.0 = normal | 1.2 = faster | 0.9 = slower")
    print()

    while True:

        value = input(
            "Speed [1.0]: "
        ).strip()

        if value == "":
            return 1.0

        try:
            speed = float(value)

            if speed > 0:
                return speed

        except ValueError:
            pass

        print("Enter a valid number.")


def get_text():

    print()
    print("Enter the text you want to convert.")
    print("When you're finished, press Enter twice")
    print("-" * 50)

    lines = []

    while True:

        line = input()

        if line == "":
            break

        lines.append(line)

    if not lines:
        raise ValueError(
            "No text was entered."
        )

    return "\n".join(lines)


# ============================================================
# MOTOR DE CLONACIÓN
# ============================================================

def clone_voice(
    reference_speaker,
    language,
    text,
    speed=1.0,
    output_filename="voice_cloned.wav",
):
    """
    Generate a cloned voice using MeloTTS + OpenVoice V2.

    Parameters:
        reference_speaker:
            Path to the audio file used as a reference.

        language:
            MeloTTS language code:
            EN, ES, FR, ZH o JP.

        text:
            Text that will be converted into speech.

        speed:
            Generation speed.

        output_filename:
            Output WAV file name.

    Return:
        Absolute path of the generated file.
    """

    # --------------------------------------------------------
    # Comprobar modelos
    # --------------------------------------------------------

    check_files()

    # --------------------------------------------------------
    # Comprobar audio de referencia
    # --------------------------------------------------------

    if not os.path.isfile(reference_speaker):

        raise FileNotFoundError(
            "Reference audio not found:\n"
            f"{reference_speaker}"
        )

    # --------------------------------------------------------
    # Comprobar texto
    # --------------------------------------------------------

    if not text or not text.strip():

        raise ValueError(
            "No text was entered."
        )

    # --------------------------------------------------------
    # Validar idioma
    # --------------------------------------------------------

    valid_languages = {
        "EN",
        "ES",
        "FR",
        "ZH",
        "JP",
    }

    if language not in valid_languages:

        raise ValueError(
            f"Invalid language: {language}"
        )

    # --------------------------------------------------------
    # Validar velocidad
    # --------------------------------------------------------

    try:

        speed = float(speed)

    except (TypeError, ValueError):

        raise ValueError(
            "The speed must be a valid number."
        )

    if speed <= 0:

        raise ValueError(
            "The speed must be greater than 0."
        )

    # --------------------------------------------------------
    # Importar OpenVoice y MeloTTS
    # --------------------------------------------------------

    print()
    print("[1/4] Loading OpenVoice V2...")

    from openvoice import se_extractor
    from openvoice.api import ToneColorConverter
    from melo.api import TTS

    # --------------------------------------------------------
    # Configuración OpenVoice
    # --------------------------------------------------------

    config_path = os.path.join(
        CHECKPOINT_DIR,
        "config.json"
    )

    checkpoint_path = os.path.join(
        CHECKPOINT_DIR,
        "checkpoint.pth"
    )

    tone_color_converter = ToneColorConverter(
        config_path,
        device=DEVICE
    )

    print("[OK] OpenVoice configuration loaded.")

    # --------------------------------------------------------
    # Cargar checkpoint
    # --------------------------------------------------------

    print("[INFO] Loading OpenVoice V2 checkpoint...")

    tone_color_converter.load_ckpt(
        checkpoint_path
    )

    print("[OK] OpenVoice V2 checkpoint loaded.")

    # --------------------------------------------------------
    # Extraer voz de referencia
    # --------------------------------------------------------

    print()
    print("[2/4] Analyzing reference voice...")
    print("This may take a few seconds...")

    target_se, audio_name = se_extractor.get_se(
        reference_speaker,
        tone_color_converter,
        vad=False
    )

    print("[OK] Reference voice processed.")
    print(f"Audio: {audio_name}")

    # --------------------------------------------------------
    # MeloTTS
    # --------------------------------------------------------

    print()
    print("[3/4] Generating backing track with MeloTTS...")

    model = TTS(
        language=language,
        device=DEVICE
    )

    speaker_ids = model.hps.data.spk2id

    print(f"Speakers MeloTTS: {speaker_ids}")

    # --------------------------------------------------------
    # Seleccionar speaker
    # --------------------------------------------------------

    speaker_key = list(speaker_ids.keys())[0]

    speaker_id = speaker_ids[speaker_key]

    speaker_key = speaker_key.lower().replace(
        "_",
        "-"
    )

    source_se_path = os.path.join(
        SPEAKERS_DIR,
        f"{speaker_key}.pth"
    )

    print()
    print("Source SE:")
    print(source_se_path)

    if not os.path.isfile(source_se_path):

        raise FileNotFoundError(
            "MeloTTS speaker embedding not found:\n"
            f"{source_se_path}"
        )

    source_se = torch.load(
        source_se_path,
        map_location=DEVICE
    )

    print("[OK] Source SE loaded.")

    # --------------------------------------------------------
    # Generar audio base
    # --------------------------------------------------------

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    temp_audio = os.path.join(
        OUTPUT_DIR,
        "tmp.wav"
    )

    model.tts_to_file(
        text,
        speaker_id,
        temp_audio,
        speed=speed
    )

    print("[OK] Base audio generated.")
    print(f"Temporary file: {temp_audio}")

    # --------------------------------------------------------
    # OpenVoice
    # --------------------------------------------------------

    print()
    print("[4/4] Applying the cloned voice...")

    output_audio = os.path.join(
        OUTPUT_DIR,
        output_filename
    )

    tone_color_converter.convert(
        audio_src_path=temp_audio,
        src_se=source_se,
        tgt_se=target_se,
        output_path=output_audio,
        message="@MyShell"
    )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("✓ GENERATION COMPLETED")
    print("=" * 60)
    print()
    print("File generated:")
    print(output_audio)
    print()

    return output_audio


# ============================================================
# PROGRAMA PRINCIPAL - TERMINAL
# ============================================================

def main():

    print()
    print("=" * 60)
    print("             OPENVOICE VOICE CLONER")
    print("=" * 60)
    print()

    print(f"Python : {sys.executable}")
    print(f"PyTorch: {torch.__version__}")
    print(f"Device : {DEVICE}")

    # --------------------------------------------------------
    # Seleccionar audio
    # --------------------------------------------------------

    reference_speaker = select_reference_audio()

    print()
    print("Selected audio:")
    print(reference_speaker)

    # --------------------------------------------------------
    # Seleccionar idioma
    # --------------------------------------------------------

    language, language_name = select_language()

    print()
    print(f"Selected language: {language_name}")

    # --------------------------------------------------------
    # Texto
    # --------------------------------------------------------

    text = get_text()

    # --------------------------------------------------------
    # Velocidad
    # --------------------------------------------------------

    speed = get_speed()

    # --------------------------------------------------------
    # Generar
    # --------------------------------------------------------

    clone_voice(
        reference_speaker=reference_speaker,
        language=language,
        text=text,
        speed=speed,
        output_filename="voice_cloned.wav",
    )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    main()

