"""SAM R008: detectar fallos recurrentes y producir módulos de estrategia candidatos.

Dos modelos sugieren y critican estrategias; sólo se genera código de un
catálogo revisado. Nunca se ejecuta código de salida del LLM ni se cambia main.
Las pruebas son exploratorias y NO constituyen generalización certificada.
"""
from __future__ import annotations

import ast
from collections import defaultdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

from .core import PENDING, evaluar, respuesta_estructurada
from .quality import es_reservada
from .strategy_eval import INSTRUCCIONES as ESTRATEGIAS_ACTUALES
from .diversity import seleccionar_diverso

# Solamente estrategias con texto revisado y código generado determinísticamente.
ESTRATEGIAS = {
    "descomponer": (
        "Descompón el problema en pasos independientes; verifica cada cálculo y "
        "sus unidades antes de responder. No inventes datos. "
        "Termina con una línea RESPUESTA: resultado."
    ),
    "refutar": (
        "Propón una solución provisional, busca un contraejemplo y comprueba "
        "qué supuestos podrían fallar. Corrige los errores antes de responder. "
        "Termina con una línea RESPUESTA: resultado."
    ),
    "interdominios": (
        "Busca una analogía con otra disciplina, explica qué mecanismo es "
        "transferible y qué límites lo invalidarían. Si no ayuda, resuelve "
        "directamente. Termina con una línea RESPUESTA: resultado."
    ),
    "unidades": (
        "Revisa dimensiones físicas, conversiones, fórmulas y el significado "
        "de cada variable. Descartar analogías sin respaldo. "
        "Termina con una línea RESPUESTA: resultado."
    ),
}


def detectar_fallos(memoria, *, minimo: int = 2) -> list[dict]:
    """Sólo práctica exacta: nunca usar holdout ni tareas de revisión humana."""
    if minimo < 2:
        raise ValueError("Se exigen dos errores diferentes como mínimo")
    grupos = defaultdict(lambda: {"errores":set(), "intentos":0, "aciertos":0})
    cursor = memoria.con.execute(
        "SELECT task_id,domain,skill,correct,outcome,payload_json FROM intentos"
    )
    for task_id,domain,skill,correct,outcome,payload_json in cursor:
        if es_reservada(task_id) or outcome == "error":
            continue
        try:
            payload = json.loads(payload_json)
        except (TypeError, ValueError):
            continue
        if (payload.get("evaluation_set") == "holdout"
                or payload.get("grade") != "exact"):
            continue
        row = grupos[(domain,skill)]
        row["intentos"] += 1
        if correct:
            row["aciertos"] += 1
        else:
            row["errores"].add(task_id)
    resultados=[]
    for (domain,skill),data in grupos.items():
        distinct=len(data["errores"])
        if distinct >= minimo:
            resultados.append({
                "dominio":domain,"habilidad":skill,
                "fallos_en_tareas_distintas":distinct,
                "intentos":data["intentos"],"aciertos":data["aciertos"],
            })
    resultados.sort(key=lambda x:(-x["fallos_en_tareas_distintas"],
                                   x["dominio"],x["habilidad"]))
    return resultados


def _identificar(texto: str) -> str | None:
    m=re.search(r"(?im)^\s*ESTRATEGIA\s*:\s*([a-z_]+)\s*$",texto)
    return m.group(1) if m and m.group(1) in ESTRATEGIAS else None


def _predeterminada(dominio: str) -> str:
    return "unidades" if dominio in ("fisica","quimica") else "descomponer"


def codigo_candidato(estrategia: str) -> str:
    """Genera código simple desde un catálogo fijo, sin texto ejecutable del LLM."""
    if estrategia not in ESTRATEGIAS:
        raise ValueError("Estrategia fuera del catálogo")
    source=(
        '"""Módulo candidato SAM: no instalado, no aprobado, no autoejecutable."""\n'
        f'ESTRATEGIA = {estrategia!r}\n'
        f'INSTRUCCIONES = {ESTRATEGIAS[estrategia]!r}\n\n'
        'def instrucciones():\n'
        '    return INSTRUCCIONES\n'
    )
    ast.parse(source)
    # Las entradas provienen solo del catálogo de strings fijo, no del LLM.
    return source


def experimentar(memoria, tareas_practica: list, modelos: tuple,
                 backend, *, max_cases: int = 2) -> dict:
    """Dos modelos proponen/critican; evaluador compara tareas de práctica NUEVAS."""
    if not 1 <= max_cases <= 4 or len(modelos) != 2:
        raise ValueError("Parámetros fuera de límites")
    result={
        "schema":"sam.self_evolve.v1",
        "utc":datetime.now(timezone.utc).isoformat(),
        "estado":PENDING,
        "promotion":"BLOQUEADA_HASTA_REVISION_TCSA",
        "codigo_ejecutado":False,
        "modo":"EVOLUCION_AISLADA",
        "evaluacion":"PRACTICA_NO_VISTA_EN_MEMORIA_NO_HOLDOUT",
    }
    errores=detectar_fallos(memoria)
    result["focos_errores"]=errores[:8]
    if not errores:
        result["resultado"]="SIN_ERRORES_RECURRENTES_SUFICIENTES"
        return result
    history=memoria.estadisticas()
    # Buscar foco con datos de práctica exactos aún no ensayados; preservar holdout.
    elegido=None
    tareas=[]
    for foco in errores:
        pool=[t for t in tareas_practica
              if t.domain==foco["dominio"] and t.skill==foco["habilidad"]
              and t.grade=="exact" and t.expected is not None
              and not es_reservada(t.id)
              and history.get(t.id,{"intentos":0})["intentos"]==0]
        if len(pool)>=max_cases:
            elegido=foco
            tareas=seleccionar_diverso(pool,{},max_cases,0)
            break
    if elegido is None:
        result["resultado"]="SIN_CASOS_NUEVOS_PARA_COMPARAR"
        return result
    result["foco"]=elegido
    listado=", ".join(ESTRATEGIAS)
    descripcion=(
        "SAM falló en la materia "+elegido["dominio"]+
        ", habilidad "+elegido["habilidad"]+
        ", en "+str(elegido["fallos_en_tareas_distintas"])+
        " ejercicios de práctica distintos. No tienes respuestas de referencia. "
        "Selecciona una estrategia de la lista: "+listado+
        ". Devuelve sólo ESTRATEGIA: nombre."
    )
    proponente,critico=modelos
    sugerencia=backend.generar(
        proponente,
        "Eres el diseñador de métodos de SAM. Elige una estrategia del catálogo, "
        "nunca código, comandos o permisos. Responde ESTRATEGIA: nombre.",
        descripcion)
    estrategia=_identificar(sugerencia)
    origen="MODELO" if estrategia else "REGLA_DE_RESPALDO"
    if estrategia is None:
        estrategia=_predeterminada(elegido["dominio"])
    objecion=backend.generar(
        critico,
        "Eres crítico independiente de estrategias. Cuestiona la utilidad, "
        "sesgos y limitaciones. No produces código ni órdenes. Responde breve.",
        "Problema: "+descripcion+"\nEstrategia candidata: "+estrategia)
    codigo=codigo_candidato(estrategia)
    hash_code=sha256(codigo.encode("utf-8")).hexdigest()
    result["propuesta"]={
        "estrategia":estrategia, "origen":origen,
        "modelo_proponente":proponente.nombre,
        "modelo_critico":critico.nombre,
        "sugerencia_cruda":sugerencia[:500],
        "critica":objecion[:1000],
        "sha256_codigo":hash_code,
        "archivo":"auto-propuestas/"+hash_code[:16]+".py",
        "estado":"CANDIDATO_NO_APROBADO",
    }
    # No se ejecuta codigo_candidato. Se compara la instrucción conocida
    # que ese código devolvería si se aprobara e instalara en el futuro.
    resultados=[]
    score={"actual":0,"candidato":0}
    for i,t in enumerate(tareas):
        model=modelos[i%2]
        por_metodo={}
        for metodo,instr in (("actual",ESTRATEGIAS_ACTUALES["directa"]),
                             ("candidato",ESTRATEGIAS[estrategia])):
            output=backend.generar(model,instr,t.prompt)
            answer=respuesta_estructurada(output)
            ok=evaluar(answer,t.expected)["verificada"]
            por_metodo[metodo]={
                "modelo":model.nombre,"respuesta":answer,
                "coincidencia_exacta":ok,
            }
            score[metodo]+=int(ok)
        resultados.append({"id":t.id,"dominio":t.domain,"habilidad":t.skill,
                           "resultados":por_metodo})
    result["casos"]=resultados
    result["resumen"]={
        "ejercicios":len(tareas),
        "aciertos_actual":score["actual"],"aciertos_candidato":score["candidato"],
        "diferencia":score["candidato"]-score["actual"],
    }
    result["resultado"]=("MEJORA_EXPLORATORIA_CANDIDATA"
        if score["candidato"]>score["actual"] else
        "SIN_MEJORA_DEMOSTRADA_EN_ESTE_LOTE")
    result["advertencia"]=(
        "Se genera Python desde catálogo fijo y no se ejecuta. "
        "Casos de práctica no vistos por memoria, pero currículo público; "
        "los modelos no han cambiado sus pesos y no se autoriza promoción."
    )
    return result


def guardar_candidato(informe: dict, directorio: str | Path) -> dict:
    """Guarda JSON público y fichero .py SOLO candidato; ninguna promoción."""
    directorio=Path(directorio)
    directorio.mkdir(parents=True,exist_ok=True)
    propuesta=informe.get("propuesta")
    if propuesta:
        code=codigo_candidato(propuesta["estrategia"])
        if sha256(code.encode("utf-8")).hexdigest()!=propuesta["sha256_codigo"]:
            raise ValueError("Código candidato alterado")
        path=directorio/(propuesta["sha256_codigo"][:16]+".py")
        path.write_text(code,encoding="utf-8")
        compile(path.read_text(encoding="utf-8"),str(path),"exec")
    name="informe-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")+".json"
    path=directorio/name
    path.write_text(json.dumps(informe,ensure_ascii=False,sort_keys=True,indent=2)+"\n",
                    encoding="utf-8")
    return {"reporte":str(path),"codigo":propuesta["archivo"] if propuesta else None}
