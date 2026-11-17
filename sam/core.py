"""SAM 0.2: ciclo IA real, verificadores deterministas y cápsulas candidatas.
Sin dependencias Python externas. No modifica automáticamente el conocimiento canónico.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json
import re
import subprocess
import unicodedata

CANONICAL_PROJECT = "SAM-CORE"
PENDING = "CANDIDATE_PENDING_TCSA"

def digest_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def normalizar(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^\w ]", " ", value)).strip()

def respuesta_estructurada(texto: str) -> str | None:
    # La línea debe ser RESPUESTA: ...; el resto no sirve como prueba.
    for linea in reversed(texto.splitlines()):
        match = re.match(r"^\s*RESPUESTA\s*:\s*(.*?)\s*$", linea, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def evaluar(respuesta: str | None, referencia: str | None) -> dict:
    """Prueba estrecha: equivalencia literal tras normalización, nunca validez general."""
    if not respuesta or not referencia:
        return {"verificada": False, "motivo": "sin respuesta estructurada o sin referencia"}
    verificada = normalizar(respuesta) == normalizar(referencia)
    return {"verificada": verificada,
            "motivo": "coincidencia exacta normalizada" if verificada else "diferente de referencia; sin aprobación"}

@dataclass(frozen=True)
class Modelo:
    nombre: str
    ruta: str

class LlamaCLI:
    """Ejecutor subprocess para GGUF locales con llama.cpp; NO consume APIs."""
    def __init__(self, ejecutable: str, timeout: int = 240, max_tokens: int = 96):
        self.ejecutable = ejecutable
        self.timeout = timeout
        self.max_tokens = max_tokens

    def generar(self, modelo: Modelo, instrucciones: str, pregunta: str) -> str:
        # Plantilla explícita compatible con Qwen2.5 y Qwen3 instruct.
        prompt = ("<|im_start|>system\n" + instrucciones + "\n/no_think\n<|im_end|>\n"
                  "<|im_start|>user\n" + pregunta + "\n<|im_end|>\n<|im_start|>assistant\n")
        comando = [
            self.ejecutable, "-m", modelo.ruta, "-p", prompt,
            "-n", str(self.max_tokens), "-c", "2048",
            "--temp", "0.2", "--no-display-prompt", "--no-perf", "--no-warmup"
        ]
        proceso = subprocess.run(comando, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace",
                                 timeout=self.timeout, check=False)
        if proceso.returncode != 0:
            raise RuntimeError(f"{modelo.nombre}: llama-cli rc={proceso.returncode}: {proceso.stderr[-600:]}")
        salida = proceso.stdout.strip()
        if not salida:
            raise RuntimeError(f"{modelo.nombre}: respuesta vacía")
        return salida[:4000]

def ciclo_dos_modelos(backend: LlamaCLI, creador: Modelo, critico: Modelo,
                      pregunta: str, referencia: str | None = None) -> dict:
    """Constructor -> crítico -> constructor. El crítico NO recibe la referencia."""
    normas = ("Eres SAM, un investigador en español. No inventes certezas. "
              "Razona entre dominios cuando aporte utilidad, señala supuestos. "
              "Da AL FINAL una línea exactamente 'RESPUESTA: valor'. "
              "La respuesta final debe ser breve y comprobable.")
    inicial = backend.generar(creador, normas, pregunta)
    revision = backend.generar(
        critico,
        "Eres crítico independiente de SAM. Busca errores, supuestos falsos y contraejemplos. "
        "No te conformes con opiniones; da objeciones concretas. Sé breve.",
        "Problema:\n" + pregunta + "\nPropuesta del creador:\n" + inicial)
    final = backend.generar(
        creador, normas,
        "Problema:\n" + pregunta + "\nTu primera propuesta:\n" + inicial +
        "\nRevisión crítica independiente:\n" + revision +
        "\nCorrige solo con argumentos verificables; termina con RESPUESTA:")
    antes = evaluar(respuesta_estructurada(inicial), referencia)
    despues = evaluar(respuesta_estructurada(final), referencia)
    return {
        "creador": creador.nombre, "critico": critico.nombre, "pregunta": pregunta,
        "primera_propuesta": inicial, "critica": revision, "propuesta_revisada": final,
        "respuesta_inicial": respuesta_estructurada(inicial),
        "respuesta_final": respuesta_estructurada(final),
        "evaluacion_inicial": antes, "evaluacion_final": despues,
        "mejora_verificada": bool(not antes["verificada"] and despues["verificada"]),
        "nota": "La comparación literal es limitada; no demuestra comprensión general ni entrenamiento neuronal."
    }

def capsula_candidata(caso_id: str, ciclo: dict, referencia: str, fuente: str) -> dict | None:
    if not ciclo["evaluacion_final"]["verificada"]:
        return None
    return {
        "schema": "sam.capsula.v0", "id": caso_id,
        "estado": PENDING, "tcsa_project": CANONICAL_PROJECT,
        "objetivo": ciclo["pregunta"], "respuesta": ciclo["respuesta_final"],
        "referencia": referencia, "fuente": fuente,
        "verificacion": ciclo["evaluacion_final"]["motivo"],
        "confianza": "solo comprobación literal estrecha",
        "restricciones": "No entrenar, publicar como verdad universal ni promover sin evaluación TCSA",
        "version_requerida": "revisión canónica TCSA3000"
    }

def informe(modo: str, casos: list[dict], modelo_a: Modelo, modelo_b: Modelo,
            backend: LlamaCLI, fuente: str) -> dict:
    if modo not in {"trabajo", "evolucion"}:
        raise ValueError("Modo no reconocido")
    resultados, capsulas = [], []
    for caso in casos:
        ciclo = ciclo_dos_modelos(backend, modelo_a, modelo_b, caso["prompt"], caso.get("expected"))
        ciclo["case_id"] = caso["id"]
        resultados.append(ciclo)
        if modo == "evolucion" and caso.get("expected"):
            capsula = capsula_candidata(caso["id"], ciclo, caso["expected"], fuente)
            if capsula:
                capsulas.append(capsula)
    return {
        "schema": "sam.run.v0", "version": "0.2.0", "modo": modo,
        "utc": datetime.now(timezone.utc).isoformat(), "tcsa_project": CANONICAL_PROJECT,
        "estado_canonico": PENDING,
        "modelos": [{"nombre": m.nombre, "sha256_gguf": digest_file(m.ruta)}
                    for m in (modelo_a, modelo_b)],
        "casos": resultados, "capsulas_candidatas": capsulas,
        "resumen": {"ejercicios": len(resultados),
                    "evaluaciones_literales_aprobadas": sum(x["evaluacion_final"]["verificada"] for x in resultados),
                    "mejoras_literales": sum(x["mejora_verificada"] for x in resultados)},
        "advertencia": "Las ejecuciones en GitHub no son canónicas hasta reconciliarse con TCSA3000; no hay entrenamiento de pesos."
    }
