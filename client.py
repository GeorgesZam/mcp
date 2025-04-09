import streamlit as st
import tempfile
import os
from moviepy.editor import VideoFileClip
import whisper

# Personnalisation CSS pour un style moderne (inspiré de Frabric)
st.markdown(
    """
    <style>
    .stTitle { 
        font-size: 2.5rem; 
        font-weight: bold; 
        color: #4a90e2;
        margin-bottom: 1rem;
    }
    .stTextArea label, .stFileUploader label {
        font-weight: bold;
        color: #333;
    }
    .stProgress>div>div {
        background-color: #4a90e2;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Transcription Vidéo - Style Frabric")
st.markdown("**Chargez une vidéo** et obtenez immédiatement sa transcription complète (traitée comme un flux continu).")

# Zone de chargement de la vidéo
uploaded_video = st.file_uploader("Choisissez une vidéo (formats: mp4, avi, mov, mkv)", type=["mp4", "avi", "mov", "mkv"])

if uploaded_video is not None:
    # Sauvegarde temporaire du fichier vidéo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(uploaded_video.read())
        temp_video_path = temp_video_file.name

    # Afficher la vidéo dans l'interface
    st.video(temp_video_path)

    st.info("Extraction de l'audio en cours...")
    try:
        # Extraction de l'audio avec MoviePy
        video_clip = VideoFileClip(temp_video_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            audio_path = temp_audio_file.name
        video_clip.audio.write_audiofile(audio_path, logger=None)
    except Exception as e:
        st.error(f"Erreur lors de l'extraction de l'audio : {e}")
        st.stop()

    st.info("Transcription de l'audio (ceci peut prendre quelques minutes)...")
    try:
        # Charger le modèle Whisper (utilisez "base" ou une autre taille en fonction de vos ressources)
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcription = result.get("text", "")
    except Exception as e:
        st.error(f"Erreur lors de la transcription : {e}")
        st.stop()

    st.success("Transcription terminée !")
    st.subheader("Transcription")
    st.text_area("Résultat :", transcription, height=300)

    # Optionnel: nettoyer les fichiers temporaires
    os.remove(temp_video_path)
    os.remove(audio_path)
