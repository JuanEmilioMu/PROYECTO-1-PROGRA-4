"""
Punto de Entrada Principal (main.py)
Proyecto: Fundamentos Básicos de Python - Variables Edáficas
Programación IV - Universidad Tecnológica de Pereira
Docente: Alejandro Rodas Vásquez

Este archivo orquesta la interacción entre el Módulo de Interfaz de Usuario (UI)
y el Módulo de Servicios de Datos (API), aplicando modularidad estricta.
"""

import sys
import os
import argparse

# Asegurar que el directorio raíz del proyecto esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_service import (
    load_dataset,
    consultar_propiedades_edaficas,
    get_available_municipalities,
    get_available_crops
)
from ui.cli_view import (
    mostrar_banner,
    solicitar_parametros_consulta,
    mostrar_tabla_resultados,
    mostrar_sugerencias,
    confirmar_continuacion
)


def ejecutar_modo_interactivo(df_cache=None) -> None:
    """Ejecuta el flujo interactivo estándar de la aplicación por consola."""
    mostrar_banner()

    print("\n[*] Inicializando servicio de datos... Por favor espere un momento.")
    try:
        df = df_cache if df_cache is not None else load_dataset()
        print("[✓] Datos cargados exitosamente.")
    except Exception as e:
        print(f"\n[X] Error crítico al cargar el archivo de datos: {e}")
        sys.exit(1)

    while True:
        # Solicitar parámetros mediante el módulo UI
        departamento, municipio, cultivo, limite = solicitar_parametros_consulta()

        print(f"\n[*] Consultando registros para {cultivo} en {municipio}, {departamento}...")

        # Invocar la lógica de negocio a través del módulo API
        resultado = consultar_propiedades_edaficas(
            departamento=departamento,
            municipio=municipio,
            cultivo=cultivo,
            limite=limite,
            df_source=df
        )

        # Mostrar resultados mediante el módulo UI
        mostrar_tabla_resultados(resultado)

        # Si no hubo resultados, sugerir opciones disponibles
        if resultado["total_encontrados"] == 0:
            munis = get_available_municipalities(df, departamento)
            cultivos = get_available_crops(df, departamento, municipio)
            mostrar_sugerencias(departamento, munis, cultivos)

        if not confirmar_continuacion():
            print("\nGracias por utilizar el Sistema de Consulta de Variables Edáficas. ¡Hasta pronto!\n")
            break


def ejecutar_modo_argumentos(args, df_cache=None) -> None:
    """Ejecuta una consulta directa por parámetros de línea de comandos."""
    mostrar_banner()
    try:
        df = df_cache if df_cache is not None else load_dataset()
    except Exception as e:
        print(f"[X] Error al cargar los datos: {e}")
        sys.exit(1)

    resultado = consultar_propiedades_edaficas(
        departamento=args.departamento,
        municipio=args.municipio,
        cultivo=args.cultivo,
        limite=args.limite,
        df_source=df
    )
    mostrar_tabla_resultados(resultado)


def main() -> None:
    """Función principal del software."""
    parser = argparse.ArgumentParser(
        description="Sistema de Consulta de Propiedades Edáficas (Programación IV - UTP)"
    )
    parser.add_argument("-d", "--departamento", type=str, help="Nombre del Departamento (ej. Risaralda)")
    parser.add_argument("-m", "--municipio", type=str, help="Nombre del Municipio (ej. Pereira)")
    parser.add_argument("-c", "--cultivo", type=str, help="Nombre del Cultivo (ej. Café)")
    parser.add_argument("-l", "--limite", type=int, default=10, help="Número de registros a consultar (ej. 10)")

    args = parser.parse_args()

    # Si se proporcionaron argumentos completos por CLI
    if args.departamento and args.municipio and args.cultivo:
        ejecutar_modo_argumentos(args)
    else:
        ejecutar_modo_interactivo()


if __name__ == "__main__":
    main()
