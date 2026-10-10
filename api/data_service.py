"""
Módulo data_service.py - Servicio de Extracción, Filtrado y Procesamiento de Datos Edáficos.
Implementa el consumo del dataset 'resultado_laboratorio_suelo.xlsx' y cálculos estadísticos de medianas.
"""

import os
import re
import unicodedata
import datetime
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np

# Rutas estándar del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEFAULT_EXCEL_PATH = os.path.join(DATA_DIR, "resultado_laboratorio_suelo.xlsx")
CACHE_FILE_PATH = os.path.join(DATA_DIR, "resultado_laboratorio_suelo_cache.parquet")

# Nombres canónicos de columnas esperadas
COL_DEPTO = "Departamento"
COL_MUNI = "Municipio"
COL_CULTIVO = "Cultivo"
COL_TOPO = "Topografia"
COL_PH = "pH agua:suelo 2,5:1,0"
COL_P = "Fósforo (P) Bray II mg/kg"
COL_K = "Potasio (K) intercambiable cmol(+)/kg"


def normalize_text(text: Any) -> str:
    """
    Normaliza texto removiendo tildes, caracteres especiales y espacios redundantes,
    en mayúsculas para búsquedas flexibles y robustas.
    """
    if pd.isna(text) or text is None:
        return ""
    text_str = str(text).strip()
    # Descomponer caracteres con acentos
    normalized = unicodedata.normalize('NFD', text_str)
    # Filtrar marcas diacríticas
    without_accents = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    return without_accents.upper()


def clean_numeric_value(val: Any, var_type: str = "generic") -> Optional[float]:
    """
    Limpia y convierte a número flotante los valores del laboratorio de suelo.
    Corrige problemas comunes de exportación en el dataset público:
    - Fechas introducidas por error de Excel en la columna pH.
    - Símbolos de límite de detección como '<3,87' o '< 0,55'.
    - Desplazamiento de coma decimal en números enteros grandes.
    """
    if val is None or pd.isna(val):
        return None

    # Si es fecha/datetime (anomalía detectada en el Excel para columnas de pH)
    if isinstance(val, (datetime.datetime, datetime.date)):
        return None

    # Convertir a cadena para análisis léxico
    s_val = str(val).strip()

    # Si parece una fecha textual (ej. '2024-05-06')
    if re.match(r'^\d{4}-\d{2}-\d{2}', s_val):
        return None

    # Si es 'ND' o 'No aplica'
    if s_val.upper() in {"ND", "NO APLICA", "NAN", "NULL", "NONE", ""}:
        return None

    # Reemplazar coma decimal por punto y limpiar operadores '<', '>'
    s_val = s_val.replace(',', '.')
    s_val = re.sub(r'[<>\s]', '', s_val)

    try:
        num = float(s_val)
    except (ValueError, TypeError):
        return None

    # Normalización de escalas edáficas agronómicas
    if var_type == "ph":
        # pH normal de suelo oscila entre 3.0 y 9.5
        if 1.0 <= num <= 14.0:
            return round(num, 2)
        return None

    elif var_type == "p":
        # Fósforo Bray II (mg/kg): rango agronómico habitual 0.1 a 300 mg/kg
        if num > 1e12:
            num = num / 1e14
        elif num > 1e6:
            num = num / 1e7
        elif num > 5000:
            num = num / 1000.0
        return round(num, 2) if num >= 0 else None

    elif var_type == "k":
        # Potasio intercambiable (cmol(+)/kg): rango agronómico habitual 0.05 a 5.0
        if num > 1e14:
            num = num / 1e17
        elif num > 1e6:
            num = num / 1e9
        elif num > 100:
            num = num / 1000.0
        return round(num, 3) if num >= 0 else None

    return round(num, 2)


def load_dataset(file_path: Optional[str] = None, use_cache: bool = True) -> pd.DataFrame:
    """
    Carga el dataset de análisis de suelo. Utiliza almacenamiento en caché tipo Parquet
    para optimizar drásticamente los tiempos de lectura subsiguientes.
    """
    target_excel = file_path or DEFAULT_EXCEL_PATH

    # Si existe la caché optimizada en Parquet y no se solicita omitirla
    if use_cache and os.path.exists(CACHE_FILE_PATH):
        try:
            return pd.read_parquet(CACHE_FILE_PATH)
        except Exception:
            pass  # Si falla la lectura de caché, leer directamente del Excel

    if not os.path.exists(target_excel):
        raise FileNotFoundError(f"No se encontró el archivo de datos: {target_excel}")

    # Lectura del archivo Excel oficial
    df = pd.read_excel(target_excel, engine="openpyxl")

    # Identificar nombres reales de columnas relevantes (resiliente a variaciones de tildes)
    col_mapping = {}
    for col in df.columns:
        norm_col = normalize_text(col)
        if "DEPARTAMENTO" in norm_col and COL_DEPTO not in col_mapping.values():
            col_mapping[col] = COL_DEPTO
        elif "MUNICIPIO" in norm_col and COL_MUNI not in col_mapping.values():
            col_mapping[col] = COL_MUNI
        elif "CULTIVO" in norm_col and COL_CULTIVO not in col_mapping.values():
            col_mapping[col] = COL_CULTIVO
        elif "TOPOGRAFIA" in norm_col and COL_TOPO not in col_mapping.values():
            col_mapping[col] = COL_TOPO
        elif "PH" in norm_col and COL_PH not in col_mapping.values():
            col_mapping[col] = COL_PH
        elif "FOSFORO" in norm_col and COL_P not in col_mapping.values():
            col_mapping[col] = COL_P
        elif "POTASIO" in norm_col and COL_K not in col_mapping.values():
            col_mapping[col] = COL_K

    df = df.rename(columns=col_mapping)

    # Columnas normalizadas auxiliares para filtrado ultrarrápido
    if COL_DEPTO in df.columns:
        df["_DEPTO_NORM"] = df[COL_DEPTO].apply(normalize_text)
    if COL_MUNI in df.columns:
        df["_MUNI_NORM"] = df[COL_MUNI].apply(normalize_text)
    if COL_CULTIVO in df.columns:
        df["_CULTIVO_NORM"] = df[COL_CULTIVO].apply(normalize_text)

    # Guardar en caché para que las consultas siguientes sean instantáneas
    if use_cache:
        try:
            df.to_parquet(CACHE_FILE_PATH, index=False)
        except Exception:
            pass

    return df


def filter_data(
    df: pd.DataFrame,
    departamento: str,
    municipio: str,
    cultivo: str,
    limite: int
) -> pd.DataFrame:
    """
    Filtra los registros según Departamento, Municipio y Cultivo (insensible a mayúsculas y tildes),
    limitando la cantidad de registros devueltos a 'limite'.
    """
    if df.empty:
        return df

    dep_norm = normalize_text(departamento)
    mun_norm = normalize_text(municipio)
    cul_norm = normalize_text(cultivo)

    mask = pd.Series(True, index=df.index)

    if dep_norm:
        mask &= df["_DEPTO_NORM"].str.contains(dep_norm, na=False)
    if mun_norm:
        mask &= df["_MUNI_NORM"].str.contains(mun_norm, na=False)
    if cul_norm:
        mask &= df["_CULTIVO_NORM"].str.contains(cul_norm, na=False)

    df_filtered = df[mask].copy()

    if limite and limite > 0:
        df_filtered = df_filtered.head(limite)

    return df_filtered


def calculate_medians(df_subset: pd.DataFrame) -> Dict[str, Optional[float]]:
    """
    Calcula la mediana matemática exacta para pH, Fósforo (P) y Potasio (K)
    sobre el conjunto de registros proporcionado.
    """
    if df_subset.empty:
        return {"mediana_ph": None, "mediana_p": None, "mediana_k": None}

    # Limpieza vectorial de cada variable
    clean_ph = df_subset[COL_PH].apply(lambda v: clean_numeric_value(v, "ph")).dropna()
    clean_p = df_subset[COL_P].apply(lambda v: clean_numeric_value(v, "p")).dropna()
    clean_k = df_subset[COL_K].apply(lambda v: clean_numeric_value(v, "k")).dropna()

    mediana_ph = round(float(clean_ph.median()), 2) if not clean_ph.empty else None
    mediana_p = round(float(clean_p.median()), 2) if not clean_p.empty else None
    mediana_k = round(float(clean_k.median()), 3) if not clean_k.empty else None

    return {
        "mediana_ph": mediana_ph,
        "mediana_p": mediana_p,
        "mediana_k": mediana_k
    }


def consultar_propiedades_edaficas(
    departamento: str,
    municipio: str,
    cultivo: str,
    limite: int,
    df_source: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Punto de entrada de negocio para la consulta de propiedades edáficas:
    Carga, filtra, calcula medianas y estructura los datos para la UI.
    """
    df = df_source if df_source is not None else load_dataset()
    df_filtered = filter_data(df, departamento, municipio, cultivo, limite)

    if df_filtered.empty:
        return {
            "total_encontrados": 0,
            "registros": [],
            "medianas": {"mediana_ph": None, "mediana_p": None, "mediana_k": None}
        }

    # Calcular las medianas del conjunto consultado
    medianas = calculate_medians(df_filtered)

    # Preparar filas requeridas por RF: Departamento, Municipio, Cultivo, Topografía, Medianas
    registros = []
    for _, row in df_filtered.iterrows():
        topografia = row.get(COL_TOPO, "No indica")
        if pd.isna(topografia) or str(topografia).strip() == "":
            topografia = "No indica"

        registros.append({
            "departamento": str(row.get(COL_DEPTO, "")),
            "municipio": str(row.get(COL_MUNI, "")),
            "cultivo": str(row.get(COL_CULTIVO, "")),
            "topografia": str(topografia),
            "mediana_ph": medianas["mediana_ph"],
            "mediana_p": medianas["mediana_p"],
            "mediana_k": medianas["mediana_k"]
        })

    return {
        "total_encontrados": len(df_filtered),
        "registros": registros,
        "medianas": medianas
    }


def get_available_departments(df: Optional[pd.DataFrame] = None) -> List[str]:
    """Retorna la lista ordenada de departamentos únicos disponibles."""
    if df is None:
        df = load_dataset()
    return sorted(df[COL_DEPTO].dropna().unique().tolist())


def get_available_municipalities(df: Optional[pd.DataFrame] = None, departamento: str = "") -> List[str]:
    """Retorna la lista ordenada de municipios para un departamento dado."""
    if df is None:
        df = load_dataset()
    if departamento:
        dep_norm = normalize_text(departamento)
        filtered = df[df["_DEPTO_NORM"].str.contains(dep_norm, na=False)]
        return sorted(filtered[COL_MUNI].dropna().unique().tolist())
    return sorted(df[COL_MUNI].dropna().unique().tolist())


def get_available_crops(df: Optional[pd.DataFrame] = None, departamento: str = "", municipio: str = "") -> List[str]:
    """Retorna los cultivos disponibles según los filtros aplicados."""
    if df is None:
        df = load_dataset()
    filtered = df
    if departamento:
        filtered = filtered[filtered["_DEPTO_NORM"].str.contains(normalize_text(departamento), na=False)]
    if municipio:
        filtered = filtered[filtered["_MUNI_NORM"].str.contains(normalize_text(municipio), na=False)]
    return sorted(filtered[COL_CULTIVO].dropna().unique().tolist())
