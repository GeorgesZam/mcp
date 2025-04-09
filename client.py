import streamlit as st
import tempfile
import os
from moviepy.editor import VideoFileClip
import whisper

# Personnalisation CSS pour un style type "Frabric"
st.markdown(
    """
    <style>
    /* Titre personnalisé */
    .stTitle { 
        font-size: 2.5rem; 
        font-weight: bold; 
        color: #4a90e2;
        margin-bottom: 1rem;
    }
    /* Style pour la zone de texte et boutons */
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

st.title("Frabric-Style Transcription")
st.markdown("**Chargez une vidéo** et obtenez une transcription instantanée (les interventions multiples seront traitées comme un flux continu).")

# Zone de chargement de la vidéo
uploaded_video = st.file_uploader("Uploader une vidéo", type=["mp4", "avi", "mov", "mkv"])

if uploaded_video is not None:
    # Création d’un fichier temporaire pour la vidéo
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video_file:
        temp_video_file.write(uploaded_video.read())
        temp_video_path = temp_video_file.name

    st.video(temp_video_path)

    st.info("Extraction de l'audio depuis la vidéo...")
    try:
        # Extraire l'audio avec MoviePy
        video_clip = VideoFileClip(temp_video_path)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
            audio_path = temp_audio_file.name
        video_clip.audio.write_audiofile(audio_path, logger=None)
    except Exception as e:
        st.error(f"Erreur lors de l'extraction de l'audio : {e}")
        st.stop()

    st.info("Transcription en cours (cela peut prendre quelques minutes)...")
    try:
        # Charger le modèle Whisper (utilise ici le modèle "base" pour un bon compromis vitesse/précision)
        model = whisper.load_model("base")
        result = model.transcribe(audio_path)
        transcript = result.get("text", "")
    except Exception as e:
        st.error(f"Erreur lors de la transcription : {e}")
        st.stop()

    # Nettoyer les fichiers temporaires
    os.remove(temp_video_path)
    os.remove(audio_path)

    st.success("Transcription terminée !")
    st.subheader("Transcription")
    st.text_area("Résultat :", transcript, height=300)
