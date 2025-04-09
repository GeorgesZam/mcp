import streamlit as st
import tempfile
import os
from moviepy.editor import VideoFileClip
import whisper

st.title("Transcription Vidéo en Texte")
st.write("Chargez votre vidéo et obtenez la transcription automatiquement.")

# Charge la vidéo depuis l'interface Streamlit
uploaded_video = st.file_uploader("Uploader une vidéo", type=["mp4", "avi", "mov", "mkv"])

if uploaded_video is not None:
    # Sauvegarde temporaire du fichier vidéo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as video_file:
        video_file.write(uploaded_video.read())
        video_path = video_file.name

    st.video(video_path)

    st.info("Extraction de l'audio en cours...")
    try:
        # Extraction de l'audio avec MoviePy
        video_clip = VideoFileClip(video_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as audio_file:
            audio_path = audio_file.name
        video_clip.audio.write_audiofile(audio_path, logger=None)
    except Exception as e:
        st.error(f"Erreur lors de l'extraction de l'audio : {e}")
        st.stop()

    st.info("Transcription en cours...")
    try:
        # Charger le modèle Whisper (modèle 'base')
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcription = result.get("text", "Aucune transcription produite.")
    except Exception as e:
        st.error(f"Erreur lors de la transcription : {e}")
        st.stop()

    st.success("Transcription terminée !")
    st.subheader("Texte Transcrit")
    st.text_area("Résultat :", transcription, height=300)

    # Nettoyage des fichiers temporaires
    os.remove(video_path)
    os.remove(audio_path)
