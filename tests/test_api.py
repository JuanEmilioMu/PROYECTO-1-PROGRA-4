"""
Pruebas Unitarias para el Módulo API
Verificación de Requisitos Funcionales y Lógica de Negocio
"""

import unittest
import os
import sys
import pandas as pd

# Incluir ruta base del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

from api.data_service import (
    clean_numeric_value,
    normalize_text,
    calculate_medians,
    consultar_propiedades_edaficas,
    load_dataset
)


class TestDataService(unittest.TestCase):
    """Casos de prueba para el servicio de datos edáficos."""

    def test_normalize_text(self):
        """Verifica la remoción de tildes y homogeneización a mayúsculas."""
        self.assertEqual(normalize_text("Risaralda"), "RISARALDA")
        self.assertEqual(normalize_text("Belén de Umbría"), "BELEN DE UMBRIA")
        self.assertEqual(normalize_text("Café"), "CAFE")
        self.assertEqual(normalize_text("  Caña panelera/azucar  "), "CANA PANELERA/AZUCAR")
        self.assertEqual(normalize_text(None), "")

    def test_clean_numeric_value(self):
        """Verifica la limpieza de valores numéricos, operadores y detección de anomalías."""
        # Valores estándar
        self.assertEqual(clean_numeric_value(5.49, "ph"), 5.49)
        self.assertEqual(clean_numeric_value("5,61", "ph"), 5.61)

        # Límite de detección
        self.assertEqual(clean_numeric_value("<3,87", "p"), 3.87)
        self.assertEqual(clean_numeric_value("< 0,55", "k"), 0.55)

        # Escalamiento de valores de fósforo con pérdida de decimal
        self.assertAlmostEqual(clean_numeric_value(1289501246355990.0, "p"), 12.90, places=1)

        # Valores corruptos de fechas en pH deben descartarse
        self.assertIsNone(clean_numeric_value("2024-05-06 00:00:00", "ph"))
        self.assertIsNone(clean_numeric_value("ND", "p"))

    def test_calculate_medians(self):
        """Verifica el cálculo de medianas sobre un DataFrame sintético."""
        data = {
            "pH agua:suelo 2,5:1,0": [5.0, 5.5, 6.0],
            "Fósforo (P) Bray II mg/kg": [10.0, 20.0, 30.0],
            "Potasio (K) intercambiable cmol(+)/kg": [0.2, 0.4, 0.6]
        }
        df_mock = pd.DataFrame(data)
        medianas = calculate_medians(df_mock)

        self.assertEqual(medianas["mediana_ph"], 5.5)
        self.assertEqual(medianas["mediana_p"], 20.0)
        self.assertEqual(medianas["mediana_k"], 0.4)

    def test_consultar_propiedades_edaficas(self):
        """Verifica la consulta completa contra el dataset real para Risaralda."""
        resultado = consultar_propiedades_edaficas(
            departamento="Risaralda",
            municipio="Balboa",
            cultivo="Caña",
            limite=5
        )

        self.assertIn("total_encontrados", resultado)
        self.assertIn("registros", resultado)
        self.assertIn("medianas", resultado)
        self.assertGreater(resultado["total_encontrados"], 0)
        self.assertLessEqual(len(resultado["registros"]), 5)

        primer_reg = resultado["registros"][0]
        self.assertEqual(primer_reg["departamento"], "RISARALDA")
        self.assertEqual(primer_reg["municipio"], "BALBOA")
        self.assertIsNotNone(primer_reg["topografia"])
        self.assertIsNotNone(primer_reg["mediana_ph"])
        self.assertIsNotNone(primer_reg["mediana_p"])
        self.assertIsNotNone(primer_reg["mediana_k"])


if __name__ == "__main__":
    unittest.main()
