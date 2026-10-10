"""
Módulo UI - Interfaz de Usuario de Escritorio por Línea de Comandos (CLI)
Proyecto: Fundamentos Básicos de Python - Programación 4
Docente: Alejandro Rodas Vásquez
Universidad Tecnológica de Pereira
"""

from .cli_view import (
    solicitar_parametros_consulta,
    mostrar_tabla_resultados,
    mostrar_banner,
    mostrar_sugerencias,
    iniciar_interfaz_usuario
)

__all__ = [
    "solicitar_parametros_consulta",
    "mostrar_tabla_resultados",
    "mostrar_banner",
    "mostrar_sugerencias",
    "iniciar_interfaz_usuario"
]
