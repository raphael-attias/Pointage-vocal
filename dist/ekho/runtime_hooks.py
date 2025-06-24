import sys
import os

def fix_streamlit_paths():
    """Corrige les chemins pour Streamlit dans les environnements gelés"""
    if getattr(sys, 'frozen', False):
        # Chemin de base de l'application compilée
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
        
        print(f"🔧 Correction des chemins pour Streamlit [base: {base_path}]")
        
        # Chemins critiques pour Streamlit
        os.environ['STREAMLIT_BASE'] = base_path
        os.environ['STREAMLIT_STATIC'] = os.path.join(base_path, 'static')
        
        # Ajout des chemins aux modules
        lib_path = os.path.join(base_path, 'lib')
        if os.path.exists(lib_path) and lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        
        # Correction spécifique pour les templates Jinja
        try:
            import jinja2
            jinja2_path = os.path.dirname(jinja2.__file__)
            if jinja2_path not in sys.path:
                sys.path.append(jinja2_path)
        except ImportError:
            pass
        
        # Correction pour les ressources de Streamlit
        try:
            import streamlit
            streamlit_path = os.path.dirname(streamlit.__file__)
            if streamlit_path not in sys.path:
                sys.path.append(streamlit_path)
        except ImportError:
            pass

# Applique les corrections au démarrage
fix_streamlit_paths()