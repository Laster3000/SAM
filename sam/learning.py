"""Memoria local, decisiones de currículo, sesiones y experimentos verificables.
La memoria de experiencias no modifica pesos ni promueve conocimiento por sí sola.
"""
from __future__ import annotations
import hashlib
import json
import math
import sqlite3
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from .core import Modelo, LlamaCLI, PENDING, ciclo_dos_modelos, capsula_candidata
from .curriculum import Tarea
from .quality import ejemplos_verificados, contexto_ejemplos

def canonical_json(x: dict) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

class Memoria:
    def __init__(self, raiz: str | Path):
        self.raiz=Path(raiz)
        self.raiz.mkdir(parents=True, exist_ok=True)
        self.con=sqlite3.connect(self.raiz/"aprendizaje.sqlite3", timeout=20)
        self.con.execute("PRAGMA journal_mode=WAL")
        self.con.execute("PRAGMA synchronous=FULL")
        self.con.execute("""CREATE TABLE IF NOT EXISTS intentos (
            evento_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            task_id TEXT NOT NULL,
            domain TEXT NOT NULL,
            skill TEXT NOT NULL,
            correct INTEGER NOT NULL,
            outcome TEXT NOT NULL,
            utc TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            canonical_status TEXT NOT NULL
        )""")
        self.con.execute("CREATE INDEX IF NOT EXISTS idx_case ON intentos(task_id)")
        self.con.commit()

    def cerrar(self):
        self.con.close()

    def importar_jsonl(self, fichero: str | Path):
        f=Path(fichero)
        if not f.exists():
            return 0
        n=0
        with f.open("r",encoding="utf-8") as h:
            for line in h:
                if not line.strip():
                    continue
                try:
                    e=json.loads(line)
                    self.con.execute("""INSERT OR IGNORE INTO intentos
                    (evento_id,run_id,task_id,domain,skill,correct,outcome,utc,payload_json,canonical_status)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (e["evento_id"],e["run_id"],e["task_id"],e["domain"],e["skill"],
                     int(e["correct"]),e["outcome"],e["utc"],canonical_json(e["payload"]),
                     PENDING))
                    n+=1
                except (KeyError,TypeError,ValueError):
                    raise ValueError("Historial mal formado, no importar como verdad")
        self.con.commit()
        return n

    def estadisticas(self) -> dict[str, dict]:
        rows=self.con.execute("SELECT task_id,COUNT(*),SUM(correct),MAX(utc) FROM intentos GROUP BY task_id")
        return {id_:{"intentos":n,"aciertos":ok,"ultimo":last} for id_,n,ok,last in rows}

    def elegir(self, tareas: list[Tarea], limite: int, ronda: int = 0) -> list[Tarea]:
        if not 1<=limite<=100:
            raise ValueError("Límite de tareas entre 1 y 100")
        stats=self.estadisticas()
        grupos=defaultdict(list)
        for t in tareas:
            m=stats.get(t.id,{"intentos":0,"aciertos":0,"ultimo":""})
            n=m["intentos"]; ok=m["aciertos"]
            # Novelas primero; después, repetir los fallos con prudencia.
            score=(n*10+(ok*3)-min(6,n-ok))
            grupos[t.domain].append((score,m["ultimo"],t.id,t))
        for v in grupos.values():
            v.sort(key=lambda x:(x[0],x[1],x[2]))
        keys=sorted(grupos)
        if not keys:
            raise ValueError("Currículo vacío")
        shift=ronda%len(keys)
        keys=keys[shift:]+keys[:shift]
        out=[]; usados=set()
        while len(out)<min(limite,len(tareas)):
            hubo=False
            for domain in keys:
                if grupos[domain]:
                    t=grupos[domain].pop(0)[-1]
                    if t.id in usados:
                        continue
                    out.append(t); usados.add(t.id); hubo=True
                    if len(out)>=limite: break
            if not hubo: break
        return out

    def agregar(self, run_id: str, task: Tarea, result: dict, *, success: bool,
                error: str | None = None, evaluation_set: str | None = None) -> dict:
        ts=datetime.now(timezone.utc).isoformat()
        event_id=hashlib.sha256((run_id+"|"+task.id).encode()).hexdigest()
        payload={"id":task.id,"domain":task.domain,"skill":task.skill,"grade":task.grade,
                 "prompt":task.prompt,"reference":task.expected,
                 "result":result,"error":error,"source":task.source}
        if evaluation_set:
            payload["evaluation_set"]=evaluation_set
        evento={
            "evento_id":event_id,"run_id":run_id,"task_id":task.id,
            "domain":task.domain,"skill":task.skill,
            "correct":bool(success),"outcome":"ok" if success else ("error" if error else "no_verificado"),
            "utc":ts,"payload":payload,
            "canonical_status":PENDING}
        try:
            self.con.execute("""INSERT INTO intentos
                 (evento_id,run_id,task_id,domain,skill,correct,outcome,utc,payload_json,canonical_status)
                 VALUES (?,?,?,?,?,?,?,?,?,?)""",
                 (event_id,run_id,task.id,task.domain,task.skill,
                  int(success),evento["outcome"],ts,canonical_json(payload),PENDING))
            self.con.commit()
            with (self.raiz/"eventos.jsonl").open("a",encoding="utf-8") as out:
                out.write(canonical_json(evento)+"\n")
                out.flush()
                import os
                os.fsync(out.fileno())
        except sqlite3.IntegrityError as exc:
            raise ValueError("Intento duplicado, no reejecutar sin reconciliar") from exc
        return evento

def ejecutar_sesion(memory: Memoria, tasks: list[Tarea], models: tuple[Modelo,Modelo],
                   backend: LlamaCLI, limit: int = 12, max_failures: int = 3,
                   *, holdout: bool = False) -> dict:
    run_id="sam-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")+"-"+uuid4().hex[:10]
    total=int(memory.con.execute("SELECT COUNT(DISTINCT run_id) FROM intentos").fetchone()[0])
    elegidas=memory.elegir(tasks,limit,total)
    reporte={"schema":"sam.learning_session.v1","run_id":run_id,
             "utc":datetime.now(timezone.utc).isoformat(),"mode":"EVOLUCION",
             "canonical_state":PENDING,"modelos":[x.nombre for x in models],
             "task_ids":[x.id for x in elegidas],"dataset":"holdout" if holdout else "practice","cases":[],
             "capsulas_candidatas":[],"errores":[]}
    failures=0
    for i,task in enumerate(elegidas):
        creator,critic=(models if i%2==0 else models[::-1])
        try:
            ejemplos=[] if holdout else ejemplos_verificados(memory,task)
            pregunta=task.prompt
            if ejemplos:
                pregunta+="\n\n"+contexto_ejemplos(ejemplos)
            result=ciclo_dos_modelos(backend,creator,critic,pregunta,
                                    task.expected if task.grade=="exact" else None)
            ok=bool(result["evaluacion_final"]["verificada"]) if task.grade=="exact" else False
            memory.agregar(run_id,task,result,success=ok,evaluation_set="holdout" if holdout else "practice")
            reporte["cases"].append({"task_id":task.id,"domain":task.domain,
                                     "skill":task.skill,"grade":task.grade,
                                     "correct":ok,"ejemplos_recuperados":len(ejemplos),"result":result})
            if ok and task.expected and task.grade=="exact":
                cap=capsula_candidata(task.id,result,task.expected,task.source)
                if cap: reporte["capsulas_candidatas"].append(cap)
        except Exception as exc:
            failures+=1
            memory.agregar(run_id,task,{},success=False,error=str(exc),evaluation_set="holdout" if holdout else "practice")
            reporte["errores"].append({"task_id":task.id,"error":str(exc)[:500]})
            if failures>=max_failures:
                reporte["interrumpida_por_fallos"]=True
                break
    reporte["resumen"]={
        "evaluadas":len(reporte["cases"]),"correctas_literalmente":sum(c["correct"] for c in reporte["cases"]),
        "no_verificadas":sum(c["grade"]!="exact" for c in reporte["cases"]),
        "errores":len(reporte["errores"]),"capsulas_candidatas":len(reporte["capsulas_candidatas"]),
        "cobertura":dict(Counter(x["domain"] for x in reporte["cases"]))}
    reporte["aviso"]="Experiencias y cápsulas pendientes de TCSA; no entrenan pesos ni certifican comprensión."
    return reporte
