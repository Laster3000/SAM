"""Contratos de arquitectura SAM: TRABAJO estable frente a EVOLUCION aislada.
Sólo construye planes candidatos reversibles. No edita ni ejecuta componentes.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json
import re

CRITICOS=frozenset({"autoridad","auditoria","recuperacion","verificacion","permisos"})
PRUEBAS_OBLIGATORIAS=(
    "compatibilidad_de_interfaces","dependencias_cerradas","ausencia_de_regresiones",
    "evaluacion_independiente","prueba_de_restauracion","autorizacion_TCSA"
)
IDENT=re.compile(r"^[a-z][a-z0-9_]{1,63}$")

class Modo(str,Enum):
    TRABAJO="TRABAJO"
    EVOLUCION="EVOLUCION"

@dataclass(frozen=True)
class Componente:
    nombre: str
    version: str
    capacidades: frozenset[str]
    dependencias: frozenset[str] = frozenset()
    protegido: bool = False
    evidencia: str = "SIN_PRUEBAS_INDEPENDIENTES"
    licencia: str = "PENDIENTE_VERIFICACION"

    def __post_init__(self):
        if (not IDENT.fullmatch(self.nombre)
                or not self.version or len(self.version)>80
                or not self.capacidades
                or any(not IDENT.fullmatch(c) for c in self.capacidades|self.dependencias)
                or self.nombre in self.dependencias):
            raise ValueError("Contrato de componente inválido")
        if self.nombre in CRITICOS and not self.protegido:
            raise PermissionError("El componente crítico debe protegerse")

def _snapshot(componentes: dict[str,Componente]) -> tuple[str,dict]:
    full={
        name:{"version":obj.version,"capacidades":sorted(obj.capacidades),
              "dependencias":sorted(obj.dependencias),"protegido":obj.protegido,
              "evidencia":obj.evidencia,"licencia":obj.licencia}
        for name,obj in sorted(componentes.items())
    }
    raw=json.dumps(full,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
    return sha256(raw).hexdigest(),full

class Arquitectura:
    def __init__(self,componentes,modo: Modo | str="TRABAJO"):
        self.modo=Modo(modo)
        partes=list(componentes)
        self._parts={p.nombre:p for p in partes}
        if len(self._parts)!=len(partes) or not partes:
            raise ValueError("Arquitectura vacía o con nombres duplicados")
        for obj in partes:
            if not obj.dependencias.issubset(self._parts.keys()):
                raise ValueError("Dependencia ausente "+obj.nombre)
        self._orden_validado()
        self.sha256,self._state=_snapshot(self._parts)

    def _orden_validado(self):
        pendientes=set(); visitados=set()
        def dfs(name):
            if name in pendientes:raise ValueError("Dependencia circular")
            if name in visitados:return
            pendientes.add(name)
            for dep in sorted(self._parts[name].dependencias):dfs(dep)
            pendientes.remove(name)
            visitados.add(name)
        for name in sorted(self._parts):dfs(name)

    def disponibles_trabajo(self):
        """Sólo capacidades con comprobación externa, fuera de evolución."""
        if self.modo is not Modo.TRABAJO:
            raise PermissionError("Modo EVOLUCION no presta servicios estables")
        return sorted({
            cap for item in self._parts.values()
            if item.evidencia=="VERIFICADA_INDEPENDIENTEMENTE"
            and item.licencia!="PENDIENTE_VERIFICACION"
            for cap in item.capacidades
        })

    def _candidato(self,tipo,origen,piezas):
        if self.modo is not Modo.EVOLUCION:
            raise PermissionError("Mutaciones prohibidas en modo TRABAJO")
        if any(x not in self._parts for x in origen):
            raise ValueError("Origen inexistente")
        if any(self._parts[x].protegido for x in origen):
            raise PermissionError("Componente protegido, no transformar")
        return {
            "schema":"sam.architecture.candidate.v1","modo":self.modo.value,
            "operacion":tipo,"origen":sorted(origen),"piezas":sorted(piezas),
            "revision_original_sha256":self.sha256,"estado":"CANDIDATE_PENDING_TCSA",
            "aplicado":False,"promocion_automatica":False,
            "rollback":{"sha256":self.sha256,"esquema":"snapshot_original_intacto"},
            "requisitos":list(PRUEBAS_OBLIGATORIAS)
        }

    def proponer_fusion(self,nombres: list[str]):
        if len(set(nombres))<2 or len(nombres)!=len(set(nombres)):
            raise ValueError("La fusión necesita componentes distintos")
        comps=[self._parts[n] for n in nombres]  # lookup also verifies existence
        union=frozenset().union(*(c.capacidades for c in comps))
        plan=self._candidato("fusion_aislada",nombres,union)
        plan["dependencias_externas"]=sorted(
            frozenset().union(*(c.dependencias for c in comps))-set(nombres)
        )
        return plan

    def proponer_division(self,nombre:str,piezas_a:set[str],piezas_b:set[str]):
        c=self._parts[nombre]
        a,b=frozenset(piezas_a),frozenset(piezas_b)
        if not a or not b or a & b or a | b != c.capacidades:
            raise ValueError("Partición incompatible, incompleta o redundante")
        plan=self._candidato("division_aislada",[nombre],c.capacidades)
        plan["salidas"]=[sorted(a),sorted(b)]
        return plan

    def proponer_poda(self,nombre:str):
        c=self._parts[nombre]
        if any(nombre in p.dependencias for p in self._parts.values()):
            raise PermissionError("Poda impediría ejecutar una dependencia")
        plan=self._candidato("poda_reversible",[nombre],c.capacidades)
        plan["etapas"]=["sombra","reducir_prioridad","desactivar","archivar"]
        plan["borrado_definitivo"]=False
        return plan

    def manifest(self):
        return {"modo":self.modo.value,"revision_sha256":self.sha256,
                "componentes":self._state,"estado":"ESPECIFICACION_NO_DESPLIEGUE"}
