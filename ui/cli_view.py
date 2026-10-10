"""
Módulo cli_view.py - Vista e Interfaz de Línea de Comandos (CLI).
Gestiona la interacción con el usuario, captura de entradas y renderizado de tablas.
"""

import sys
from typing import Dict, Any, List, Tuple

# Asegurar codificación UTF-8 para consola en Windows
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False


def mostrar_banner() -> None:
    """Muestra el banner institucional y de bienvenida del sistema."""
    linea = "=" * 78
    print("\n" + linea)
    print("   UNIVERSIDAD TECNOLÓGICA DE PEREIRA - INGENIERÍA DE SISTEMAS Y COMPUTACIÓN")
    print("                 PROGRAMACIÓN IV - DOCENTE: ALEJANDRO RODAS VÁSQUEZ")
    print("             SISTEMA DE CONSULTA DE VARIABLES EDÁFICAS EN SUELOS")
    print(linea)


def solicitar_parametros_consulta() -> Tuple[str, str, str, int]:
    """
    Solicita interactivamente los parámetros de consulta al usuario:
    1. Departamento
    2. Municipio
    3. Cultivo
    4. Número de registros a consultar
    """
    print("\n[+] Ingrese los parámetros de búsqueda solicitados:\n")

    # 1. Departamento
    while True:
        departamento = input("  1. Ingrese el Departamento (ej. Risaralda): ").strip()
        if departamento:
            break
        print("     [!] El departamento no puede estar vacío. Intente de nuevo.")

    # 2. Municipio
    while True:
        municipio = input("  2. Ingrese el Municipio (ej. Pereira, Balboa, Santa Rosa): ").strip()
        if municipio:
            break
        print("     [!] El municipio no puede estar vacío. Intente de nuevo.")

    # 3. Cultivo
    while True:
        cultivo = input("  3. Ingrese el Cultivo (ej. Café, Aguacate, Plátano): ").strip()
        if cultivo:
            break
        print("     [!] El cultivo no puede estar vacío. Intente de nuevo.")

    # 4. Número de registros a consultar
    while True:
        limite_input = input("  4. Ingrese el Número de registros a consultar: ").strip()
        try:
            limite = int(limite_input)
            if limite > 0:
                break
            print("     [!] El número de registros debe ser un entero positivo mayor a 0.")
        except ValueError:
            print("     [!] Ingrese un valor numérico válido (ej. 10).")

    return departamento, municipio, cultivo, limite


def mostrar_tabla_resultados(resultado: Dict[str, Any]) -> None:
    """
    Renderiza la tabla de resultados requerida por el profesor:
    Columnas: Departamento | Municipio | Cultivo | Topografía | Mediana pH | Mediana P (mg/kg) | Mediana K (cmol/kg)
    """
    registros: List[Dict[str, Any]] = resultado.get("registros", [])
    total: int = resultado.get("total_encontrados", 0)
    medianas = resultado.get("medianas", {})

    if total == 0:
        print("\n" + "-" * 78)
        print("  [-] No se encontraron registros con los criterios especificados.")
        print("-" * 78)
        return

    headers = [
        "Departamento",
        "Municipio",
        "Cultivo",
        "Topografía",
        "Mediana pH",
        "Mediana P\n(Bray II mg/kg)",
        "Mediana K\n(cmol(+)/kg)"
    ]

    filas = []
    for reg in registros:
        ph_str = f"{reg['mediana_ph']:.2f}" if reg["mediana_ph"] is not None else "N/D"
        p_str = f"{reg['mediana_p']:.2f}" if reg["mediana_p"] is not None else "N/D"
        k_str = f"{reg['mediana_k']:.3f}" if reg["mediana_k"] is not None else "N/D"

        filas.append([
            reg["departamento"],
            reg["municipio"],
            reg["cultivo"],
            reg["topografia"],
            ph_str,
            p_str,
            k_str
        ])

    print("\n" + "=" * 78)
    print(f"  RESULTADOS DE LA CONSULTA ({total} registro(s) visualizado(s))")
    print("=" * 78 + "\n")

    if HAS_TABULATE:
        try:
            print(tabulate(filas, headers=headers, tablefmt="grid", stralign="left", numalign="right"))
        except UnicodeEncodeError:
            print(tabulate(filas, headers=headers, tablefmt="simple", stralign="left", numalign="right"))
    else:
        # Fallback si tabulate no estuviera instalado
        header_str = " | ".join(headers)
        print(header_str)
        print("-" * len(header_str))
        for f in filas:
            print(" | ".join(str(c) for c in f))

    # Resumen explícito de las medianas calculadas
    print("\n" + "-" * 78)
    print("  RESUMEN ESTADÍSTICO DE VARIABLES EDÁFICAS DEL CULTIVO CONSULTADO:")
    print(f"    * Mediana pH:       {medianas.get('mediana_ph', 'N/D')}")
    print(f"    * Mediana Fósforo:  {medianas.get('mediana_p', 'N/D')} mg/kg")
    print(f"    * Mediana Potasio:  {medianas.get('mediana_k', 'N/D')} cmol(+)/kg")
    print("-" * 78 + "\n")


def mostrar_sugerencias(departamento: str, municipios: List[str], cultivos: List[str]) -> None:
    """Muestra opciones disponibles para guiar al usuario si no encuentra registros."""
    print("\n[i] Guía rápida de valores en el departamento de " + departamento + ":")
    if municipios:
        print(f"    Municipios disponibles ({len(municipios)}): {', '.join(municipios[:8])}...")
    if cultivos:
        print(f"    Cultivos disponibles ({len(cultivos)}): {', '.join(cultivos[:10])}...")


def iniciar_interfaz_usuario() -> None:
    """Bucle principal de la interfaz de consola."""
    mostrar_banner()


def confirmar_continuacion() -> bool:
    """Pregunta al usuario si desea realizar otra consulta."""
    while True:
        resp = input("\n¿Desea realizar otra consulta? (s/n): ").strip().lower()
        if resp in {"s", "si", "sí", "y", "yes"}:
            return True
        if resp in {"n", "no"}:
            return False
        print("  [!] Por favor responda 's' para Sí o 'n' para No.")
