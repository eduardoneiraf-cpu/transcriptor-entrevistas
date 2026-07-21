import streamlit as st
from groq import Groq

# Configuración de la página
st.set_page_config(page_title="Transcriptor de Entrevistas", page_icon="🎙️", layout="centered")

st.title("🎙️ Transcriptor de Entrevistas")
st.write("Carga tu audio para generar la transcripción automática usando Inteligencia Artificial.")

# Campo para la clave de acceso de la IA
api_key = st.sidebar.text_input("Clave de API de Groq:", type="password", help="Pega aquí tu clave gratuita de Groq")

# Cargador de archivos de audio
uploaded_file = st.file_uploader("Sube tu archivo de audio (MP3, M4A, WAV)", type=["mp3", "m4a", "wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format="audio/wav")
    
    if st.button("🚀 Iniciar Transcripción", type="primary"):
        if not api_key:
            st.error("Por favor, ingresa tu clave de API en el menú lateral.")
        else:
            try:
                with st.spinner("Transcribiendo entrevista... esto tomará solo unos segundos."):
                    # Inicializar el cliente de IA
                    client = Groq(api_key=api_key)
                    
                    # Enviar el audio a Whisper
                    transcription = client.audio.transcriptions.create(
                        file=(uploaded_file.name, uploaded_file.read()),
                        model="whisper-large-v3",
                        language="es",
                        response_format="text"
                    )
                    
                    st.success("¡Transcripción completada!")
                    
                    # Mostrar el texto en pantalla
                    st.text_area("Resultado:", value=transcription, height=300)
                    
                    # Botón para descargar el resultado
                    st.download_button(
                        label="💾 Descargar en TXT",
                        data=transcription,
                        file_name="transcripcion_entrevista.txt",
                        mime="text/plain"
                    )
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
