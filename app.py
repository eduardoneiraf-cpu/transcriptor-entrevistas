import streamlit as st
from groq import Groq
from pydub import AudioSegment
import tempfile
import os
import math

# Configuración de la página
st.set_page_config(page_title="Transcriptor de Entrevistas", page_icon="🎙️", layout="centered")

st.title("🎙️ Transcriptor de Entrevistas Pro")
st.write("Carga tu audio. Si es muy largo, la app lo dividirá y procesará automáticamente.")

# Campo para la clave de acceso
api_key = st.sidebar.text_input("Clave de API de Groq:", type="password", help="Pega aquí tu clave gratuita de Groq")

# Cargador de archivos
uploaded_file = st.file_uploader("Sube tu archivo de audio (MP3, M4A, WAV)", type=["mp3", "m4a", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    
    if st.button("🚀 Iniciar Transcripción", type="primary"):
        if not api_key:
            st.error("Por favor, ingresa tu clave de API en el menú lateral.")
        else:
            client = Groq(api_key=api_key)
            
            with st.spinner("Preparando el audio... esto puede tardar un poco dependiendo del tamaño."):
                try:
                    # 1. Guardar el archivo subido temporalmente para poder leerlo
                    ext = uploaded_file.name.split('.')[-1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as tmp_file:
                        tmp_file.write(uploaded_file.read())
                        tmp_file_path = tmp_file.name
                    
                    # 2. Cargar el audio para cortarlo
                    audio = AudioSegment.from_file(tmp_file_path)
                    
                    # 3. Definir cortes de 10 minutos (600,000 milisegundos)
                    chunk_length_ms = 10 * 60 * 1000 
                    total_length_ms = len(audio)
                    num_chunks = math.ceil(total_length_ms / chunk_length_ms)
                    
                    full_transcript = ""
                    
                    st.info(f"El audio se dividió en {num_chunks} partes para su procesamiento.")
                    progress_bar = st.progress(0)
                    estado_texto = st.empty()

                    # 4. Procesar cada pedazo
                    for i in range(num_chunks):
                        estado_texto.text(f"Transcribiendo parte {i + 1} de {num_chunks}...")
                        
                        start_time = i * chunk_length_ms
                        end_time = min((i + 1) * chunk_length_ms, total_length_ms)
                        chunk = audio[start_time:end_time]
                        
                        # Guardar el pedacito temporalmente en mp3
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as chunk_file:
                            chunk.export(chunk_file.name, format="mp3")
                            chunk_file_path = chunk_file.name
                        
                        # Enviar a Groq
                        with open(chunk_file_path, "rb") as file:
                            transcription = client.audio.transcriptions.create(
                                file=(f"chunk_{i}.mp3", file.read()),
                                model="whisper-large-v3",
                                language="es",
                                response_format="text"
                            )
                            full_transcript += transcription + "\n\n"
                        
                        # Limpiar el pedacito y actualizar progreso
                        os.remove(chunk_file_path)
                        progress_bar.progress((i + 1) / num_chunks)
                    
                    # Limpiar archivo original
                    os.remove(tmp_file_path)
                    estado_texto.text("¡Proceso finalizado!")
                    
                    st.success("¡Transcripción completada con éxito!")
                    
                    # Mostrar y descargar
                    st.text_area("Resultado:", value=full_transcript, height=300)
                    st.download_button(
                        label="💾 Descargar en TXT",
                        data=full_transcript,
                        file_name="transcripcion_completa.txt",
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"Ocurrió un error procesando el audio: {e}")
