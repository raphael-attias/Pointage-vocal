from cx_Freeze import setup, Executable
import sys
import os
import streamlit

print("🔧 Configuration cx_Freeze pour ekho (version corrigée)")
print("=" * 60)

# Détection automatique du chemin Streamlit
streamlit_path = os.path.dirname(streamlit.__file__)
static_path = os.path.join(streamlit_path, "static")

print(f"📁 Streamlit path: {streamlit_path}")
print(f"📁 Streamlit version: {streamlit.__version__}")

# Construction de la liste include_files
include_files = [
    ("images/", "images/"),
    ("app.py", "app.py"),
    ("launcher.py", "launcher.py"),
    ("runtime_hooks.py", "runtime_hooks.py")
]

# Ajout conditionnel du répertoire static s'il existe
if os.path.exists(static_path):
    include_files.append((static_path, "streamlit/static"))
    print(f"✅ Streamlit static ajouté: {static_path}")

# Packages essentiels (version minimaliste testée)
packages = [
    # Streamlit core seulement
    "streamlit",
    "streamlit.cli",
    "streamlit.web.cli",
    
    # Votre application
    "pandas", 
    "speech_recognition",
    "fuzzywuzzy",
    "openpyxl",
    "unidecode",
    "xlsxwriter",
    
    # Dépendances critiques
    "altair",
    "tornado",
    "click",
    "requests",
    "urllib3",
    "jinja2",
    "numpy",
    "pyarrow",
    "PIL",
    
    # Système de base
    "json",
    "base64",
    "hashlib",
    "uuid",
    "datetime",
    "collections",
    "threading",
    "webbrowser",
    "pathlib",
    "time",
    "traceback",
    
    # Audio
    "pyaudio",
]

# Tentative d'ajout des modules Streamlit s'ils existent
optional_streamlit_modules = [
    "streamlit.runtime",
    "streamlit.web",
    "streamlit.components",
    "streamlit.cli",
    "streamlit.web.cli"
]

for module in optional_streamlit_modules:
    try:
        __import__(module)
        packages.append(module)
        print(f"✅ Module ajouté: {module}")
    except ImportError:
        print(f"⚠️ Module ignoré: {module}")

print(f"📦 Total packages: {len(packages)}")

build_exe_options = {
    "packages": packages,
    "excludes": [
        "tkinter",
        "matplotlib", 
        "test",
        "unittest",
        "pydoc",
        "doctest",
        "multiprocessing",
        "streamlit.server",  # Exclusion explicite du module problématique
    ],
    "include_files": include_files,
    "optimize": 1,
    "build_exe": "dist/ekho",
    "path": sys.path + ["."],
    "include_msvcr": True,
    "silent": False,
    "zip_include_packages": [],
    "zip_exclude_packages": ["streamlit", "pandas", "numpy"],
}

executables = [
    Executable(
        script="launcher.py",
        base="Console",
        target_name="ekho.exe",
        icon="images/ekho-logo.ico" if os.path.exists("images/ekho-logo.ico") else None
    )
]

print("\n🚀 Lancement de la compilation...")

setup(
    name="ekho",
    version="2.0",
    description="Application de pointage vocal avec Streamlit",
    options={"build_exe": build_exe_options},
    executables=executables
)

print("✅ Compilation terminée !")