"""
AX-S v10.0 - Sistema de Control de Accesos Residencial
Entry point para Streamlit Cloud
"""
import streamlit as st
import sys
import os

# Asegurar que el directorio raíz está en el path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importar y ejecutar la app principal
if __name__ == "__main__":
    # Importar aquí para evitar ejecución prematura
    import app_accesos_residencial
