import streamlit as st
import pandas as pd
import speech_recognition as sr
from fuzzywuzzy import fuzz
from io import BytesIO
import unidecode

# Configuration initiale
st.set_page_config(page_title="ekho - Pointage vocal", page_icon="🎤", layout="centered")
st.image("images/ekho_logo.png", width=150)
st.markdown("<h1 style='color:#0b76ff;'>ekho - Pointage vocal intelligent</h1>", unsafe_allow_html=True)

# Style CSS amélioré
st.markdown("""
<style>
    /* En-têtes de colonnes */
    th[data-testid="stColumnHeader"][aria-label*="Nom"] {
        background-color: #0b76ff !important;
        color: white !important;
    }
    th[data-testid="stColumnHeader"][aria-label*="résent"] {
        background-color: #28a745 !important;
        color: white !important;
    }
    
    /* Boutons */
    .stButton>button {
        background-color: #0b76ff !important;
        color: white !important;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
    }
    
    /* Messages d'erreur */
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Fonction améliorée de détection de colonne
def detect_nom_colonne(columns):
    colonnes_candidates = []
    for col in columns:
        col_norm = unidecode.unidecode(col).lower()
        score = 0
        if "nom" in col_norm: score += 3
        if "prenom" in col_norm: score += 3
        if "prénom" in col_norm: score += 3
        if "fullname" in col_norm: score += 2
        if "invite" in col_norm: score += 1
        if "participant" in col_norm: score += 1
        if "name" in col_norm: score += 1
        
        if score > 0:
            colonnes_candidates.append((col, score))
    
    return max(colonnes_candidates, key=lambda x: x[1])[0] if colonnes_candidates else None

# Upload de fichier
uploaded_file = st.file_uploader("📂 Importer le tableau des invités (.csv ou .xlsx)", type=["csv", "xlsx"])

if uploaded_file:
    # Lecture fichier
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
    
    # Détection colonne des noms
    nom_colonne = detect_nom_colonne(df.columns)
    
    # Interface de sélection de colonne
    if not nom_colonne:
        st.error("❌ Colonne 'Nom' non détectée automatiquement")
        nom_colonne = st.selectbox("Sélectionnez manuellement la colonne contenant les noms complets", df.columns)
    else:
        st.success(f"✅ Colonne détectée automatiquement : `{nom_colonne}`")
        if st.checkbox("Utiliser une autre colonne ?"):
            nom_colonne = st.selectbox("Sélectionnez la colonne des noms", df.columns)
    
    # Initialisation colonne Présent
    if "Présent" not in df.columns:
        df["Présent"] = "❌"
    else:
        # Convertir les valeurs existantes en format emoji
        df["Présent"] = df["Présent"].apply(lambda x: "✔️" if str(x).lower() in ["oui", "yes", "vrai", "true", "1", "✔️"] else "❌")
    
    # Affichage du tableau
    st.dataframe(df.head(10))
    
    # Contrôles de pointage
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🎙️ Démarrer l'écoute vocale", help="Cliquez puis parlez le nom de la personne"):
            st.session_state.recording = True
    with col2:
        if st.button("🔄 Réinitialiser les présences", type="secondary"):
            df["Présent"] = "❌"
            st.success("Statut de présence réinitialisé !")
            st.experimental_rerun()
    
    # Module vocal
    if st.session_state.get('recording', False):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("🎤 En écoute... Parlez maintenant (délai de 5 secondes)", icon="🔊")
            r.adjust_for_ambient_noise(source)
            
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                text = r.recognize_google(audio, language="fr-FR")
                st.success(f"🔊 Reconnaissance : **{text}**")
                
                # Normalisation du texte
                text_norm = unidecode.unidecode(text.lower().strip())
                matches = 0
                
                # Recherche de correspondances
                for i, nom in enumerate(df[nom_colonne]):
                    nom_str = str(nom)
                    nom_norm = unidecode.unidecode(nom_str.lower())
                    
                    # Comparaison fuzzy avec seuil ajustable
                    if fuzz.partial_ratio(text_norm, nom_norm) > 85:
                        df.at[i, "Présent"] = "✔️"
                        st.info(f"✅ **{nom_str}** marqué(e) présent(e)")
                        matches += 1
                
                if matches == 0:
                    st.warning("⚠️ Aucune correspondance trouvée. Essayez de prononcer le nom complet")
                else:
                    st.success(f"**{matches} personne(s)** marquée(s) présente(s) avec succès")
                
                # Mise à jour de l'affichage
                st.dataframe(df.head(10))
                st.session_state.recording = False
                
            except sr.WaitTimeoutError:
                st.error("⏱️ Délai d'écoute dépassé - Aucun son détecté")
                st.session_state.recording = False
            except sr.UnknownValueError:
                st.error("❓ Parole non reconnue - Essayez de parler plus clairement")
                st.session_state.recording = False
            except sr.RequestError as e:
                st.error(f"🔌 Erreur de connexion : {str(e)}")
                st.session_state.recording = False

    # Téléchargement
    st.divider()
    st.markdown("### 💾 Exporter la liste mise à jour")
    
    col1, col2 = st.columns(2)
    with col1:
        output_csv = BytesIO()
        df.to_csv(output_csv, index=False, encoding='utf-8')
        st.download_button(
            label="📥 Télécharger en CSV",
            data=output_csv.getvalue(),
            file_name="pointage_ekho.csv",
            mime="text/csv"
        )
    
    with col2:
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        st.download_button(
            label="📊 Télécharger en Excel",
            data=output_excel.getvalue(),
            file_name="pointage_ekho.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )