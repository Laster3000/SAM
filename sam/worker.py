"""SAM autónomo local: ciclos recuperables hasta detenerlo o agotar recursos.
No se ejecuta sin un ordenador encendido ni llama.cpp y GGUF disponibles.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
import signal
import sys
import time
from .curriculum import cargar
from .core import Modelo, LlamaCLI, PENDING, digest_file
from .learning import Memoria, ejecutar_sesion
from .research import investigar_lote
from .quality import separar
from .diversity import seleccionar_diverso, cobertura
from .strategy_eval import comparar_estrategias

def ejecutar(argv=None):
    p=argparse.ArgumentParser(prog="python -m sam.worker",description="Worker SAM de evolución repetida")
    p.add_argument("--model-a")
    p.add_argument("--model-b")
    p.add_argument("--llama-cli",default="llama-cli")
    p.add_argument("--state",default=".sam-state")
    p.add_argument("--reports",default="resultados")
    p.add_argument("--eval-dir",default="evaluacion")
    p.add_argument("--batch",type=int,default=12)
    p.add_argument("--interval",type=int,default=20)
    p.add_argument("--max-cycles",type=int,default=0,
                   help="0: continuar hasta parada o guardarraíl")
    p.add_argument("--min-free-gb",type=float,default=1.0)
    p.add_argument("--max-state-mb",type=int,default=256)
    p.add_argument("--research-topics",type=int,default=0,help="Hasta 3 temas públicos por ciclo; sin certificación automática")
    p.add_argument("--holdout-cases",type=int,default=2,help="Casos ciegos por ciclo; nunca usan memoria")
    p.add_argument("--diverse",action="store_true",help="Rotar dominios y habilidades")
    p.add_argument("--strategy-cases",type=int,default=0,
                   help="Comparar razonamiento directo y divergente sobre hasta 4 casos reservados")
    p.add_argument("--dry-run",action="store_true")
    a=p.parse_args(argv)
    if a.batch<1 or a.batch>100 or a.interval<0 or a.min_free_gb<0.1 or a.max_state_mb<16 or not 0<=a.research_topics<=3 or not 0<=a.holdout_cases<=4 or not 0<=a.strategy_cases<=4:
        p.error("Parámetros fuera de límites")
    tareas=cargar(a.eval_dir)
    practica,reservadas=separar(tareas)
    if a.dry_run:
        resumen={}
        for t in tareas: resumen[t.domain]=resumen.get(t.domain,0)+1
        print(json.dumps({"curriculum_total":len(tareas),"train":len(practica),"holdout":len(reservadas),"dominios":resumen},ensure_ascii=False))
        return 0
    if not a.model_a or not a.model_b:
        p.error("Se requieren las rutas a dos modelos GGUF reales")
    for x in (a.model_a,a.model_b):
        if not Path(x).is_file():
            p.error("Modelo no encontrado: "+x)
    state=Path(a.state)
    reports=Path(a.reports)
    state.mkdir(parents=True,exist_ok=True)
    reports.mkdir(parents=True,exist_ok=True)
    mem=Memoria(state)
    # Recuperar estados de otras ejecuciones antes de elegir tareas.
    if (state/"importar-eventos.jsonl").exists():
        mem.importar_jsonl(state/"importar-eventos.jsonl")
    halt=[False]
    def parar(signum,frame): halt[0]=True
    for sig in (signal.SIGINT,signal.SIGTERM):
        try: signal.signal(sig,parar)
        except (ValueError,AttributeError): pass
    modelos=(Modelo("Qwen3-0.6B",a.model_a),
             Modelo("Qwen2.5-0.5B-Instruct",a.model_b))
    backend=LlamaCLI(a.llama_cli,timeout=240,max_tokens=120)
    contador=0
    failures=0
    try:
        while not halt[0] and (a.max_cycles==0 or contador<a.max_cycles):
            if (state/"STOP").exists():
                print("SAM_PAUSADO_MANUAL: fichero STOP detectado")
                break
            free=shutil.disk_usage(state).free/(1024**3)
            tam=sum(f.stat().st_size for f in state.glob("*") if f.is_file())/1048576
            if free<a.min_free_gb or tam>a.max_state_mb:
                print("SAM_PAUSA_PROTECCION_DISCO",round(free,2),round(tam,2),file=sys.stderr)
                return 3
            try:
                resultado=ejecutar_sesion(mem,practica,modelos,backend,a.batch,
                                           diverse=a.diverse)
                if a.diverse:
                    resultado["cobertura_diversa"]=cobertura([
                        t for t in practica if t.id in set(resultado["task_ids"])])
                if a.holdout_cases:
                    resultado["holdout"]=ejecutar_sesion(
                        mem,reservadas,modelos,backend,a.holdout_cases,holdout=True)
                    print("SAM_HOLDOUT",resultado["holdout"]["resumen"],
                          "sin memoria, sin entrenamiento",flush=True)
                if a.strategy_cases:
                    reservadas_exactas=[t for t in reservadas if t.grade=="exact"]
                    ronda=int(mem.con.execute("SELECT COUNT(DISTINCT run_id) FROM intentos").fetchone()[0])
                    candidatos=seleccionar_diverso(
                        reservadas_exactas,mem.estadisticas(),a.strategy_cases,ronda)
                    if candidatos:
                        resultado["evaluacion_estrategias"]=comparar_estrategias(
                            backend,modelos,candidatos,max_cases=a.strategy_cases)
                        print("SAM_ESTRATEGIAS",resultado["evaluacion_estrategias"]["resumen"],
                              "sin memoria; candidato no canónico",flush=True)
                if a.research_topics:
                    resultado["investigacion_externa"]=investigar_lote(
                        mem,backend,modelos,a.research_topics)
                    print("SAM_INVESTIGACION_EXTERNA",
                          len(resultado["investigacion_externa"]["topics"]),
                          "errores",len(resultado["investigacion_externa"]["errors"]),
                          "estatus",PENDING,flush=True)
                outfile=reports/(resultado["run_id"]+".json")
                tmp=outfile.with_suffix(".partial")
                tmp.write_text(json.dumps(resultado,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
                os.replace(tmp,outfile)
                contador+=1
                failures=0 if not resultado["errores"] else failures+1
                print("SAM_CICLO",contador,resultado["resumen"],
                      "canonical=",PENDING,flush=True)
                if failures>=3: break
            except Exception as exc:
                failures+=1
                print("SAM_CICLO_ERROR",str(exc),file=sys.stderr,flush=True)
                if failures>=3: return 2
            if a.interval and not halt[0] and (a.max_cycles==0 or contador<a.max_cycles):
                time.sleep(a.interval)
    finally:
        mem.cerrar()
    return 0

if __name__=="__main__":
    sys.exit(ejecutar())
