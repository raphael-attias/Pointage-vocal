from cx_Freeze import setup, Executable
import sys
import os

# Modules critiques supplémentaires
import jinja2
import setuptools
import asyncio
import sqlite3
import watchdog
import numpy
import pyarrow
import PIL

build_exe_options = {
    "packages": [
        "streamlit",
        "pandas", 
        "speech_recognition",
        "fuzzywuzzy",
        "openpyxl",
        "unidecode",
        "xlsxwriter",
        "altair",
        "tornado",
        "click",
        "requests",
        "urllib3",
        "pyaudio",
        "jinja2",
        "setuptools",
        "asyncio",
        "sqlite3",
        "watchdog",
        "numpy",
        "pyarrow",
        "PIL",
    ],
    "excludes": [
        "tkinter",
        "matplotlib",
        "test",
        "unittest"
    ],
    "include_files": [
        ("images/", "images/"),
        ("app.py", "app.py"),
        ("launcher.py", "launcher.py"),
        ("runtime_hooks.py", "runtime_hooks.py")
    ],
    "optimize": 2,
    "build_exe": "dist/ekho",
    "path": sys.path + ["."],
    "include_msvcr": True,
}

executables = [
    Executable(
        script="launcher.py",
        base=None,
        target_name="ekho.exe",
        icon="images/ekho-logo.ico"
    )
]

setup(
    name="ekho",
    version="2.0",
    description="Application de pointage vocal avec Streamlit",
    options={"build_exe": build_exe_options},
    executables=executables
)