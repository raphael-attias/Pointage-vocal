import streamlit as st
import pandas as pd
import speech_recognition as sr
from fuzzywuzzy import fuzz, process
from io import BytesIO
import unidecode
import re
from datetime import datetime

# Configuration initiale
st.set_page_config(page_title="ekho - Pointage vocal", page_icon="🎤", layout="wide")

# Header avec logo et titre
col1, col2 = st.columns([1, 4])
with col1:
    st.image("images/ekho_logo.png", width=120)
with col2:
    st.markdown("<h1 style='color:#0b76ff; margin-top: 20px;'>ekho - Pointage vocal intelligent</h1>", unsafe_allow_html=True)

# Style CSS amélioré
st.markdown("""
<style>
    /* En-têtes de colonnes */
    th[data-testid="stColumnHeader"] {
        background-color: #f8f9fa !important;
        color: #0b76ff !important;
        font-weight: bold;
    }
    
    /* Boutons principaux */
    .stButton>button {
        background-color: #0b76ff !important;
        color: white !important;
        border-radius: 8px;
        padding: 8px 16px;
        font-weight: bold;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #0956cc !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(11, 118, 255, 0.3);
    }
    
    /* Statistiques */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    
    /* Messages d'info */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #0b76ff;
    }
    
    /* Tableau personnalisé */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Fonctions utilitaires améliorées
def detect_colonnes_noms(columns):
    """Détecte automatiquement les colonnes nom et prénom"""
    colonnes_nom = []
    colonnes_prenom = []
    colonne_complete = None
    
    for col in columns:
        col_norm = unidecode.unidecode(col).lower()
        
        # Recherche colonne nom complet
        if any(term in col_norm for term in ["nom complet", "fullname", "nom_complet", "nomcomplet"]):
            colonne_complete = col
            break
            
        # Recherche colonne nom
        if any(term in col_norm for term in ["nom", "lastname", "surname"]) and "prenom" not in col_norm:
            colonnes_nom.append(col)
            
        # Recherche colonne prénom
        if any(term in col_norm for term in ["prenom", "prénom", "firstname", "prenom"]):
            colonnes_prenom.append(col)
    
    return {
        'complete': colonne_complete,
        'nom': colonnes_nom[0] if colonnes_nom else None,
        'prenom': colonnes_prenom[0] if colonnes_prenom else None
    }

def normaliser_texte(texte):
    """Normalise le texte pour la comparaison"""
    if pd.isna(texte):
        return ""
    texte = str(texte).strip()
    texte = unidecode.unidecode(texte.lower())
    texte = re.sub(r'[^\w\s]', '', texte)  # Supprime la ponctuation
    return texte

def rechercher_correspondance(texte_vocal, df, colonne_noms, seuil=70):
    """Recherche les correspondances avec le texte vocal - Version améliorée"""
    texte_vocal_norm = normaliser_texte(texte_vocal)
    correspondances = []
    
    # Mots du texte vocal pour recherche par mots-clés
    mots_vocal = texte_vocal_norm.split()
    
    for i, nom in enumerate(df[colonne_noms]):
        nom_norm = normaliser_texte(nom)
        mots_nom = nom_norm.split()
        
        # 1. Comparaisons classiques
        scores = [
            fuzz.ratio(texte_vocal_norm, nom_norm),
            fuzz.partial_ratio(texte_vocal_norm, nom_norm),
            fuzz.token_sort_ratio(texte_vocal_norm, nom_norm),
            fuzz.token_set_ratio(texte_vocal_norm, nom_norm)
        ]
        
        # 2. Bonus si tous les mots du vocal sont dans le nom
        bonus_mots = 0
        if all(any(fuzz.partial_ratio(mot_vocal, mot_nom) > 80 for mot_nom in mots_nom) for mot_vocal in mots_vocal):
            bonus_mots = 15
        
        # 3. Bonus pour correspondance de début de mot
        bonus_debut = 0
        for mot_vocal in mots_vocal:
            for mot_nom in mots_nom:
                if mot_nom.startswith(mot_vocal[:3]) or mot_vocal.startswith(mot_nom[:3]):
                    bonus_debut += 10
        
        # Score final avec bonus
        score_max = max(scores) + bonus_mots + min(bonus_debut, 20)
        score_max = min(score_max, 100)  # Plafonner à 100%
        
        if score_max >= seuil:
            correspondances.append({
                'index': i,
                'nom': nom,
                'score': int(score_max)
            })
    
    # Trier par score décroissant
    correspondances.sort(key=lambda x: x['score'], reverse=True)
    return correspondances

# Interface de configuration
st.sidebar.markdown("## ⚙️ Configuration")

# Upload de fichier
uploaded_file = st.file_uploader(
    "📂 Importer le tableau des invités", 
    type=["csv", "xlsx"],
    help="Formats supportés : CSV, Excel (.xlsx)"
)

if uploaded_file:
    try:
        # Lecture fichier
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding='utf-8')
        else:
            df = pd.read_excel(uploaded_file)
        
        # Appliquer les mises à jour sauvegardées
        if 'df_updates' in st.session_state:
            for index, updates in st.session_state.df_updates.items():
                for col, value in updates.items():
                    df.at[index, col] = value
        
        # Détection automatique des colonnes
        colonnes_detectees = detect_colonnes_noms(df.columns)
        
        st.sidebar.markdown("### 👤 Configuration des colonnes")
        
        # Interface de sélection des colonnes
        if colonnes_detectees['complete']:
            st.sidebar.success(f"Colonne nom complet détectée : `{colonnes_detectees['complete']}`")
            colonne_noms = colonnes_detectees['complete']
            mode_colonnes = "complete"
        elif colonnes_detectees['nom'] and colonnes_detectees['prenom']:
            st.sidebar.success(f"Colonnes séparées détectées :")
            st.sidebar.write(f"- Nom : `{colonnes_detectees['nom']}`")
            st.sidebar.write(f"- Prénom : `{colonnes_detectees['prenom']}`")
            
            # Créer une colonne combinée
            df['_nom_complet'] = df[colonnes_detectees['prenom']].astype(str) + " " + df[colonnes_detectees['nom']].astype(str)
            colonne_noms = '_nom_complet'
            mode_colonnes = "separees"
        else:
            st.sidebar.error("❌ Colonnes nom non détectées automatiquement")
            colonne_noms = st.sidebar.selectbox("Sélectionnez la colonne des noms", df.columns)
            mode_colonnes = "manuelle"
        
        # Option de reconfiguration manuelle
        if st.sidebar.checkbox("⚙️ Configuration manuelle"):
            mode_config = st.sidebar.radio("Mode de configuration", ["Nom complet", "Nom + Prénom séparés"])
            
            if mode_config == "Nom complet":
                colonne_noms = st.sidebar.selectbox("Colonne nom complet", df.columns)
                mode_colonnes = "complete"
            else:
                col_prenom = st.sidebar.selectbox("Colonne prénom", df.columns)
                col_nom = st.sidebar.selectbox("Colonne nom", df.columns)
                df['_nom_complet'] = df[col_prenom].astype(str) + " " + df[col_nom].astype(str)
                colonne_noms = '_nom_complet'
                mode_colonnes = "separees"
        
        # Configuration du seuil de reconnaissance
        seuil_reconnaissance = st.sidebar.slider("🎯 Seuil de reconnaissance (%)", 50, 95, 70)
        
        # Options avancées de reconnaissance
        with st.sidebar.expander("⚙️ Options avancées"):
            auto_validation_seuil = st.slider("Seuil auto-validation", 90, 100, 95)
            recherche_flexible = st.checkbox("Recherche flexible (mots individuels)", True)
            inversion_nom_prenom = st.checkbox("Essayer l'inversion Nom/Prénom", True)
        
        # Initialisation colonne Présent avec horodatage
        if "Présent" not in df.columns:
            df["Présent"] = "❌"
        if "Heure_pointage" not in df.columns:
            df["Heure_pointage"] = ""
        
        # Convertir les valeurs existantes
        for i in range(len(df)):
            if str(df.at[i, "Présent"]).lower() in ["oui", "yes", "vrai", "true", "1", "✔️"]:
                df.at[i, "Présent"] = "✔️"
            else:
                df.at[i, "Présent"] = "❌"
        
        # Statistiques
        presents = len(df[df["Présent"] == "✔️"])
        absents = len(df[df["Présent"] == "❌"])
        taux_presence = (presents / len(df)) * 100 if len(df) > 0 else 0
        
        # Affichage des statistiques
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("👥 Total", len(df))
        with col2:
            st.metric("✅ Présents", presents)
        with col3:
            st.metric("❌ Absents", absents)
        with col4:
            st.metric("📊 Taux", f"{taux_presence:.1f}%")
        
        # Interface principale
        st.markdown("---")
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            if st.button("🎙️ Démarrer l'écoute vocale", help="Cliquez puis parlez le nom de la personne"):
                st.session_state.recording = True
        
        with col2:
            recherche_manuelle = st.text_input("🔍 Recherche manuelle", placeholder="Tapez un nom...")
            
        with col3:
            if st.button("🔄 Reset", type="secondary"):
                df["Présent"] = "❌"
                df["Heure_pointage"] = ""
                st.success("Réinitialisé !")
                st.rerun()
        
        # Traitement de la recherche manuelle
        if recherche_manuelle:
            correspondances = rechercher_correspondance(recherche_manuelle, df, colonne_noms, seuil_reconnaissance)
            if correspondances:
                for match in correspondances[:3]:  # Top 3 correspondances
                    if st.button(f"✔️ Marquer présent : {match['nom']} ({match['score']}%)"):
                        df.at[match['index'], "Présent"] = "✔️"
                        df.at[match['index'], "Heure_pointage"] = datetime.now().strftime("%H:%M:%S")
                        st.success(f"✅ {match['nom']} marqué(e) présent(e)")
                        st.rerun()
        
        # Module vocal amélioré
        if st.session_state.get('recording', False):
            with st.spinner("🎤 Initialisation du microphone..."):
                r = sr.Recognizer()
                
                # Configuration optimisée pour la reconnaissance vocale
                r.energy_threshold = 300  # Seuil d'énergie pour détecter la parole
                r.dynamic_energy_threshold = True
                r.pause_threshold = 0.8  # Pause entre les mots
                r.operation_timeout = None
                
                try:
                    with sr.Microphone() as source:
                        st.info("🔊 **En écoute... Parlez maintenant !**", icon="🎤")
                        st.write("💡 Conseil : Dites clairement 'Prénom Nom' ou 'Nom Prénom'")
                        
                        # Calibration du microphone
                        r.adjust_for_ambient_noise(source, duration=1)
                        
                        # Écoute avec paramètres optimisés
                        audio = r.listen(source, timeout=10, phrase_time_limit=8)
                        
                    with st.spinner("🧠 Traitement de la reconnaissance vocale..."):
                        # Essayer plusieurs services de reconnaissance
                        texte_reconnu = None
                        
                        try:
                            # Google (français)
                            texte_reconnu = r.recognize_google(audio, language="fr-FR")
                            service_utilise = "Google (fr-FR)"
                        except:
                            try:
                                # Google (français canadien, parfois meilleur)
                                texte_reconnu = r.recognize_google(audio, language="fr-CA")
                                service_utilise = "Google (fr-CA)"
                            except:
                                try:
                                    # Sphinx (hors ligne, moins précis mais backup)
                                    texte_reconnu = r.recognize_sphinx(audio, language="fr-FR")
                                    service_utilise = "Sphinx (fr-FR)"
                                except:
                                    raise sr.UnknownValueError("Aucun service de reconnaissance n'a pu traiter l'audio")
                        
                    st.success(f"🔊 **Texte reconnu :** '{texte_reconnu}' (via {service_utilise})")
                    
                    # Nettoyage et préparation du texte
                    texte_nettoye = texte_reconnu.strip()
                    
                    # Recherche de correspondances avec plusieurs variantes
                    correspondances = []
                    
                    # 1. Recherche directe
                    correspondances.extend(rechercher_correspondance(texte_nettoye, df, colonne_noms, seuil_reconnaissance))
                    
                    # 2. Recherche avec inversion Prénom/Nom
                    mots = texte_nettoye.split()
                    if len(mots) >= 2:
                        texte_inverse = " ".join(reversed(mots))
                        correspondances.extend(rechercher_correspondance(texte_inverse, df, colonne_noms, seuil_reconnaissance))
                    
                    # 3. Recherche avec chaque mot individuellement
                    for mot in mots:
                        if len(mot) > 2:  # Éviter les mots trop courts
                            correspondances.extend(rechercher_correspondance(mot, df, colonne_noms, max(seuil_reconnaissance-20, 50)))
                    
                    # Supprimer les doublons et trier
                    correspondances_uniques = {}
                    for match in correspondances:
                        if match['index'] not in correspondances_uniques or match['score'] > correspondances_uniques[match['index']]['score']:
                            correspondances_uniques[match['index']] = match
                    
                    correspondances_finales = sorted(correspondances_uniques.values(), key=lambda x: x['score'], reverse=True)
                    
                    if correspondances_finales:
                        st.markdown("### 🎯 Correspondances trouvées :")
                        
                        # Affichage des correspondances avec boutons
                        for i, match in enumerate(correspondances_finales[:5]):  # Top 5
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                st.write(f"**{match['nom']}** (Score: {match['score']}%)")
                            with col2:
                                if st.button(f"✔️ Présent", key=f"btn_present_{i}"):
                                    df.at[match['index'], "Présent"] = "✔️"
                                    df.at[match['index'], "Heure_pointage"] = datetime.now().strftime("%H:%M:%S")
                                    st.success(f"✅ {match['nom']} marqué(e) présent(e)")
                                    # Sauvegarder dans session state pour persister
                                    if 'df_updates' not in st.session_state:
                                        st.session_state.df_updates = {}
                                    st.session_state.df_updates[match['index']] = {
                                        'Présent': '✔️',
                                        'Heure_pointage': datetime.now().strftime("%H:%M:%S")
                                    }
                                    st.rerun()
                            with col3:
                                if st.button(f"❌ Absent", key=f"btn_absent_{i}"):
                                    df.at[match['index'], "Présent"] = "❌"
                                    df.at[match['index'], "Heure_pointage"] = ""
                                    st.info(f"❌ {match['nom']} marqué(e) absent(e)")
                                    st.rerun()
                        
                        # Auto-validation pour les scores TRÈS élevés seulement
                        if correspondances_finales[0]['score'] >= 95:
                            df.at[correspondances_finales[0]['index'], "Présent"] = "✔️"  
                            df.at[correspondances_finales[0]['index'], "Heure_pointage"] = datetime.now().strftime("%H:%M:%S")
                            st.success(f"🎯 **Auto-validé :** {correspondances_finales[0]['nom']} (Score: {correspondances_finales[0]['score']}%)")
                            # Sauvegarder dans session state
                            if 'df_updates' not in st.session_state:
                                st.session_state.df_updates = {}
                            st.session_state.df_updates[correspondances_finales[0]['index']] = {
                                'Présent': '✔️',
                                'Heure_pointage': datetime.now().strftime("%H:%M:%S")
                            }
                            st.rerun()
                        else:
                            st.info("💡 Cliquez sur ✔️ pour confirmer la présence")
                            
                    else:
                        st.warning(f"⚠️ Aucune correspondance trouvée pour '{texte_nettoye}' (seuil: {seuil_reconnaissance}%)")
                        st.info("💡 **Suggestions :**")
                        st.write("- Baissez le seuil de reconnaissance")
                        st.write("- Utilisez la recherche manuelle")
                        st.write("- Vérifiez l'orthographe des noms")
                        st.write("- Essayez de dire 'Prénom Nom' ou 'Nom Prénom'")
                    
                except sr.WaitTimeoutError:
                    st.error("⏱️ Délai d'écoute dépassé - Aucun son détecté")
                    st.info("💡 Vérifiez que votre microphone fonctionne")
                except sr.UnknownValueError:
                    st.error("❓ Parole non reconnue - Essayez de parler plus clairement")
                    st.info("💡 Parlez plus fort, plus lentement et articulez bien")
                except sr.RequestError as e:
                    st.error(f"🔌 Erreur de service de reconnaissance : {e}")
                    st.info("💡 Vérifiez votre connexion internet")
                except Exception as e:
                    st.error(f"🚫 Erreur inattendue : {e}")
                    st.info("💡 Rechargez la page et réessayez")
                finally:
                    st.session_state.recording = False
        
        # Affichage du tableau avec options
        st.markdown("---")
        st.markdown("### 📋 Liste des participants")
        
        # Filtres d'affichage
        col1, col2, col3 = st.columns(3)
        with col1:
            filtre_statut = st.selectbox("Filtrer par statut", ["Tous", "Présents", "Absents"])
        with col2:
            nb_lignes = st.selectbox("Lignes à afficher", [10, 25, 50, 100, "Toutes"])
        with col3:
            if st.button("📊 Afficher statistiques détaillées"):
                st.session_state.show_stats = not st.session_state.get('show_stats', False)
        
        # Application des filtres
        df_affichage = df.copy()
        if filtre_statut == "Présents":
            df_affichage = df_affichage[df_affichage["Présent"] == "✔️"]
        elif filtre_statut == "Absents":
            df_affichage = df_affichage[df_affichage["Présent"] == "❌"]
        
        # Colonnes à afficher
        colonnes_affichage = [col for col in df_affichage.columns if not col.startswith('_')]
        
        # Affichage du tableau
        if nb_lignes == "Toutes":
            st.dataframe(df_affichage[colonnes_affichage], use_container_width=True)
        else:
            st.dataframe(df_affichage[colonnes_affichage].head(nb_lignes), use_container_width=True)
        
        # Statistiques détaillées
        if st.session_state.get('show_stats', False):
            st.markdown("### 📈 Statistiques détaillées")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Répartition par statut :**")
                st.bar_chart(pd.Series([presents, absents], index=["Présents", "Absents"]))
            
            with col2:
                if df["Heure_pointage"].str.len().sum() > 0:  # Si il y a des heures
                    heures_pointage = df[df["Heure_pointage"] != ""]["Heure_pointage"]
                    st.markdown("**Heures de pointage :**")
                    st.write(heures_pointage.tolist())
        
        # Export amélioré
        st.markdown("---")
        st.markdown("### 💾 Exporter les résultats")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Export CSV
            output_csv = BytesIO()
            df[colonnes_affichage].to_csv(output_csv, index=False, encoding='utf-8')
            st.download_button(
                label="📥 Télécharger CSV",
                data=output_csv.getvalue(),
                file_name=f"pointage_ekho_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Export Excel
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                df[colonnes_affichage].to_excel(writer, index=False, sheet_name='Pointage')
                
                # Formatage Excel
                workbook = writer.book
                worksheet = writer.sheets['Pointage']
                
                # Format pour les présents
                format_present = workbook.add_format({'bg_color': '#d4edda', 'font_color': '#155724'})
                format_absent = workbook.add_format({'bg_color': '#f8d7da', 'font_color': '#721c24'})
                
                # Application du formatage
                for row in range(1, len(df) + 1):
                    if df.iloc[row-1]['Présent'] == '✔️':
                        worksheet.set_row(row, cell_format=format_present)
                    else:
                        worksheet.set_row(row, cell_format=format_absent)
            
            st.download_button(
                label="📊 Télécharger Excel",
                data=output_excel.getvalue(),
                file_name=f"pointage_ekho_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            # Export présents uniquement
            df_presents = df[df["Présent"] == "✔️"]
            if len(df_presents) > 0:
                output_presents = BytesIO()
                df_presents[colonnes_affichage].to_csv(output_presents, index=False, encoding='utf-8')
                st.download_button(
                    label="✅ Présents uniquement",
                    data=output_presents.getvalue(),
                    file_name=f"presents_seulement_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.button("✅ Présents uniquement", disabled=True, help="Aucun présent à exporter")
    
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement du fichier : {e}")
        st.info("Vérifiez que le fichier est bien formaté et contient des colonnes de noms.")

else:
    st.info("👆 Commencez par importer un fichier CSV ou Excel contenant la liste des participants")
    
    # Exemple de format attendu
    with st.expander("📖 Format de fichier attendu"):
        st.markdown("""
        **Formats supportés :**
        - Une colonne avec nom complet : `Nom complet`, `Full Name`, etc.
        - Deux colonnes séparées : `Nom` + `Prénom`, `LastName` + `FirstName`, etc.
        
        **Exemple CSV :**
        ```
        Prénom,Nom,Email
        Jean,Dupont,jean.dupont@email.com
        Marie,Martin,marie.martin@email.com
        ```
        
        **Exemple avec nom complet :**
        ```
        Nom complet,Fonction
        Jean Dupont,Directeur
        Marie Martin,Secrétaire
        ```
        """)

# Informations dans la sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("## ℹ️ Informations")
st.sidebar.markdown("""
**Fonctionnalités :**
- 🎤 Reconnaissance vocale français
- 🔍 Recherche manuelle
- 📊 Statistiques en temps réel
- 💾 Export multi-format
- ⚙️ Seuil de reconnaissance ajustable

**Conseils d'utilisation :**
- Parlez clairement et distinctement
- Utilisez le prénom ET le nom
- Ajustez le seuil si nécessaire
- Vérifiez les correspondances proposées
""")

st.sidebar.markdown("---")
st.sidebar.markdown("*ekho v2.0 - Pointage vocal intelligent*")