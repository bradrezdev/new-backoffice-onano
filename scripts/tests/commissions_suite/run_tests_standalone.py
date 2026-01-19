"""
Script standalone para ejecutar tests de comisiones MLM.
Este script inicializa Reflex correctamente antes de ejecutar pytest.

Autor: QA Engineer Giovann
Fecha: Octubre 2025
"""

import sys
import os

# Agregar path del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

# Inicializar reflex PRIMERO
import reflex as rx

# Ahora importar pytest y ejecutar
import pytest

if __name__ == "__main__":
    # Ejecutar pytest con los argumentos proporcionados
    sys.exit(pytest.main(sys.argv[1:]))
