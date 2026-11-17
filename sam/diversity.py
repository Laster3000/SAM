"""Selección equilibrada de tareas entre dominios y habilidades.

Conservar variedad no garantiza conocimiento; solo mejora cobertura de ensayos.
"""
from __future__ import annotations
from collections import defaultdict


def seleccionar_diverso(tareas, estadisticas: dict, limite: int,
                      ronda: int = 0) -> list:
    if not 1 <= limite <= 100:
        raise ValueError("Límite de tareas de 1 a 100")
    if not tareas:
        raise ValueError("Sin tareas")
    groups = defaultdict(lambda: defaultdict(list))
    for task in tareas:
        st = estadisticas.get(task.id, {})
        attempts = int(st.get("intentos", 0))
        success = int(st.get("aciertos", 0))
        # Primero casos nuevos; después insistir en los fallos sin bucle infinito.
        priority = (attempts * 10 + success * 3, task.id)
        groups[task.domain][task.skill].append((priority, task))
    for domain in groups:
        for skill in groups[domain]:
            groups[domain][skill].sort(key=lambda e: e[0])
    domains = sorted(groups)
    shift = ronda % len(domains)
    domains = domains[shift:] + domains[:shift]
    chosen, used = [], set()
    while len(chosen) < min(limite, len(tareas)):
        progressed = False
        for domain in domains:
            skills = sorted(groups[domain])
            rotation = (ronda + len(chosen)) % len(skills)
            ordered = skills[rotation:] + skills[:rotation]
            for skill in ordered:
                bucket = groups[domain][skill]
                while bucket and bucket[0][1].id in used:
                    bucket.pop(0)
                if bucket:
                    task = bucket.pop(0)[1]
                    chosen.append(task)
                    used.add(task.id)
                    progressed = True
                    break
            if len(chosen) >= limite:
                break
        if not progressed:
            break
    return chosen


def cobertura(tareas: list) -> dict:
    return {
        "dominios": sorted({t.domain for t in tareas}),
        "habilidades": sorted({t.domain + ":" + t.skill for t in tareas}),
        "casos": len(tareas),
    }
