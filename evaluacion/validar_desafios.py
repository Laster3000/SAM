#!/usr/bin/env python3
"""Verifica formato/cobertura de desafíos SAM. No evalúa una IA."""
from pathlib import Path
import json
from collections import Counter
BASE=Path(__file__).resolve().parent
data=json.loads((BASE/"desafios_interdominios.json").read_text(encoding="utf-8"))
cases=data["casos"]
keys={"id","habilidad","origen","destino","pregunta","respuesta_referencia","mecanismo","limite","prueba","contraejemplo"}
skills=Counter()
ids=set()
assert len(cases)>=8
for case in cases:
    assert keys.issubset(case), f"faltan campos {case.get('id')}"
    assert case["id"] not in ids, "ID duplicado"
    ids.add(case["id"])
    for key in keys:
        assert isinstance(case[key],str) and case[key].strip(), f"campo inválido {case['id']}.{key}"
    skills[case["habilidad"]]+=1
assert len(skills)>=5, "Falta diversidad de razonamientos"
print(f"DESAFIOS_OK {len(cases)} casos; {len(skills)} habilidades")
print("Esto verifica estructura, no capacidad de IA ni exactitud científica.")
