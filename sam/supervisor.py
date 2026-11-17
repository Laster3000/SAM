"""Supervisor externo del worker SAM. Reinicia procesos caídos sin inventar éxito.
Solo se ejecuta en un equipo persistentemente encendido y con modelos disponibles.
"""
from __future__ import annotations
import argparse
import os
from pathlib import Path
import subprocess
import sys
import time

def delay(failures: int, base: int = 30) -> int:
    return min(300, base * (2 ** min(failures, 5)))

def run_supervisor(args=None):
    p=argparse.ArgumentParser(description="SAM: arranque y recuperación del worker")
    p.add_argument("--model-a",required=True)
    p.add_argument("--model-b",required=True)
    p.add_argument("--llama-cli",required=True)
    p.add_argument("--state",default=".sam-state")
    p.add_argument("--reports",default="resultados")
    p.add_argument("--batch",type=int,default=18)
    p.add_argument("--research-topics",type=int,default=2)
    p.add_argument("--delay",type=int,default=30)
    a=p.parse_args(args)
    if a.delay<5 or a.delay>300:
        p.error("La espera de recuperación debe estar entre 5 y 300 segundos")
    state=Path(a.state)
    state.mkdir(parents=True,exist_ok=True)
    failures=0
    while True:
        if (state/"STOP").exists():
            print("SAM_SUPERVISOR_DETENIDO_MANUALMENTE",flush=True)
            return 0
        cmd=[sys.executable,"-m","sam.worker",
            "--model-a",a.model_a,"--model-b",a.model_b,
            "--llama-cli",a.llama_cli,
            "--state",str(state),"--reports",a.reports,
            "--batch",str(a.batch),"--research-topics",str(a.research_topics),
            "--interval","20","--max-cycles","0"]
        start=time.monotonic()
        try:
            proc=subprocess.Popen(cmd)
            code=proc.wait()
        except KeyboardInterrupt:
            if "proc" in locals() and proc.poll() is None:
                proc.terminate()
                try:proc.wait(timeout=15)
                except subprocess.TimeoutExpired:proc.kill()
            return 0
        except OSError as exc:
            code=2
            print("SAM_SUPERVISOR_ERROR",str(exc),file=sys.stderr)
        if code==3: # Worker detectó falta de espacio o estado demasiado grande.
            print("SAM_SUPERVISOR_BLOQUEADO_POR_RECURSOS; no reiniciar automáticamente",file=sys.stderr)
            return 3
        if (state/"STOP").exists():
            return 0
        runtime=time.monotonic()-start
        failures=0 if runtime>=600 else failures+1
        wait=delay(failures,a.delay)
        print("SAM_REINICIO_CONTROLADO",{"rc":code,"segundos":wait,
                                        "fallos_rapidos":failures},flush=True)
        time.sleep(wait)

if __name__=="__main__":
    sys.exit(run_supervisor())
