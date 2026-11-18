"""Conciliación reversible de ledgers experimentales SAM sin perder experiencias.

Los eventos con el mismo identificador deben ser byte/equivalentemente idénticos
en contenido lógico, de otro modo se detiene la importación. Ningún dato se
promociona al canon TCSA.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import tempfile
from .quality import auditar_ledger

MAX_TOTAL=100_000_000

def combinar(entradas: list[str | Path], destino: str | Path) -> dict:
    if len(entradas)<2 or len(entradas)>8:
        raise ValueError("Dos a ocho ledgers como máximo")
    destino=Path(destino)
    datos={}
    orden=[]
    sizes=[]
    for source in entradas:
        src=Path(source)
        a=auditar_ledger(src)
        sizes.append(a["events"])
        for line in src.read_text(encoding="utf-8").splitlines():
            event=json.loads(line)
            eid=event["evento_id"]
            canonical=json.dumps(event,ensure_ascii=False,sort_keys=True,
                                 separators=(",",":"))
            if eid in datos:
                if datos[eid]!=canonical:
                    raise ValueError("Conflicto de evento entre ramas: "+eid)
                continue
            datos[eid]=canonical
            orden.append(eid)
    salida=("\n".join(datos[x] for x in orden)+"\n").encode("utf-8")
    if len(salida)>MAX_TOTAL:
        raise ValueError("No cabe en el límite de memoria GitHub")
    destino.parent.mkdir(parents=True,exist_ok=True)
    tmp=None
    try:
        with tempfile.NamedTemporaryFile(dir=destino.parent,prefix=".sam-merge-",
                                         suffix=".jsonl",delete=False) as f:
            tmp=Path(f.name)
            f.write(salida)
            f.flush()
            os.fsync(f.fileno())
        merged=auditar_ledger(tmp)
        os.replace(tmp,destino)
        return {"entrada_eventos":sizes,"eventos_unicos":merged["events"],
                "duplicados":sum(sizes)-merged["events"],
                "sha256":merged["sha256"],"estado":"CANDIDATE_PENDING_TCSA"}
    finally:
        if tmp and tmp.exists():tmp.unlink()

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("ledgers",nargs="+")
    p.add_argument("--output",required=True)
    a=p.parse_args(argv)
    print("SAM_UNION_LEDGERS",json.dumps(combinar(a.ledgers,a.output),ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
