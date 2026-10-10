"""
Módulo API - Lógica de Negocio y Servicio de Datos
Proyecto: Fundamentos Básicos de Python - Programación 4
Docente: Alejandro Rodas Vásquez
Universidad Tecnológica de Pereira
"""

from .data_service import (
    load_dataset,
    filter_data,
    calculate_medians,
    consultar_propiedades_edaficas,
    get_available_departments,
    get_available_municipalities,
    get_available_crops
)

__all__ = [
    "load_dataset",
    "filter_data",
    "calculate_medians",
    "consultar_propiedades_edaficas",
    "get_available_departments",
    "get_available_municipalities",
    "get_available_crops"
]
