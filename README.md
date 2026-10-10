# Proyecto: Consulta de Variables Edáficas en Suelos de Colombia

**Universidad Tecnológica de Pereira (UTP)**  
**Facultad de Ingenierías - Programa de Ingeniería de Sistemas y Computación**  
**Asignatura:** Programación IV  
**Docente:** Alejandro Rodas Vásquez  

---

## 📌 1. Descripción del Proyecto

Este software es una aplicación de escritorio por línea de comandos (CLI) desarrollada en Python, diseñada bajo principios de **modularidad** y **separación de responsabilidades**. Su objetivo es permitir a técnicos agrícolas, investigadores y productores consultar y analizar las propiedades edáficas fundamentales (**pH**, **Fósforo [P]** y **Potasio [K]**) a partir de los datos oficiales del análisis de laboratorio de suelos en Colombia, con especial énfasis en los cultivos prioritarios del departamento de **Risaralda**.

---

## 🏗️ 2. Arquitectura de Software

El sistema implementa una arquitectura modular de tres capas/componentes desacoplados:

```
proyecto_suelos/
├── api/
│   ├── __init__.py
│   └── data_service.py       # Lógica de negocio, limpieza de datos y cálculos
├── ui/
│   ├── __init__.py
│   └── cli_view.py           # Interfaz de usuario por consola y renderizado de tablas
├── data/
│   └── resultado_laboratorio_suelo.xlsx  # Dataset oficial de análisis de suelo
├── docs/
│   └── Proyecto_1_progra_4.tex           # Informe académico en LaTeX
├── Images/
│   └── arq_proyecto.png      # Diagrama de estructura base
├── tests/
│   ├── __init__.py
│   └── test_api.py           # Suite de pruebas unitarias
├── main.py                   # Orquestador y punto de entrada
├── requirements.txt          # Dependencias de producción
├── .gitignore                # Exclusión de archivos temporales y entornos virtuales
└── README.md                 # Documentación técnica completa
```

### Descripción de Módulos:
1. **Módulo API (`api/`):**
   - Consume el archivo de datos `resultado_laboratorio_suelo.xlsx`.
   - Aplica filtros por Departamento, Municipio y Cultivo (insensible a mayúsculas y acentos).
   - Implementa algoritmos de limpieza de datos para tratar anomalías del dataset (símbolos `<`/`>`, fechas erróneas en pH y normalización de escalas).
   - Calcula la **mediana estadística exacta** de pH, Fósforo (Bray II mg/kg) y Potasio (cmol(+)/kg).
   - Utiliza almacenamiento en caché tipo Parquet para lograr respuestas en **milisegundos**.

2. **Módulo UI (`ui/`):**
   - Maneja la interacción con el usuario en terminal.
   - Valida entradas interactivas (evita campos vacíos y fuerza enteros positivos en límites).
   - Renderiza tablas estructuradas con formato amigable en consola y compatibilidad garantizada en Windows PowerShell / Linux / macOS.

3. **Punto de Entrada (`main.py`):**
   - Orquesta la conexión entre `ui` y `api`.
   - Soporta modo interactivo estándar y modo por parámetros de línea de comandos (`argparse`).

---

## 🚀 3. Instalación y Puesta en Marcha

### Prerrequisitos
- Python 3.10 o superior instalado.
- Administrador de paquetes `pip`.

### Paso 1: Clonar el repositorio
```bash
git clone <URL_DE_TU_REPOSITORIO>
cd proyecto_suelos
```

### Paso 2: Crear y activar un entorno virtual (Opcional pero recomendado)
En Windows:
```powershell
python -m venv venv
.\venv\Scripts\activate
```

En Linux/macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 💻 4. Modo de Uso

### Modo 1: Interactivo (Por defecto)
Ejecute el archivo principal:
```bash
python main.py
```
El sistema le solicitará interactivamente:
1. **Departamento:** (ej. `Risaralda`)
2. **Municipio:** (ej. `Pereira`, `Balboa`, `Santa Rosa`)
3. **Cultivo:** (ej. `Café`, `Aguacate`, `Caña panelera/azucar`)
4. **Número de registros a consultar:** (ej. `5`)

### Modo 2: Por argumentos de línea de comandos (CLI Flags)
Permite realizar consultas directas automatizadas:
```bash
python main.py -d "Risaralda" -m "Pereira" -c "Aguacate" -l 5
```
```bash
python main.py -d "Risaralda" -m "Balboa" -c "Caña" -l 5
```
```bash
python main.py -d "Risaralda" -m "Santa Rosa" -c "Café" -l 3
```

---

## 📊 5. Ejemplo de Salida en Consola

```text
==============================================================================
   UNIVERSIDAD TECNOLÓGICA DE PEREIRA - INGENIERÍA DE SISTEMAS Y COMPUTACIÓN
                 PROGRAMACIÓN IV - DOCENTE: ALEJANDRO RODAS VÁSQUEZ
             SISTEMA DE CONSULTA DE VARIABLES EDÁFICAS EN SUELOS
==============================================================================

==============================================================================
  RESULTADOS DE LA CONSULTA (5 registro(s) visualizado(s))
==============================================================================

+----------------+-------------+----------------------+--------------+--------------+-------------------+-----------------+
| Departamento   | Municipio   | Cultivo              | Topografía   |   Mediana pH | Mediana P         | Mediana K       |
|                |             |                      |              |              | (Bray II mg/kg)   | (cmol(+)/kg)    |
+================+=============+======================+==============+==============+===================+=================+
| RISARALDA      | BALBOA      | Caña panelera/azucar | Plano        |         6.55 | 49.28             | 0.267           |
| RISARALDA      | BALBOA      | Caña panelera/azucar | Plano        |         6.55 | 49.28             | 0.267           |
| RISARALDA      | BALBOA      | Caña panelera/azucar | Plano        |         6.55 | 49.28             | 0.267           |
| RISARALDA      | BALBOA      | Caña panelera/azucar | Plano        |         6.55 | 49.28             | 0.267           |
| RISARALDA      | BALBOA      | Caña panelera/azucar | Plano        |         6.55 | 49.28             | 0.267           |
+----------------+-------------+----------------------+--------------+--------------+-------------------+-----------------+

------------------------------------------------------------------------------
  RESUMEN ESTADÍSTICO DE VARIABLES EDÁFICAS DEL CULTIVO CONSULTADO:
    * Mediana pH:       6.55
    * Mediana Fósforo:  49.28 mg/kg
    * Mediana Potasio:  0.267 cmol(+)/kg
------------------------------------------------------------------------------
```

---

## 🧪 6. Ejecución de Pruebas Unitarias

Para comprobar la integridad del software y el cumplimiento de los cálculos:
```bash
python -m unittest tests/test_api.py
```
**Salida esperada:**
```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.174s

OK
```

---

## 📚 7. Fundamento Teórico: Arquitectura de Software y Diagramas de Componentes

### 1. ¿Qué es un Componente?
En el estándar UML (*Unified Modeling Language*), un **componente** es una parte modular, encapsulada y reemplazable de un sistema que oculta los detalles internos de su implementación y expone un conjunto de interfaces bien definidas. Un componente representa una unidad autónoma de código ejecutable o lógica de negocio (por ejemplo, el módulo `api` o el módulo `ui`).

### 2. ¿Qué es un Diagrama de Componentes?
Es un diagrama estructural dentro de UML que modela la organización física y lógica de los componentes de software, sus dependencias mutuas, interfaces suministradas y requeridas, y artefactos de despliegue.

### 3. ¿Para qué se utiliza?
- **Visualización de la Arquitectura:** Permite a los desarrolladores y arquitectos comprender la estructura de alto nivel del sistema sin perderse en el código fuente.
- **Verificación de la Modularidad:** Comprueba el bajo acoplamiento y la alta cohesión entre subsistemas.
- **Mantenibilidad y Reemplazabilidad:** Garantiza que un componente (ej. reemplazar la interfaz de consola `ui` por una interfaz web o gráfica) pueda sustituirse sin afectar al componente de lógica (`api`).
- **Planificación de Integración y Pruebas:** Facilita la definición de pruebas de integración y contratos entre módulos.

---

## 👨‍💻 Autor y Licencia
- **Estudiante:** Proyecto Académico de Programación IV
- **Institución:** Universidad Tecnológica de Pereira (UTP)
- **Licencia:** MIT License
