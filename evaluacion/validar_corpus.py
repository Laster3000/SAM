#!/usr/bin/env python3
"""Validación del corpus SAM 0.1, sin dependencias externas ni uso de IA."""
import json
import pathlib
import sys
from collections import Counter

ROOT=pathlib.Path(__file__).resolve().parents[1]
VALID_DOMAINS={"espanol","matematicas","fisica","quimica","biologia","psicologia"}
VALID_KEYS={"id","domain","skill","prompt","expected","notes"}
def main():
    p=ROOT/"evaluacion"/"casos_iniciales.json"
    obj=json.loads(p.read_text(encoding="utf-8"))
    cases=obj["cases"]
    ids=[c.get("id") for c in cases]
    assert len(ids)==len(set(ids)), "IDs duplicados"
    counts=Counter()
    for c in cases:
        assert VALID_KEYS <= set(c), f"campos ausentes: {c}"
        assert c["domain"] in VALID_DOMAINS, f"dominio desconocido: {c['domain']}"
        assert all(isinstance(c[k],str) and c[k].strip() for k in VALID_KEYS), f"campo vacío: {c['id']}"
        counts[c["domain"]]+=1
    assert set(counts)==VALID_DOMAINS, "Faltan áreas"
    assert len(cases)>=12, "Corpus inicial insuficiente"
    print("CORPUS_OK",len(cases),"casos",dict(sorted(counts.items())))
    print("AVISO: esto solo valida estructura y cobertura, NO comprensión de una IA.")
    return 0
if __name__=="__main__":
    sys.exit(main())
