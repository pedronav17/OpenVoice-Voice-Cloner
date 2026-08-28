import os
import sys
import wave
import torch

from openvoice import se_extractor
from openvoice.api import ToneColorConverter
from melo.api import TTS


# ============================================================
# RUTAS
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

RESOURCES_DIR = os.path.join(
    BASE_DIR,
    "resources"
)

OUTPUT_DIR = os.path.join(
    BASE_DIR,
    "outputs"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# CONFIGURACIÓN
# ============================================================

device = "cpu"

reference_speaker = os.path.join(
    RESOURCES_DIR,
    "example_reference.mp3"
)

source_se_path = os.path.join(
    SPEAKERS_DIR,
    "es.pth"
)

config_path = os.path.join(
    CHECKPOINT_DIR,
    "config.json"
)

output_path = os.path.join(
    OUTPUT_DIR,
    "voice_cloned.wav"
)

tmp_path = os.path.join(
    OUTPUT_DIR,
    "tmp.wav"
)


# ============================================================
# INFORMACIÓN
# ============================================================

print("=" * 70)
print("OPENVOICE V2 - PRUEBA DE CLONACIÓN")
print("=" * 70)

print()
print("Python:")
print(sys.executable)

print()
print("OpenVoice:")
import openvoice
print(openvoice.__file__)

print()
print("Referencia:")
print(reference_speaker)
print("Existe:", os.path.isfile(reference_speaker))

print()
print("Checkpoint:")
print(os.path.join(CHECKPOINT_DIR, "checkpoint.pth"))
print(
    "Existe:",
    os.path.isfile(
        os.path.join(CHECKPOINT_DIR, "checkpoint.pth")
    )
)

print()
print("Speaker SE:")
print(source_se_path)
print("Existe:", os.path.isfile(source_se_path))


# ============================================================
# OPENVOICE
# ============================================================

print()
print("[1/4] Cargando OpenVoice V2...")

tone_color_converter = ToneColorConverter(
    config_path,
    device=device
)

print("[OK] Configuración de OpenVoice cargada.")

checkpoint_path = os.path.join(
    CHECKPOINT_DIR,
    "checkpoint.pth"
)

print("Cargando checkpoint:")
print(checkpoint_path)

tone_color_converter.load_ckpt(
    checkpoint_path
)

print("[OK] Checkpoint de OpenVoice V2 cargado.")


# ============================================================
# EXTRAER VOZ
# ============================================================

print()
print("[2/4] Extrayendo voz de referencia...")
print("Esto puede tardar unos segundos...")

target_se, audio_name = se_extractor.get_se(
    reference_speaker,
    tone_color_converter,
    vad=False
)

print("[OK] Voz de referencia procesada.")
print("Audio:", audio_name)

# ------------------------------------------------------------
# DEBUG TARGET SE
# ------------------------------------------------------------

print()
print("========== DEBUG TARGET SE ==========")
print("Tipo:", type(target_se))
print("Shape:", target_se.shape)
print("Dtype:", target_se.dtype)
print("Device:", target_se.device)
print("MIN:", target_se.min().item())
print("MAX:", target_se.max().item())
print("MEAN:", target_se.mean().item())
print("=====================================")


# ============================================================
# MELOTTS
# ============================================================

print()
print("[3/4] Generando audio base con MeloTTS...")

language = "ES"

model = TTS(
    language=language,
    device=device
)

speaker_ids = model.hps.data.spk2id

print("Speakers MeloTTS:", speaker_ids)

speaker_id = speaker_ids["ES"]

text = (
    "Hola a todos. Esta es una prueba de mi proyecto "
    "de clonación de voz utilizando OpenVoice V2."
)

model.tts_to_file(
    text,
    speaker_id,
    tmp_path,
    speed=1.0
)

print("[OK] Audio base generado.")
print("Archivo:", tmp_path)

# ------------------------------------------------------------
# DEBUG TMP WAV
# ------------------------------------------------------------

print()
print("========== DEBUG TMP WAV ==========")
print("Existe:", os.path.isfile(tmp_path))

if os.path.isfile(tmp_path):

    print("Tamaño:", os.path.getsize(tmp_path), "bytes")

    try:
        with wave.open(tmp_path, "rb") as wav:
            print("Canales:", wav.getnchannels())
            print("Sample rate:", wav.getframerate(), "Hz")
            print("Frames:", wav.getnframes())
            print(
                "Duración:",
                wav.getnframes() / wav.getframerate(),
                "segundos"
            )

    except Exception as e:
        print("No se pudo analizar el WAV:", e)

print("===================================")


# ============================================================
# OPENVOICE CONVERSION
# ============================================================

print()
print("[4/4] Aplicando la voz clonada...")

print("Source SE:")
print(source_se_path)

source_se = torch.load(
    source_se_path,
    map_location=device
)

print("[OK] Source SE cargado.")

# ------------------------------------------------------------
# DEBUG SOURCE SE
# ------------------------------------------------------------

print()
print("========== DEBUG SOURCE SE ==========")
print("Tipo:", type(source_se))
print("Shape:", source_se.shape)
print("Dtype:", source_se.dtype)
print("Device:", source_se.device)
print("MIN:", source_se.min().item())
print("MAX:", source_se.max().item())
print("MEAN:", source_se.mean().item())
print("=====================================")


# ------------------------------------------------------------
# CONVERSIÓN
# ------------------------------------------------------------

print()
print("Ejecutando tone_color_converter.convert()...")
print("Entrada:", tmp_path)
print("Salida:", output_path)

tone_color_converter.convert(
    audio_src_path=tmp_path,
    src_se=source_se,
    tgt_se=target_se,
    output_path=output_path,
    message="@MyShell"
)

print()
print("[OK] tone_color_converter.convert() terminó.")


# ============================================================
# COMPROBAR RESULTADO
# ============================================================

print()
print("========== DEBUG OUTPUT ==========")

print("Existe:", os.path.isfile(output_path))

if os.path.isfile(output_path):

    print("Tamaño:", os.path.getsize(output_path), "bytes")

    try:

        with wave.open(output_path, "rb") as wav:

            print("Canales:", wav.getnchannels())
            print("Sample rate:", wav.getframerate(), "Hz")
            print("Frames:", wav.getnframes())

            duration = (
                wav.getnframes()
                / wav.getframerate()
            )

            print("Duración:", duration, "segundos")

            frames = wav.readframes(wav.getnframes())

            import struct

            samples = struct.unpack(
                "<" + "h" * (len(frames) // 2),
                frames
            )

            max_sample = max(abs(x) for x in samples)

            print("Máximo valor de muestra:", max_sample)

            if max_sample == 0:
                print("⚠️ RESULTADO: WAV COMPLETAMENTE SILENCIOSO")
            else:
                print("✅ RESULTADO: El WAV CONTIENE AUDIO")

    except Exception as e:

        print("No se pudo analizar el WAV:")
        print(e)

print("==================================")


# ============================================================
# FINAL
# ============================================================

print()
print("=" * 70)
print("GENERACIÓN COMPLETADA")
print("=" * 70)
print()
print("Archivo:")
print(output_path)


import inspect
from openvoice import se_extractor

print(se_extractor.__file__)
print()
print(inspect.getsource(se_extractor.get_se))