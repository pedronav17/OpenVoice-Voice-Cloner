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
        print("MODELOS DE OPENVOICE V2 NO ENCONTRADOS")
        print("=" * 60)
        print()
        print("Se ejecutará la descarga automática.")
        print()

        download_script = os.path.join(
            BASE_DIR,
            "download_checkpoints.py"
        )

        if not os.path.isfile(download_script):
            raise FileNotFoundError(
                "No se encontró download_checkpoints.py:\n"
                f"{download_script}"
            )

        result = subprocess.run(
            [sys.executable, download_script],
            cwd=BASE_DIR
        )

        if result.returncode != 0:
            raise RuntimeError(
                "La descarga de los modelos de OpenVoice V2 "
                "no se completó correctamente."
            )

    # --------------------------------------------------------
    # Comprobar nuevamente después de la descarga
    # --------------------------------------------------------

    if not os.path.isfile(checkpoint):
        raise FileNotFoundError(
            "No se encontró el checkpoint de OpenVoice V2:\n"
            f"{checkpoint}"
        )

    if not os.path.isfile(config):
        raise FileNotFoundError(
            "No se encontró config.json:\n"
            f"{config}"
        )

    print("[OK] Modelos de OpenVoice V2 disponibles.")


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
    print("Archivos de referencia disponibles:")
    print("-" * 50)

    files = get_reference_files()

    if not files:
        print("No se encontraron archivos de audio.")
        raise FileNotFoundError(
            "Coloca un archivo de audio en la carpeta resources."
        )

    for index, filename in enumerate(files, start=1):
        print(f"{index}. {filename}")

    print()

    while True:

        choice = input(
            "Selecciona el número del audio de referencia: "
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

        print("Opción no válida. Inténtalo nuevamente.")


def select_language():

    languages = {
        "1": ("EN", "English"),
        "2": ("ES", "Spanish"),
        "3": ("FR", "French"),
        "4": ("ZH", "Chinese"),
        "5": ("JP", "Japanese"),
    }

    print()
    print("Idiomas disponibles:")
    print("-" * 50)

    for key, value in languages.items():
        print(f"{key}. {value[1]}")

    print()

    while True:

        choice = input(
            "Selecciona el idioma: "
        ).strip()

        if choice in languages:
            return languages[choice]

        print("Opción no válida. Inténtalo nuevamente.")


def get_speed():

    print()
    print("Velocidad de la voz.")
    print("Ejemplo: 1.0 = normal | 1.2 = más rápida")
    print()

    while True:

        value = input(
            "Velocidad [1.0]: "
        ).strip()

        if value == "":
            return 1.0

        try:
            speed = float(value)

            if speed > 0:
                return speed

        except ValueError:
            pass

        print("Introduce un número válido.")


def get_text():

    print()
    print("Introduce el texto que quieres convertir.")
    print("Cuando termines, escribe una línea vacía.")
    print("-" * 50)

    lines = []

    while True:

        line = input()

        if line == "":
            break

        lines.append(line)

    if not lines:
        raise ValueError(
            "No se introdujo ningún texto."
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
    Genera una voz clonada utilizando MeloTTS + OpenVoice V2.

    Parámetros:
        reference_speaker:
            Ruta al archivo de audio utilizado como referencia.

        language:
            Código de idioma de MeloTTS:
            EN, ES, FR, ZH o JP.

        text:
            Texto que será convertido en voz.

        speed:
            Velocidad de generación.

        output_filename:
            Nombre del archivo WAV de salida.

    Retorna:
        Ruta absoluta del archivo generado.
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
            "No se encontró el audio de referencia:\n"
            f"{reference_speaker}"
        )

    # --------------------------------------------------------
    # Comprobar texto
    # --------------------------------------------------------

    if not text or not text.strip():

        raise ValueError(
            "No se introdujo ningún texto."
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
            f"Idioma no válido: {language}"
        )

    # --------------------------------------------------------
    # Validar velocidad
    # --------------------------------------------------------

    try:

        speed = float(speed)

    except (TypeError, ValueError):

        raise ValueError(
            "La velocidad debe ser un número válido."
        )

    if speed <= 0:

        raise ValueError(
            "La velocidad debe ser mayor que 0."
        )

    # --------------------------------------------------------
    # Importar OpenVoice y MeloTTS
    # --------------------------------------------------------

    print()
    print("[1/4] Cargando OpenVoice V2...")

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

    print("[OK] Configuración de OpenVoice cargada.")

    # --------------------------------------------------------
    # Cargar checkpoint
    # --------------------------------------------------------

    print("[INFO] Cargando checkpoint de OpenVoice V2...")

    tone_color_converter.load_ckpt(
        checkpoint_path
    )

    print("[OK] Checkpoint de OpenVoice V2 cargado.")

    # --------------------------------------------------------
    # Extraer voz de referencia
    # --------------------------------------------------------

    print()
    print("[2/4] Analizando voz de referencia...")
    print("Esto puede tardar unos segundos...")

    target_se, audio_name = se_extractor.get_se(
        reference_speaker,
        tone_color_converter,
        vad=False
    )

    print("[OK] Voz de referencia procesada.")
    print(f"Audio: {audio_name}")

    # --------------------------------------------------------
    # MeloTTS
    # --------------------------------------------------------

    print()
    print("[3/4] Generando audio base con MeloTTS...")

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
            "No se encontró el speaker embedding de MeloTTS:\n"
            f"{source_se_path}"
        )

    source_se = torch.load(
        source_se_path,
        map_location=DEVICE
    )

    print("[OK] Source SE cargado.")

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

    print("[OK] Audio base generado.")
    print(f"Archivo temporal: {temp_audio}")

    # --------------------------------------------------------
    # OpenVoice
    # --------------------------------------------------------

    print()
    print("[4/4] Aplicando la voz clonada...")

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
    print("✓ GENERACIÓN COMPLETADA")
    print("=" * 60)
    print()
    print("Archivo generado:")
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
    print("Audio seleccionado:")
    print(reference_speaker)

    # --------------------------------------------------------
    # Seleccionar idioma
    # --------------------------------------------------------

    language, language_name = select_language()

    print()
    print(f"Idioma seleccionado: {language_name}")

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

