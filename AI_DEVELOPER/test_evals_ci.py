"""
Pipeline de CI/CD - Evaluación Automatizada y Prevención de Regresiones (Evals)
=============================================================================
Tema 6 & Tema 8 & Tema 10 - AI Engineer (Mainsoft AI Academy)
Ejecuta el dataset de evaluación de arquitectura CICS y aplica un Quality Gate:
Si el accuracy es inferior al 90%, falla el build (sys.exit(1)).
"""

import sys
import os

# Asegurar import de mainframe_copilot
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mainframe_copilot import MainframeCopilotAgent

# DATASET DE EVALUACIÓN OFICIAL (10 Casos del Tema 6)
EVAL_DATASET = [
    {
        "id": "ID-01",
        "query": "¿Cómo debe finalizar la ejecución de un programa transaccional CICS que retorna el control a la región?",
        "expected_keywords": ["return", "cics"],
        "forbidden_keywords": ["stop run"],
        "category": "CICS Flow"
    },
    {
        "id": "ID-02",
        "query": "¿Qué área de comunicación se debe utilizar para transferir datos entre dos programas CICS llamados vía LINK o XCTL?",
        "expected_keywords": ["dfhcommarea"],
        "category": "CICS Memory"
    },
    {
        "id": "ID-03",
        "query": "¿Qué variable del bloque DFHEIBLK se debe evaluar inmediatamente después de ejecutar un comando CICS para verificar si hubo error?",
        "expected_keywords": ["eibresp", "dfhresp"],
        "category": "CICS Return Code"
    },
    {
        "id": "ID-04",
        "query": "¿Cómo se fuerza un rollback de memoria y se aborta una transacción de forma programada?",
        "expected_keywords": ["abend"],
        "category": "CICS Transaction"
    },
    {
        "id": "ID-05",
        "query": "¿Cuál es la regla de almacenamiento y cálculo de bytes en variables COMP-3?",
        "expected_keywords": ["comp-3", "bytes", "dígitos"],
        "category": "COBOL Data Types"
    },
    {
        "id": "ID-06",
        "query": "¿Cuáles son las reglas para el uso del Área A y Área B en el código fuente COBOL?",
        "expected_keywords": ["área a", "área b", "columnas"],
        "category": "Coding Standards"
    },
    {
        "id": "ID-07",
        "query": "¿Qué prefijos obligatorios deben llevar las variables en la WORKING-STORAGE SECTION?",
        "expected_keywords": ["ws-", "working-storage"],
        "category": "Naming Conventions"
    },
    {
        "id": "ID-08",
        "query": "¿Cuáles son los comandos para desplegar un clúster de microservicios con Docker en Windows Server?",
        "expected_out_of_domain": True,  # Debe rechazar responder por estar fuera de dominio
        "category": "Domain Boundaries (Trampa)"
    },
    {
        "id": "ID-09",
        "query": "El JOB_PAGOS_01 falló con error en el cálculo numérico. ¿Cuál es el diagnóstico?",
        "expected_keywords": ["s0c7", "pgmbanc1", "comp-3"],
        "category": "Agent & Tool Execution"
    },
    {
        "id": "ID-10",
        "query": "¿Qué código se debe verificar tras un EXEC SQL en DB2?",
        "expected_keywords": ["sqlcode", "db2"],
        "category": "Database DB2"
    }
]

def normalize_text(text: str) -> str:
    """Elimina tildes y caracteres especiales para validaciones robustas."""
    text = text.lower()
    replacements = (("á", "a"), ("é", "e"), ("í", "i"), ("ó", "o"), ("ú", "u"), ("ñ", "n"))
    for a, b in replacements:
        text = text.replace(a, b)
    return text

def run_evaluation_suite(min_score_percent: float = 90.0) -> bool:
    print("=" * 70)
    print("  EJECUTANDO EVALUACIONES CI/CD (EVALS - LLMOps QUALITY GATE)")
    print(f"  Dataset: {len(EVAL_DATASET)} casos | Umbral mínimo requerido: {min_score_percent}%")
    print("=" * 70)
    
    agent = MainframeCopilotAgent(user_id="ci_cd_runner")
    passed_cases = 0
    total_cases = len(EVAL_DATASET)
    
    for case in EVAL_DATASET:
        case_id = case["id"]
        query = case["query"]
        category = case["category"]
        
        result = agent.process_query(query)
        response_text = normalize_text(result.get("response", ""))
        passed = False
        reason = ""
        
        # Validación de caso fuera de dominio (Trampa)
        if case.get("expected_out_of_domain"):
            if "no dispongo de informacion" in response_text or "restringida a arquitectura" in response_text:
                passed = True
                reason = "Rechazó responder correctamente (bloqueó alucinación fuera de dominio)"
            else:
                passed = False
                reason = "Fallo de frontera: intentó responder sobre tecnologías ajenas"
        else:
            # Validación de keywords esperadas normalizadas
            norm_expected = [normalize_text(kw) for kw in case.get("expected_keywords", [])]
            exp_matches = [kw for kw in norm_expected if kw in response_text]
            
            # Caso especial ID-01: Prohíbe STOP RUN (debe advertir que está prohibido o exigir RETURN)
            if case_id == "ID-01":
                if "return" in response_text and ("prohibido" in response_text or "stop run" in response_text):
                    passed = True
                    reason = "Exige EXEC CICS RETURN y advierte restricción de STOP RUN"
                else:
                    passed = False
                    reason = "No especificó RETURN o la restricción de STOP RUN"
            else:
                if len(exp_matches) == len(norm_expected):
                    passed = True
                    reason = f"Contiene conceptos clave {exp_matches}"
                else:
                    passed = False
                    missing = [kw for kw in norm_expected if kw not in exp_matches]
                    reason = f"Faltan keywords requeridas: {missing}"
        
        status_icon = "PASS" if passed else "FAIL"
        if passed:
            passed_cases += 1
            
        print(f"[{status_icon}] {case_id} ({category}): {reason}")
    
    score_percentage = (passed_cases / total_cases) * 100
    print("\n" + "=" * 70)
    print(f"  RESULTADO FINAL: {passed_cases}/{total_cases} casos aprobados ({score_percentage:.1f}%)")
    print("=" * 70)
    
    if score_percentage >= min_score_percent:
        print("[OK] QUALITY GATE APROBADO: No se detectan regresiones. Autorizado para despliegue.")
        return True
    else:
        print("[ERROR] QUALITY GATE RECHAZADO: Calidad por debajo del umbral mínimo. Despliegue cancelado.")
        return False

if __name__ == "__main__":
    success = run_evaluation_suite()
    if not success:
        sys.exit(1)
    sys.exit(0)
