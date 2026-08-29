import os
import gradio as gr

from app import (
    clone_voice,
    get_reference_files,
    RESOURCES_DIR,
    OUTPUT_DIR,
    DEVICE,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


LANGUAGES = {
    "English": "EN",
    "Spanish": "ES",
    "French": "FR",
    "Chinese": "ZH",
    "Japanese": "JP",
}


# ============================================================
# FUNCIONES DE LA INTERFAZ
# ============================================================

def get_audio_choices():
    """
    Obtiene los archivos de audio disponibles en resources/.
    """

    try:
        files = get_reference_files()

        return files

    except Exception:
        return []


def generate_voice(
    reference_audio,
    language_name,
    text,
    speed,
):
    """
    Ejecuta el motor de clonación definido en app.py.
    """

    # --------------------------------------------------------
    # Validar audio
    # --------------------------------------------------------

    if not reference_audio:
        raise gr.Error(
            "Selecciona un archivo de audio de referencia."
        )

    # --------------------------------------------------------
    # Resolver ruta del audio
    # --------------------------------------------------------

    # Gradio puede devolver una ruta absoluta cuando el usuario
    # sube un archivo desde la interfaz.

    if os.path.isfile(reference_audio):

        audio_path = reference_audio

    else:

        audio_path = os.path.join(
            RESOURCES_DIR,
            reference_audio
        )

    if not os.path.isfile(audio_path):

        raise gr.Error(
            f"No se encontró el archivo de audio:\n{audio_path}"
        )

    # --------------------------------------------------------
    # Validar idioma
    # --------------------------------------------------------

    if language_name not in LANGUAGES:

        raise gr.Error(
            "Selecciona un idioma válido."
        )

    language = LANGUAGES[language_name]

    # --------------------------------------------------------
    # Validar texto
    # --------------------------------------------------------

    if not text or not text.strip():

        raise gr.Error(
            "Introduce el texto que quieres convertir."
        )

    # --------------------------------------------------------
    # Validar velocidad
    # --------------------------------------------------------

    try:

        speed = float(speed)

    except (TypeError, ValueError):

        raise gr.Error(
            "La velocidad debe ser un número válido."
        )

    if speed <= 0:

        raise gr.Error(
            "La velocidad debe ser mayor que 0."
        )

    # --------------------------------------------------------
    # Generar nombre de salida
    # --------------------------------------------------------

    output_filename = "voice_cloned.wav"

    # --------------------------------------------------------
    # Ejecutar OpenVoice + MeloTTS
    # --------------------------------------------------------

    try:

        output_audio = clone_voice(
            reference_speaker=audio_path,
            language=language,
            text=text,
            speed=speed,
            output_filename=output_filename,
        )

    except Exception as error:

        print()
        print("=" * 60)
        print("ERROR DURANTE LA GENERACIÓN")
        print("=" * 60)
        print(error)
        print()

        raise gr.Error(
            f"Error durante la generación:\n{error}"
        )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    if not os.path.isfile(output_audio):

        raise gr.Error(
            "La generación terminó, pero no se encontró "
            "el archivo de audio resultante."
        )

    return output_audio


def refresh_audio_list():
    """
    Actualiza la lista de audios disponibles en resources/.
    """

    files = get_audio_choices()

    return gr.update(
        choices=files,
        value=files[0] if files else None
    )


# ============================================================
# INTERFAZ GRADIO
# ============================================================

with gr.Blocks(
    title="OpenVoice Voice Cloner"
) as interface:

    # --------------------------------------------------------
    # ENCABEZADO
    # --------------------------------------------------------

    gr.Markdown(
        """
# 🎙️ OpenVoice Voice Cloner

Genera voz utilizando **MeloTTS + OpenVoice V2**.

Selecciona un audio de referencia, elige el idioma,
introduce el texto y genera el audio con la voz clonada.
"""
    )

    # --------------------------------------------------------
    # INFORMACIÓN DEL SISTEMA
    # --------------------------------------------------------

    gr.Markdown(
        f"""
**Dispositivo:** `{DEVICE}`

Los modelos se ejecutan localmente en este ordenador.
"""
    )

    # --------------------------------------------------------
    # AUDIO DE REFERENCIA
    # --------------------------------------------------------

    gr.Markdown("## 1. Audio de referencia")

    with gr.Row():

        with gr.Column():

            audio_files = get_audio_choices()

            reference_audio = gr.Dropdown(
                choices=audio_files,
                value=audio_files[0] if audio_files else None,
                label="Selecciona un audio de resources/",
                info="Formatos compatibles: MP3, WAV, M4A y FLAC",
            )

            refresh_button = gr.Button(
                "🔄 Actualizar lista"
            )

        with gr.Column():

            uploaded_audio = gr.Audio(
                label="O subir un audio",
                type="filepath",
                sources=["upload"],
            )

    # --------------------------------------------------------
    # IDIOMA
    # --------------------------------------------------------

    gr.Markdown("## 2. Idioma")

    language = gr.Dropdown(
        choices=list(LANGUAGES.keys()),
        value="Spanish",
        label="Idioma",
    )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    gr.Markdown("## 3. Texto")

    text = gr.Textbox(
        label="Texto que quieres convertir en voz",
        placeholder=(
            "Escribe aquí el texto que quieres convertir..."
        ),
        lines=8,
    )

    # --------------------------------------------------------
    # VELOCIDAD
    # --------------------------------------------------------

    gr.Markdown("## 4. Velocidad")

    speed = gr.Slider(
        minimum=0.5,
        maximum=2.0,
        value=1.0,
        step=0.05,
        label="Velocidad de la voz",
        info="1.0 = velocidad normal",
    )

    # --------------------------------------------------------
    # BOTÓN GENERAR
    # --------------------------------------------------------

    generate_button = gr.Button(
        "🎙️ GENERAR VOZ CLONADA",
        variant="primary",
        size="lg",
    )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    gr.Markdown("## 5. Resultado")

    output_audio = gr.Audio(
        label="Voz clonada",
        type="filepath",
    )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    refresh_button.click(
        fn=refresh_audio_list,
        inputs=None,
        outputs=reference_audio,
    )

    # --------------------------------------------------------
    # Generación utilizando audio de resources/
    # --------------------------------------------------------

    generate_button.click(
        fn=generate_voice,
        inputs=[
            reference_audio,
            language,
            text,
            speed,
        ],
        outputs=output_audio,
    )



# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("        OPENVOICE VOICE CLONER - WEB INTERFACE")
    print("=" * 60)
    print()
    print(f"Device: {DEVICE}")
    print()
    print("Iniciando servidor Gradio...")
    print()
    
    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
    )

