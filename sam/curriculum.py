"""Currículo abierto y reproducible de SAM. Casos sintéticos NO equivalen a sabiduría.
Incluye datos originales del proyecto y tareas cuantitativas verificables.
"""
from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Iterator

@dataclass(frozen=True)
class Tarea:
    id: str
    domain: str
    skill: str
    prompt: str
    expected: str | None
    source: str
    grade: str = "exact"

    def as_case(self) -> dict:
        return {"id": self.id, "domain": self.domain, "skill": self.skill,
                "prompt": self.prompt, "expected": self.expected,
                "source": self.source, "grade": self.grade}

def generadas() -> Iterator[Tarea]:
    for a in range(12, 60, 3):
        for b in range(11, 51, 4):
            yield Tarea(f"gen-mul-{a}-{b}", "matematicas", "aritmetica",
                        f"Calcula exactamente {a} × {b}. Responde solo el número.", str(a*b), "generador:aritmetica")
    for a in range(2, 13):
        for x in range(2, 24):
            b = a + x
            yield Tarea(f"gen-alg-{a}-{x}", "matematicas", "algebra",
                        f"Resuelve la ecuación {a}x + {b} = {a*x+b}. Da únicamente x.",
                        str(x), "generador:algebra")
    for p in range(10, 100, 10):
        for base in range(40, 241, 20):
            yield Tarea(f"gen-pct-{p}-{base}", "matematicas", "porcentajes",
                        f"¿Cuánto es el {p}% de {base}? Escribe un número.",
                        str((p*base)//100), "generador:porcentaje")
    for v in range(3, 31, 3):
        for segundos in range(4, 31, 3):
            d=v*segundos
            yield Tarea(f"gen-vel-{v}-{segundos}", "fisica", "mecanica",
                        f"Un objeto recorre {d} metros en {segundos} segundos a velocidad uniforme. ¿Velocidad en m/s? Da el número.",
                        str(v), "generador:velocidad")
    for m in range(4, 21, 2):
        for v in range(2, 15, 2):
            yield Tarea(f"gen-ec-{m}-{v}", "fisica", "energia",
                        f"Con masa {m} kg y rapidez {v} m/s, ¿energía cinética en J? Usa E=1/2·m·v²; da el número.",
                        str(m*v*v//2), "generador:energia")
    masses={"H2O":(2,16), "CO2":(12,32), "NH3":(14,3), "CH4":(12,4), "O2":(0,32)}
    for molecule,(carbon_or_nitrogen,other) in masses.items():
        for cantidad in range(1, 27):
            yield Tarea(f"gen-mol-{molecule}-{cantidad}", "quimica", "masas_molares",
                        f"Usando masas atómicas aproximadas H=1, C=12, N=14, O=16 g/mol: ¿qué masa en gramos representan {cantidad} moles de {molecule}? Solo el número.",
                        str((carbon_or_nitrogen+other)*cantidad), "generador:masa_molar")
    for n in range(1, 11):
        for inicial in range(1, 17):
            yield Tarea(f"gen-cel-{n}-{inicial}", "biologia", "modelos_celulares",
                        f"En un modelo idealizado sin muerte celular ni límites, cada célula se divide en dos {n} veces. Si hay {inicial} células iniciales, ¿cuántas habrá? Número.",
                        str(inicial*(2**n)), "generador:division_ideal")
    for tp in range(1, 10):
        for escala in range(2, 19, 2):
            yield Tarea(f"gen-pre-{tp}-{escala}", "psicologia", "metodologia_estadistica",
                        f"En una prueba clasificadora hay {tp*escala} verdaderos positivos y {(10-tp)*escala} falsos positivos. ¿Qué precisión (%) tiene la clasificación? Solo número, sin símbolo.",
                        str(tp*10), "generador:metodologia")
    dialectos=[
        ("Vos tenés razón", "tú tienes razón", "voseo rioplatense"),
        ("Vos podés venir", "tú puedes venir", "voseo rioplatense"),
        ("¿Qué hacés?", "¿qué haces?", "voseo rioplatense"),
        ("Che, vení acá", "oye, ven aquí", "voseo rioplatense"),
        ("Ordenador", "computadora", "España comparado con buena parte de América"),
        ("Móvil", "celular", "España comparado con muchos países americanos"),
        ("Coche", "automóvil", "España"),
        ("Guagua", "autobús", "Canarias, en contexto de transporte"),
        ("Chamba", "trabajo", "México, coloquial"),
        ("Pega", "trabajo", "Chile, coloquial"),
        ("Laburo", "trabajo", "Argentina y Uruguay, coloquial"),
        ("Qué bacán", "qué bueno", "regiones andinas, coloquial"),
        ("Qué chévere", "qué bueno", "Venezuela y otras regiones, coloquial"),
        ("Platicar", "conversar", "México"),
        ("Computadora", "ordenador", "América comparado con España"),
    ]
    for i,(frase,expected,region) in enumerate(dialectos,1):
        yield Tarea(f"gen-esp-{i:03d}", "espanol", "variantes_panhispanicas",
                    f"En {region}, convierte a una expresión equivalente de español estándar, manteniendo intención: «{frase}». Da únicamente la expresión.",
                    expected, "ejemplos originales cuidadosamente acotados")

def cargar(base: str | Path = "evaluacion") -> list[Tarea]:
    root=Path(base)
    tareas=list(generadas())
    inicial=root/"casos_iniciales.json"
    if inicial.exists():
        data=json.loads(inicial.read_text(encoding="utf-8"))
        for x in data.get("cases", []):
            tareas.append(Tarea(x["id"], x["domain"], x["skill"],
                               x["prompt"], x["expected"], str(inicial)))
    inter=root/"desafios_interdominios.json"
    if inter.exists():
        data=json.loads(inter.read_text(encoding="utf-8"))
        for x in data.get("casos", []):
            tareas.append(Tarea(x["id"], "interdominios", x["habilidad"],
                              x["pregunta"] + "\nAnaliza el mecanismo, sus límites y cómo comprobarlo.",
                              x["respuesta_referencia"], str(inter), "revision_humana"))
    ids=[x.id for x in tareas]
    if len(ids)!=len(set(ids)):
        raise ValueError("IDs de currículo duplicados")
    return tareas
