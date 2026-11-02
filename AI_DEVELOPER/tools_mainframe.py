"""
Definición e Implementación de Herramientas del Agente (Tool Calling)
=====================================================================
Mainframe Copilot - AI Engineer (Mainsoft AI Academy 2026)
Esquemas JSON formales compatibles con el estándar de Anthropic Tool Use / MCP
y funciones de ejecución del agente para diagnóstico en Mainframe.
"""

import sys
import json
from typing import Dict, Any, List

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# =====================================================================
# ESQUEMAS FORMALES JSON SCHEMA DE HERRAMIENTAS (ANTHROPIC TOOL USE)
# =====================================================================
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "name": "consultar_estado_job_batch",
        "description": (
            "Consulta el catálogo del spool JES2 en z/OS para obtener el estado de ejecución, "
            "código de ABEND, programa fallido, línea de código afectada y mensaje de diagnóstico de un JOB batch."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "Identificador único del JOB batch en JES2 (ej. 'JOB_PAGOS_01', 'JOB_EXTR_02')."
                }
            },
            "required": ["job_id"]
        }
    },
    {
        "name": "analizar_impacto_compilacion",
        "description": (
            "Calcula el tiempo estimado de compilación y determina el nivel de riesgo transaccional "
            "para la región CICS en base a la cantidad de líneas de código COBOL modificadas."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "programa": {
                    "type": "string",
                    "description": "Nombre del archivo o módulo COBOL a compilar (ej. 'PGMBANC1.cbl')."
                },
                "lineas": {
                    "type": "integer",
                    "description": "Número de líneas de código modificadas en el programa."
                }
            },
            "required": ["programa", "lineas"]
        }
    }
]

# Base de datos simulada de Jobs en ejecución
MOCK_BATCH_JOBS_DB = {
    "JOB_PAGOS_01": {
        "job_id": "JOB_PAGOS_01",
        "status": "ABENDED",
        "abend_code": "S0C7",
        "program": "PGMBANC1.cbl",
        "failed_line": 45,
        "error_message": "Data exception on PACKED-DECIMAL calculation in WS-MONTO-TOTAL (COMP-3 byte overflow)",
        "timestamp": "2026-11-02 03:14:22"
    },
    "JOB_EXTR_02": {
        "job_id": "JOB_EXTR_02",
        "status": "COMPLETED",
        "abend_code": "0000",
        "program": "PGMEX02.cbl",
        "failed_line": None,
        "error_message": "Ejecución exitosa, 12050 registros procesados",
        "timestamp": "2026-11-02 04:00:10"
    }
}

# =====================================================================
# HANDLERS DE EJECUCIÓN DE LAS HERRAMIENTAS
# =====================================================================
def consultar_estado_job_batch(job_id: str) -> Dict[str, Any]:
    """Ejecuta la consulta en el catálogo JES2."""
    job_id_clean = job_id.strip().upper()
    if job_id_clean in MOCK_BATCH_JOBS_DB:
        return {
            "success": True,
            "job_id": job_id_clean,
            "data": MOCK_BATCH_JOBS_DB[job_id_clean]
        }
    return {
        "success": False,
        "error": f"El JOB '{job_id}' no fue encontrado en el catálogo de ejecuciones activas de JES2."
    }

def analizar_impacto_compilacion(programa: str, lineas: int) -> Dict[str, Any]:
    """Calcula métricas de compilación y riesgo en CICS."""
    riesgo = "BAJO"
    if lineas > 500:
        riesgo = "ALTO"
    elif lineas > 100:
        riesgo = "MEDIO"
    
    tiempo_est_segundos = round(lineas * 0.08 + 2.5, 2)
    return {
        "success": True,
        "programa": programa,
        "lineas_modificadas": lineas,
        "tiempo_compilacion_estimado_s": tiempo_est_segundos,
        "nivel_riesgo_cics": riesgo,
        "requiere_ventana_mantenimiento": (riesgo == "ALTO")
    }

def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Despachador central de herramientas (Tool Dispatcher)."""
    if tool_name == "consultar_estado_job_batch":
        return consultar_estado_job_batch(arguments.get("job_id", ""))
    elif tool_name == "analizar_impacto_compilacion":
        return analizar_impacto_compilacion(arguments.get("programa", ""), int(arguments.get("lineas", 0)))
    else:
        return {"success": False, "error": f"Herramienta desconocida: '{tool_name}'"}

def print_tools_catalog():
    """Imprime el catálogo formal de herramientas para auditoría o demo."""
    print("=" * 70)
    print("  CATÁLOGO DE HERRAMIENTAS DEL AGENTE (ANTHROPIC TOOL SCHEMAS)")
    print("=" * 70)
    for tool in TOOL_SCHEMAS:
        print(f"\n[TOOL]: {tool['name']}")
        print(f"Descripción: {tool['description']}")
        print("Esquema de Entrada (Input JSON Schema):")
        print(json.dumps(tool["input_schema"], indent=2))
        print("-" * 70)

if __name__ == "__main__":
    print_tools_catalog()
