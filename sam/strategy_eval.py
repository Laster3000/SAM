"""Comparación reproducible de dos estrategias sin modificar pesos ni memoria.

El conjunto reservado nunca entra al contexto del modelo con respuestas.
La coincidencia literal es una prueba estrecha, NO certificación de inteligencia.
"""
from __future__ import annotations
from datetime import datetime, timezone
from .core import evaluar, respuesta_estructurada, PENDING
from .quality import es_reservada

INSTRUCCIONES = {
    "directa": (
        "Resuelve directamente el problema. Identifica lo necesario, calcula y "
        "comprueba. Termina con una línea RESPUESTA: resultado."
    ),
    "divergente": (
        "Explora al menos dos enfoques, incluido uno de analogía o transferencia "
        "entre disciplinas si puede aportar algo. Cuestiona supuestos, distingue "
        "límites reales de aparentes y verifica que la analogía se aplica. "
        "Elige la solución más justificada. Termina con RESPUESTA: resultado."
    ),
}


def comparar_estrategias(backend, modelos, tareas: list, *, max_cases: int = 2) -> dict:
    if not 1 <= max_cases <= 4:
        raise ValueError("Máximo 4 casos por ensayo comparativo en CI")
    if len(modelos) != 2 or not all(hasattr(m, "nombre") for m in modelos):
        raise ValueError("Se requieren exactamente dos modelos")
    elegidas = list(tareas)[:max_cases]
    if not elegidas or any(not es_reservada(t.id) or t.grade != "exact"
                          or t.expected is None for t in elegidas):
        raise ValueError("Usar únicamente casos exactos del conjunto reservado")
    out = {"schema":"sam.strategy_eval.v1","utc":datetime.now(timezone.utc).isoformat(),
           "estado":PENDING,"tipo":"comparacion_en_holdout_sin_memoria",
           "casos":[],"estrategias":list(INSTRUCCIONES)}
    resultados = {key:0 for key in INSTRUCCIONES}
    for i,task in enumerate(elegidas):
        creator = modelos[i % 2]
        case = {"id":task.id,"dominio":task.domain,"habilidad":task.skill,
                "resultados":{}}
        for strategy, instruction in INSTRUCCIONES.items():
            # La referencia solo se usa después de generar, nunca en instrucciones.
            text = backend.generar(creator, instruction, task.prompt)
            answer = respuesta_estructurada(text)
            verified = evaluar(answer, task.expected)
            case["resultados"][strategy] = {
                "modelo":creator.nombre, "respuesta":answer,
                "verificada_literalmente":verified["verificada"],
                "motivo":verified["motivo"],
            }
            resultados[strategy] += int(verified["verificada"])
        out["casos"].append(case)
    out["resumen"] = {"total":len(out["casos"]), "aciertos_literales":resultados,
                      "diferencia_divergente_menos_directa": (
                           resultados["divergente"] - resultados["directa"])}
    out["aviso"] = (
        "Ensayo de estrategias sobre casos exactos; no incorpora conocimiento, "
        "no cambia parámetros ni promueve propuestas. Holdout reservado al "
        "entrenamiento, pero su banco está publicado: NO prueba ciega externa."
    )
    return out
