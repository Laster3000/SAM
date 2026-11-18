"""Informe de evidencia sin confundir ejecuciones con aprendizaje.
Holdout público y repetido: NO es evaluación independiente ni entrenamiento.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
from pathlib import Path
from .quality import auditar_ledger

def resumir(eventos: list[dict]) -> dict:
    domains=defaultdict(lambda:{"practice":{"attempts":0,"exact":0,"ids":set()},
                                "holdout":{"attempts":0,"exact":0,"ids":set()}})
    for item in eventos:
        p=item["payload"]
        dataset=p.get("evaluation_set","practice")
        if dataset not in ("practice","holdout"):
            raise ValueError("Dataset no permitido")
        d=domains[item["domain"]][dataset]
        d["attempts"]+=1
        d["exact"]+=int(item["correct"] is True)
        d["ids"].add(item["task_id"])
    by_domain={}
    total_holdout=set(); total_attempts=0
    for name,sets in sorted(domains.items()):
        by_domain[name]={}
        for dataset,stats in sets.items():
            attempts=stats["attempts"]; unique=len(stats["ids"])
            by_domain[name][dataset]={
                "attempts":attempts,"unique_tasks":unique,
                "repetitions":attempts-unique,"exact_matches":stats["exact"],
                "literal_rate":round(stats["exact"]/attempts,4) if attempts else None
            }
            if dataset=="holdout":
                total_holdout.update(stats["ids"])
                total_attempts+=attempts
    return {"schema":"sam.learning-evidence.v1","dominios":by_domain,
        "holdout_unicos":len(total_holdout),
        "holdout_intentos":total_attempts,
        "holdout_repeticiones":total_attempts-len(total_holdout),
        "pesos_entrenados":False,
        "benchmark_independiente":False,
        "generalizacion_certificada":False,
        "aprendizaje_demostrado":False,
        "motivo":"Holdout sintético de corpus público y posiblemente repetido; "
                 "sin comparación externa controlada ni entrenamiento de pesos.",
        "estado":"EXPERIMENTO_NO_CANONICO"}

def analizar(path: str | Path) -> dict:
    path=Path(path)
    audit=auditar_ledger(path)
    events=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    out=resumir(events)
    out["ledger_sha256"]=audit["sha256"]
    out["ledger_events"]=audit["events"]
    out["canonical_status"]=audit["tcsa_status"]
    return out

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("ledger")
    p.add_argument("--output")
    args=p.parse_args(argv)
    report=analizar(args.ledger)
    if args.output:
        out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SAM_LEARNING_EVIDENCE",json.dumps({
        key:report[key] for key in ("ledger_events","holdout_unicos","holdout_intentos",
                                   "holdout_repeticiones","generalizacion_certificada")},ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
