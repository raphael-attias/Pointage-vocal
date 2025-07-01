import streamlit
import os
import pkgutil

def check_streamlit_structure():
    """Vérifie la structure réelle de Streamlit installé"""
    
    streamlit_path = os.path.dirname(streamlit.__file__)
    print(f"🔍 Analyse de Streamlit {streamlit.__version__}")
    print(f"📁 Chemin: {streamlit_path}")
    print("=" * 60)
    
    # Liste tous les sous-modules de streamlit
    print("📦 Modules Streamlit disponibles:")
    
    valid_modules = []
    for importer, modname, ispkg in pkgutil.iter_modules(streamlit.__path__, streamlit.__name__ + "."):
        print(f"   {'📁' if ispkg else '📄'} {modname}")
        valid_modules.append(modname)
    
    # Vérification des modules couramment utilisés
    print(f"\n🔧 Vérification des modules critiques:")
    critical_modules = [
        "streamlit.runtime",
        "streamlit.web", 
        "streamlit.server",
        "streamlit.components",
        "streamlit.runtime.legacy_caching",
        "streamlit.runtime.caching",
        "streamlit.runtime.state"
    ]
    
    existing_modules = []
    for module in critical_modules:
        try:
            __import__(module)
            print(f"   ✅ {module}")
            existing_modules.append(module)
        except ImportError:
            print(f"   ❌ {module}")
    
    # Génération du code pour setup.py
    print(f"\n📝 Modules à utiliser dans setup.py:")
    print("=" * 40)
    print('    "streamlit",')
    for module in existing_modules:
        print(f'    "{module}",')
    
    return existing_modules

if __name__ == "__main__":
    check_streamlit_structure()