import streamlit as st
from groq import Groq
from pydub import AudioSegment
import tempfile
import os
import math

# Configuración de la página
st.set_page_config(page_title="Grabador y Transcriptor Pro", page_icon="🎙️", layout="centered")

st.title("🎙️ Grabador y Transcriptor de Entrevistas Pro")
st.write("Graba tu entrevista en vivo o sube un archivo grabado para transcribirlo con IA.")

# Campo para la clave de acceso
api_key = st.sidebar.text_input("Clave de API de Groq:", type="password", help="Pega aquí tu clave gratuita de Groq")

# Crear pestañas de selección
tab1, tab2 = st.tabs(["🎙️ Grabar Audio Directo", "📁 Subir Archivo de Audio"])

audio_file = None

with tab1:
    st.write("Haz clic en el micrófono para iniciar la grabación:")
    recorded_audio = st.audio_input("Grabadora en vivo")
    if recorded_audio is not None:
        audio_file = recorded_audio

with tab2:
    uploaded_file = st.file_uploader("Sube tu archivo de audio (MP3, M4A, WAV)", type=["mp3", "m4a", "wav"])
    if uploaded_file is not None:
        audio_file = uploaded_file

# Si hay un audio (grabado o subido), mostramos el botón de transcripción
if audio_file is not None:
    st.audio(audio_file)
    
    if st.button("🚀 Iniciar Transcripción", type="primary"):
        if not api_key:
            st.error("Por favor, ingresa tu clave de API en el menú lateral.")
        else:
            client = Groq(api_key=api_key)
            
            with st.spinner("Preparando el audio... esto puede tardar un poco dependiendo de la duración."):
                try:
                    # Guardar el audio temporalmente
                    ext = audio_file.name.split('.')[-1] if hasattr(audio_file, 'name') else "wav"
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(audio_file.read())
                        tmp_file_path = tmp_file.name
                    
                    # Cargar el audio
                    audio = AudioSegment.from_file(tmp_file_path)
                    
                    # Definir bloques de 10 minutos
                    chunk_length_ms = 10 * 60 * 1000 
                    total_length_ms = len(audio)
                    num_chunks = math.ceil(total_length_ms / chunk_length_ms)
                    
                    full_transcript = ""
                    
                    st.info(f"Procesando audio (Dividido en {num_chunks} partes)...")
                    progress_bar = st.progress(0)
                    estado_texto = st.empty()

                    # Transcribir pedazo por pedazo
                    for i in range(num_chunks):
                        estado_texto.text(f"Transcribiendo parte {i + 1} de {num_chunks}...")
                        
                        start_time = i * chunk_length_ms
                        end_time = min((i + 1) * chunk_length_ms, total_length_ms)
                        chunk = audio[start_time:end_time]
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as chunk_file:
                            chunk.export(chunk_file.name, format="mp3")
                            chunk_file_path = chunk_file.name
                        
                        with open(chunk_file_path, "rb") as file:
                            transcription = client.audio.transcriptions.create(
                                file=(f"chunk_{i}.mp3", file.read()),
                                model="whisper-large-v3",
                                language="es",
                                response_format="text"
                            )
                            full_transcript += transcription + "\n\n"
                        
                        os.remove(chunk_file_path)
                        progress_bar.progress((i + 1) / num_chunks)
                    
                    os.remove(tmp_file_path)
                    estado_texto.text("¡Proceso finalizado!")
                    
                    st.success("¡Transcripción completada con éxito!")
                    
                    # Resultado y Descarga
                    st.text_area("Resultado de la Entrevista:", value=full_transcript, height=300)
                    st.download_button(
                        label="💾 Descargar Texto (.TXT)",
                        data=full_transcript,
                        file_name="transcripcion_entrevista.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Ocurrió un error al procesar el audio: {e}")
