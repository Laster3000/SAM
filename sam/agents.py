"""Especificaciones modulares. Solo emite CANDIDATOS, jamás parchea el sistema estable."""
from dataclasses import dataclass
from typing import Iterable

PROTEGIDOS = frozenset({"permisos", "auditoria", "recuperacion", "verificacion"})
ROLES = (
    "interprete", "creador", "critico", "corrector", "simplificador",
    "esceptico", "mutador_aislado", "detector_errores", "alternativas",
    "verificador_determinista", "arbitro", "gestor_memoria", "supervisor_evolucion",
)

@dataclass(frozen=True)
class Agente:
    nombre: str
    version: str
    piezas: frozenset[str]
    dependencias: frozenset[str] = frozenset()
    activo: bool = True

def combinar_candidato(agentes: Iterable[Agente], piezas: Iterable[str]) -> dict:
    agentes = tuple(agentes)
    solicitadas = frozenset(piezas)
    disponibles = frozenset().union(*(agente.piezas for agente in agentes))
    if not agentes or not solicitadas or not solicitadas.issubset(disponibles):
        raise ValueError("Piezas no disponibles o sin origen")
    if PROTEGIDOS.intersection(solicitadas):
        raise ValueError("Componentes protegidos: no trasplantar automáticamente")
    return {
        "tipo": "fusion_candidata",
        "origen": [{"nombre": a.nombre, "version": a.version} for a in agentes],
        "piezas": sorted(solicitadas),
        "estado": "CANDIDATE_PENDING_TCSA",
        "promocion_automatica": False,
        "requisitos": ["contratos", "compatibilidad", "pruebas de ablación",
                       "regresiones", "holdout", "rollback", "autorización TCSA"]
    }

def podar_candidato(agente: Agente) -> dict:
    if agente.piezas.intersection(PROTEGIDOS):
        raise ValueError("Agente con funciones críticas protegidas")
    return {
        "tipo": "poda_reversible", "agente": agente.nombre, "version": agente.version,
        "estado": "CANDIDATE_PENDING_TCSA",
        "fases": ["bajar_prioridad", "sombra", "desactivar", "archivar_recuperable"],
        "borrado_definitivo": False, "ejecutado": False
    }
