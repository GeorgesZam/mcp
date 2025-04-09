import streamlit as st
import spacy

# Titre et description de l'application
st.title("Analyse de texte avec spaCy")
st.write("Entrez un texte en français pour extraire et visualiser les entités nommées.")

# Zone de texte pour l'entrée
text = st.text_area("Votre texte :", "Entrez ici votre texte en français...")

# Bouton pour lancer l'analyse
if st.button("Analyser"):
    if text:
        try:
            # Charger le modèle spaCy en français 
            # (Assure-toi d'avoir installé le modèle en ligne de commande : python -m spacy download fr_core_news_md)
            nlp = spacy.load("fr_core_news_md")
            doc = nlp(text)
            
            # Extraction des entités nommées
            entities = [(ent.text, ent.label_) for ent in doc.ents]
            
            st.success("Analyse effectuée avec succès !")
            if entities:
                st.subheader("Entités nommées extraites :")
                # Afficher dans un tableau
                st.table(entities)
            else:
                st.info("Aucune entité nommée détectée.")
        except Exception as e:
            st.error(f"Une erreur s'est produite : {e}")
    else:
        st.warning("Veuillez entrer un texte à analyser.")
