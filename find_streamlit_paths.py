import os
import sys
import streamlit

def find_streamlit_paths():
    """Trouve et affiche les chemins Streamlit pour cx_Freeze"""
    
    print("🔍 Diagnostic des chemins Streamlit")
    print("=" * 50)
    
    # Chemin de Streamlit
    streamlit_path = os.path.dirname(streamlit.__file__)
    print(f"📁 Streamlit installé dans: {streamlit_path}")
    
    # Vérification du répertoire static
    static_path = os.path.join(streamlit_path, "static")
    if os.path.exists(static_path):
        print(f"✅ Répertoire static trouvé: {static_path}")
        files_count = len(os.listdir(static_path))
        print(f"   📄 Contient {files_count} fichiers/dossiers")
    else:
        print(f"❌ Répertoire static INTROUVABLE: {static_path}")
        
        # Chercher d'autres répertoires static possibles
        print("🔎 Recherche d'autres répertoires static...")
        for root, dirs, files in os.walk(streamlit_path):
            if 'static' in dirs:
                found_static = os.path.join(root, 'static')
                print(f"   📁 Trouvé: {found_static}")
    
    # Informations sur l'environnement
    print(f"\n🐍 Python executable: {sys.executable}")
    print(f"📦 Site-packages: {os.path.dirname(streamlit_path)}")
    
    # Génération du code pour setup.py
    print(f"\n📝 Code à utiliser dans setup.py:")
    print("=" * 50)
    if os.path.exists(static_path):
        print(f'    ("{static_path}", "streamlit/static"),')
    else:
        print("# Aucun répertoire static trouvé - supprimez cette ligne du setup.py")
    
    # Vérification des autres dépendances critiques
    print(f"\n🔧 Vérification des autres modules:")
    modules_to_check = ['pandas', 'numpy', 'jinja2', 'tornado', 'altair']
    for module_name in modules_to_check:
        try:
            module = __import__(module_name)
            module_path = os.path.dirname(module.__file__)
            print(f"✅ {module_name}: {module_path}")
        except ImportError:
            print(f"❌ {module_name}: NON INSTALLÉ")

if __name__ == "__main__":
    find_streamlit_paths()