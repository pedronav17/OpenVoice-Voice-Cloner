import os
import gradio as gr

from app import clone_voice, get_reference_files, RESOURCES_DIR


# ============================================================
# CONFIGURACIÓN
# ============================================================

APP_TITLE = "OpenVoice Voice Cloner"

LANGUAGES = {
    "English": "EN",
    "Spanish": "ES",
    "French": "FR",
    "Chinese": "ZH",
    "Japanese": "JP",
}


# ============================================================
# FUNCIONES
# ============================================================

def get_audio_choices():
    """
    Get the available audio files from resources/.
    """

    files = get_reference_files()

    return files


def generate_voice(
    uploaded_audio,
    selected_audio,
    language_name,
    text,
    speed,
):
    """
    Run the app.py cloning engine.
    """

    try:

        # ----------------------------------------------------
        # Determinar audio de referencia
        # ----------------------------------------------------

        reference_audio = None

        # Si el usuario subió un archivo, tiene prioridad.
        if uploaded_audio:

            reference_audio = uploaded_audio

        # Si no subió archivo, utilizar el seleccionado.
        elif selected_audio:

            reference_audio = os.path.join(
                RESOURCES_DIR,
                selected_audio
            )

        else:

            raise ValueError(
                "Select a reference audio file or upload a new one."
            )

        # ----------------------------------------------------
        # Validar texto
        # ----------------------------------------------------

        if not text or not text.strip():

            raise ValueError(
                "Enter the text you want to convert to speech."
            )

        # ----------------------------------------------------
        # Idioma
        # ----------------------------------------------------

        language = LANGUAGES.get(language_name)

        if not language:

            raise ValueError(
                "Please select a valid language."
            )

        # ----------------------------------------------------
        # Velocidad
        # ----------------------------------------------------

        speed = float(speed)

        if speed <= 0:

            raise ValueError(
                "The speed must be greater than 0."
            )

        # ----------------------------------------------------
        # Generar nombre de salida
        # ----------------------------------------------------

        output_filename = "voice_cloned.wav"

        # ----------------------------------------------------
        # Ejecutar motor
        # ----------------------------------------------------

        output_audio = clone_voice(
            reference_speaker=reference_audio,
            language=language,
            text=text,
            speed=speed,
            output_filename=output_filename,
        )

        return (
            output_audio,
            f"✓ Generation completed successfully.\n\n"
            f"Archivo: {os.path.basename(output_audio)}"
        )

    except Exception as e:

        return (
            None,
            f"❌ Error:\n\n{str(e)}"
        )


def refresh_audio_list():
    """
    Update the list of available audio files.
    """

    return gr.update(
        choices=get_audio_choices()
    )


# ============================================================
# CSS
# ============================================================

CUSTOM_CSS = """
body {
    background: #f5f6f8;
}

.gradio-container {
    max-width: 1180px !important;
    margin: 0 auto !important;
    padding: 25px 20px 40px !important;
}

#main-header {
    text-align: center;
    margin-bottom: 25px;
}

#main-header h1 {
    font-size: 34px;
    margin-bottom: 6px;
    font-weight: 700;
}

#main-header p {
    font-size: 15px;
    color: #6b7280;
    margin-top: 0;
}

.card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 22px;
    box-shadow: 0 3px 12px rgba(0, 0, 0, 0.05);
}

.section-title {
    font-size: 19px;
    font-weight: 600;
    margin-bottom: 4px;
}

.section-description {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 16px;
}

#generate-button {
    margin-top: 12px;
}

#result-box {
    min-height: 130px;
}

footer {
    display: none !important;
}
"""


# ============================================================
# INTERFAZ
# ============================================================

with gr.Blocks(
    title=APP_TITLE,
    css=CUSTOM_CSS,
    theme=gr.themes.Soft(),
) as interface:

    # --------------------------------------------------------
    # CABECERA
    # --------------------------------------------------------

    gr.HTML(
        """
        <div id="main-header">
            <h1>🎙️ OpenVoice Voice Cloner</h1>
            <p>
                Voice cloning and text-to-speech powered by
                OpenVoice V2 and MeloTTS
            </p>
        </div>
        """
    )

    # --------------------------------------------------------
    # FILA PRINCIPAL
    # --------------------------------------------------------

    with gr.Row(equal_height=False):

        # ====================================================
        # COLUMNA IZQUIERDA
        # ====================================================

        with gr.Column(scale=1):

            with gr.Group(elem_classes="card"):

                gr.HTML(
                    """
                    <div class="section-title">
                        🎤 Reference Voice
                    </div>

                    <div class="section-description">
                        Select an existing reference audio or
                        upload a new recording.
                    </div>
                    """
                )

                selected_audio = gr.Dropdown(
                    choices=get_audio_choices(),
                    label="Audio available",
                    info="Files stored in resources/",
                    allow_custom_value=False,
                )

                refresh_button = gr.Button(
                    "↻ Refresh audio list",
                    size="sm",
                )

                gr.Markdown(
                    "or",
                    elem_classes="section-description"
                )

                uploaded_audio = gr.Audio(
                    label="Upload reference audio",
                    type="filepath",
                    sources=["upload", "microphone"],
                )

        # ====================================================
        # COLUMNA DERECHA
        # ====================================================

        with gr.Column(scale=1):

            with gr.Group(elem_classes="card"):

                gr.HTML(
                    """
                    <div class="section-title">
                        ⚙️ Voice Settings
                    </div>

                    <div class="section-description">
                        Configure the language and speaking speed.
                    </div>
                    """
                )

                language = gr.Dropdown(
                    choices=list(LANGUAGES.keys()),
                    value="English",
                    label="Language",
                )

                speed = gr.Slider(
                    minimum=0.5,
                    maximum=2.0,
                    value=1.0,
                    step=0.05,
                    label="Speech speed",
                    info="1.0 = normal speed",
                )

    # --------------------------------------------------------
    # TEXTO
    # --------------------------------------------------------

    with gr.Group(elem_classes="card"):

        gr.HTML(
            """
            <div class="section-title">
                📝 Text to Speech
            </div>

            <div class="section-description">
                Enter the text that will be generated using
                the cloned voice.
            </div>
            """
        )

        text = gr.Textbox(
            label="Text",
            placeholder=(
                "Write the text you want to convert into speech..."
            ),
            lines=8,
            max_lines=15,
        )

        generate_button = gr.Button(
            "🎙️ Generate Cloned Voice",
            variant="primary",
            size="lg",
            elem_id="generate-button",
        )

    # --------------------------------------------------------
    # RESULTADO
    # --------------------------------------------------------

    with gr.Group(elem_classes="card"):

        gr.HTML(
            """
            <div class="section-title">
                🔊 Generated Audio
            </div>

            <div class="section-description">
                Your cloned voice will appear here after generation.
            </div>
            """
        )

        output_audio = gr.Audio(
            label="Result",
            type="filepath",
            interactive=False,
        )

        result_message = gr.Textbox(
            label="Status",
            interactive=False,
            lines=4,
            elem_id="result-box",
        )

    # --------------------------------------------------------
    # INFORMACIÓN
    # --------------------------------------------------------

    gr.Markdown(
        """
        ---
        
        **OpenVoice V2** · MeloTTS · PyTorch

        The application runs locally on your computer.

        www.soumyonline.com.
        """
    )

    # --------------------------------------------------------
    # EVENTOS
    # --------------------------------------------------------

    refresh_button.click(
        fn=refresh_audio_list,
        inputs=None,
        outputs=selected_audio,
    )

    generate_button.click(
        fn=generate_voice,
        inputs=[
            uploaded_audio,
            selected_audio,
            language,
            text,
            speed,
        ],
        outputs=[
            output_audio,
            result_message,
        ],
    )


# ============================================================
# EJECUCIÓN
# ============================================================

if __name__ == "__main__":

    interface.launch(
        server_name="127.0.0.1",
        server_port=7860,
        inbrowser=True,
    )
