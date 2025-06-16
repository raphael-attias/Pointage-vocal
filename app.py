import streamlit as st
import pandas as pd
import speech_recognition as sr
from fuzzywuzzy import fuzz
from io import BytesIO

st.set_page_config(page_title="Pointage Vocal", layout="wide")
st.title("📋 Pointage vocal des participants")

# Fonction pour trouver et marquer la présence
def marquer_presence(df, texte, seuil=80):
    texte = texte.strip()
    mots = texte.split()
    if len(mots) == 2:
        mot1, mot2 = mots
    else:
        return None, None, None

    for i, row in df.iterrows():
        nom = str(row.get('Nom', '')).strip()
        prenom = str(row.get('Prenom', '')).strip()
        combos = [f"{nom} {prenom}", f"{prenom} {nom}"]
        for combo in combos:
            score = fuzz.ratio(combo.lower(), texte.lower())
            if score >= seuil:
                df.at[i, 'Présent'] = '✔️'
                return nom, prenom, score
    return None, None, None

# Initialisation de l'état de session
if 'df' not in st.session_state:
    st.session_state.df = None

# Upload : n'initialiser que si session_state.df est vide
uploaded_file = st.file_uploader("📂 Importer le tableau Excel ou CSV", type=["xlsx", "csv"])
if uploaded_file and st.session_state.df is None:
    if uploaded_file.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    if 'Présent' not in df.columns:
        df['Présent'] = ''
    st.session_state.df = df.copy()

# Utilisation du DataFrame en session
df = st.session_state.df
if df is not None:
    # Affichage dynamique
    table_placeholder = st.empty()
    table_placeholder.dataframe(df, use_container_width=True)

    # Interface en deux colonnes
    col1, col2 = st.columns([1, 1])

    # Reconnaissance vocale
    with col1:
        if st.button("🎙️ Démarrer la reconnaissance vocale"):
            r = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎧 Parlez maintenant...")
                audio = r.listen(source)
            try:
                texte = r.recognize_google(audio, language="fr-FR")
                st.success(f"🗣️ Vous avez dit : {texte}")
                nom, prenom, score = marquer_presence(df, texte)
                if nom:
                    st.success(f"✅ {prenom} {nom} marqué(e) présent(e) (score: {score})")
                    st.session_state.df = df.copy()
                else:
                    st.error("❌ Aucun nom correspondant trouvé.")
                table_placeholder.dataframe(df, use_container_width=True)
            except sr.UnknownValueError:
                st.error("⚠️ Voix non reconnue, veuillez réessayer.")
            except sr.RequestError:
                st.error("⚠️ Erreur avec le service de reconnaissance vocale.")

    # Export du tableau
    with col2:
        output = BytesIO()
        if uploaded_file.name.lower().endswith(".csv"):
            st.session_state.df.to_csv(output, index=False)
            st.download_button(
                label="⬇️ Télécharger le CSV mis à jour",
                data=output.getvalue(),
                file_name="pointage.csv",
                mime="text/csv"
            )
        else:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                st.session_state.df.to_excel(writer, index=False)
            st.download_button(
                label="⬇️ Télécharger l'Excel mis à jour",
                data=output.getvalue(),
                file_name="pointage.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
else:
    st.info("Importe un tableau pour démarrer le pointage.")
