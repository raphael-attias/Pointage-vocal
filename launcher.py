import os
import subprocess
import sys
import webbrowser
import threading

def open_browser():
    webbrowser.open_new("http://localhost:8501")

if __name__ == "__main__":
    # Ouvre le navigateur après 1 sec
    threading.Timer(1, open_browser).start()
    
    # Lance streamlit avec app.py
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    subprocess.run(cmd)
