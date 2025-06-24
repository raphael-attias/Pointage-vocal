# Ajoutez cette section AU DÉBUT du fichier
import sys
import os

if getattr(sys, 'frozen', False):
    try:
        # Ajoute le répertoire de l'exécutable au chemin
        base_path = os.path.dirname(sys.executable)
        if base_path not in sys.path:
            sys.path.insert(0, base_path)
        
        # Importe et exécute le hook
        import runtime_hooks
        runtime_hooks.fix_streamlit_paths()
    except ImportError as e:
        print(f"⚠️ Erreur lors du chargement du hook: {e}")
    except Exception as e:
        print(f"⚠️ Erreur critique dans le hook: {e}")

# Le reste du code existant...
import webbrowser
import time
from pathlib import Path
import threading
import streamlit.cli as stcli

def run_streamlit():
    """Lance Streamlit en interne sans sous-processus"""
    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.port=8501",
        "--browser.gatherUsageStats=false",
        "--logger.level=error"
    ]
    stcli.main()

if __name__ == "__main__":
    # Détermine le chemin du script app.py
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).parent
        app_path = base_path / "app.py"
        # Correction cruciale pour les environnements gelés
        sys.path.insert(0, str(base_path))
    else:
        app_path = Path("app.py")
    
    print("🎤 Démarrage d'ekho - Pointage vocal")
    print("📱 L'application va s'ouvrir dans votre navigateur...")
    print("🌐 URL: http://localhost:8501")
    print("❌ Pour arrêter : Ctrl+C dans cette fenêtre")
    print("-" * 50)
    
    try:
        # Ouvrir le navigateur après un délai contrôlé
        def open_browser():
            time.sleep(3)  # Donne le temps à Streamlit de démarrer
            webbrowser.open("http://localhost:8501")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Lance Streamlit directement
        run_streamlit()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'application...")
    except FileNotFoundError:
        print(f"❌ Erreur: {app_path} non trouvé")
        input("Appuyez sur Entrée pour quitter...")
    except Exception as e:
        print(f"❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        input("Appuyez sur Entrée pour quitter...")