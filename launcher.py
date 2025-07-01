import subprocess
import os
import sys

def main():
    # Récupère le chemin de l'app dans le même dossier que l'exécutable
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    app_path = os.path.join(base_dir, "app.py")
    
    # Lance le serveur Streamlit
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
