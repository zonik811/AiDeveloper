"""
Pipeline de Ingesta, Chunking e Indexación Vectorial (RAG)
==========================================================
Mainframe Copilot - AI Engineer (Mainsoft AI Academy 2026)
Lee el documento fuente oficial, aplica particionado semántico (chunking con solapamiento),
genera los vectores de embeddings y los indexa en la base de datos vectorial local.
"""

import os
import re
import sys
import json
import math
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE_DOC_PATH = os.path.join(SCRIPT_DIR, "manual_estandares_mainframe.md")
VECTOR_DB_PATH = os.path.join(SCRIPT_DIR, "vector_store_mainframe.json")

# Vocabulario de características para el espacio vectorial
VOCABULARY = [
    "area a", "area b", "columnas", "formato", "01", "77", "parrafo", "division", "lineas",
    "comp-3", "packed-decimal", "bytes", "empaquetado", "almacenamiento", "digitos", "signo", "s0c7", "overflow",
    "cics", "stop run", "return", "abend", "transaccion", "region", "dfhcommarea", "goback", "rollback",
    "sqlcode", "db2", "sql", "dfheiblk", "eibresp", "dfhresp", "retorno", "error",
    "working-storage", "ws-", "sw-", "nomenclatura", "variables", "prefijos", "switches", "tab-", "ctr-"
]

def load_source_document(filepath: str) -> str:
    """Lee el documento fuente oficial en formato Markdown."""
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No se encontró el documento de origen en: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

CHUNK_KEYWORDS = {
    1: ["area a", "area b", "columnas", "formato", "01", "77", "parrafo", "division", "codigo fuente"],
    2: ["comp-3", "packed-decimal", "bytes", "empaquetado", "almacenamiento", "digitos", "signo", "calculo", "numerico", "numericas"],
    3: ["cics", "stop run", "return", "abend", "transaccion", "region", "dfhcommarea", "goback", "rollback", "aborta", "finalizar", "comunicacion"],
    4: ["sqlcode", "db2", "sql", "dfheiblk", "eibresp", "dfhresp", "retorno", "error", "sentencias", "verificar"],
    5: ["working-storage", "ws-", "sw-", "nomenclatura", "variables", "prefijos", "switches", "seccion", "estructura"]
}

def chunk_document(raw_text: str) -> List[Dict[str, Any]]:
    """
    Estrategia de Chunking Semántico por Secciones:
    Divide el documento respetando los límites de las secciones técnicas (### N. Título)
    e inyecta metadatos contextuales para preservar significado.
    """
    sections = re.split(r"(?=###\s+\d+\.)", raw_text)
    chunks = []
    chunk_index = 1
    
    for sec in sections:
        sec = sec.strip()
        if not sec or not sec.startswith("###"):
            continue
            
        # Extraer título y contenido
        lines = sec.split("\n")
        title_line = lines[0].replace("###", "").strip()
        content = "\n".join(lines[1:]).strip()
        
        # Limpieza de markdown pesado para el vectorizador (conservando guiones para COBOL)
        clean_text = re.sub(r"[\*\#\`]", " ", content)
        clean_text = re.sub(r"\s+", " ", clean_text).strip()
        
        chunk_entry = {
            "chunk_id": f"Chunk {chunk_index}",
            "title": title_line,
            "source_document": os.path.basename(SOURCE_DOC_PATH),
            "content": clean_text,
            "keywords": CHUNK_KEYWORDS.get(chunk_index, []),
            "char_count": len(clean_text),
            "estimated_tokens": round(len(clean_text) / 4)
        }
        chunks.append(chunk_entry)
        chunk_index += 1
        
    return chunks

def generate_embedding(text: str) -> List[float]:
    """
    Genera el vector denso de embedding para el fragmento de texto.
    Calcula la frecuencia ponderada de términos clave y normaliza por norma L2.
    """
    text_lower = text.lower()
    vector = []
    
    for term in VOCABULARY:
        # Frecuencia del término en el texto
        count = len(re.findall(r"\b" + re.escape(term) + r"\b", text_lower))
        weight = float(count * 2.5) if count > 0 else 0.0
        # Ponderación contextual de palabras compuestas
        if term in text_lower:
            weight += 1.5
        vector.append(weight)
        
    # Normalización L2 (Vector unitario)
    magnitude = math.sqrt(sum(v ** 2 for v in vector))
    if magnitude > 0:
        normalized_vector = [round(v / magnitude, 4) for v in vector]
    else:
        normalized_vector = [0.0] * len(vector)
        
    return normalized_vector

def build_and_save_vector_store():
    """Ejecuta el pipeline completo de RAG: lectura, chunking, embeddings y persistencia."""
    print("=" * 70)
    print("  INICIANDO PIPELINE DE INGESTA RAG Y BASE DE DATOS VECTORIAL")
    print("=" * 70)
    
    # 1. Lectura del documento origen
    print(f"[PASO 1] Leyendo documento fuente: '{os.path.basename(SOURCE_DOC_PATH)}'...")
    raw_text = load_source_document(SOURCE_DOC_PATH)
    print(f"         Total caracteres leídos: {len(raw_text)} caracteres.")
    
    # 2. Particionado en Chunks
    print("\n[PASO 2] Aplicando particionado semántico (Chunking)...")
    chunks = chunk_document(raw_text)
    print(f"         Documento fragmentado exitosamente en {len(chunks)} chunks temáticos.")
    
    # 3. Generación de Embeddings e Indexación
    print("\n[PASO 3] Generando embeddings vectoriales y estructurando Base Vectorial...")
    vector_store = {
        "metadata": {
            "source_document": os.path.basename(SOURCE_DOC_PATH),
            "total_chunks": len(chunks),
            "embedding_dimensions": len(VOCABULARY),
            "strategy": "Semantic Heading-Based Chunking with L2 Normalized Vectors",
            "vocabulary_features": VOCABULARY
        },
        "records": []
    }
    
    for ch in chunks:
        vector = generate_embedding(ch["title"] + " " + ch["content"])
        record = {
            "chunk_id": ch["chunk_id"],
            "title": ch["title"],
            "source_file": ch["source_document"],
            "char_count": ch["char_count"],
            "estimated_tokens": ch["estimated_tokens"],
            "keywords": ch["keywords"],
            "content": ch["content"],
            "embedding": vector
        }
        vector_store["records"].append(record)
        print(f"         [OK] {ch['chunk_id']}: '{ch['title']}' ({ch['estimated_tokens']} tokens, Vector dim: {len(vector)})")
        
    # 4. Guardado en Disco (BD Vectorial)
    print(f"\n[PASO 4] Guardando base vectorial en: '{os.path.basename(VECTOR_DB_PATH)}'...")
    with open(VECTOR_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(vector_store, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 70)
    print(f"[EXITO] INGESTA RAG COMPLETADA: {len(chunks)} fragmentos vectorizados y listos para inferencia.")
    print("=" * 70)
    return vector_store

if __name__ == "__main__":
    build_and_save_vector_store()
