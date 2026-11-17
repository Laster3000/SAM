"""Control de tandas GitHub encadenadas para pruebas del proyecto.
Limita el coste de runners: nunca implementa hospedaje permanente 24/7.
"""
from __future__ import annotations
import argparse

DEFAULT_CHAIN_LIMIT=3

def siguiente(current: str | int, limit: int = DEFAULT_CHAIN_LIMIT) -> int | None:
    if not isinstance(current,(str,int)):
        raise ValueError("Número de etapa inválido")
    raw=str(current)
    if not raw.isdecimal() or len(raw)>3:
        raise ValueError("Número de etapa inválido")
    if not isinstance(limit,int) or not 1<=limit<=6:
        raise ValueError("Límite fuera de política (1-6)")
    step=int(raw)
    if step>=limit or step<0:
        raise ValueError("Etapa fuera de límite")
    return step+1 if step+1<limit else None

def main(argv=None):
    p=argparse.ArgumentParser(description="Siguiente etapa GitHub con límite de seguridad")
    p.add_argument("--current",required=True)
    p.add_argument("--limit",type=int,default=DEFAULT_CHAIN_LIMIT)
    args=p.parse_args(argv)
    result=siguiente(args.current,args.limit)
    print("STOP" if result is None else str(result))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
