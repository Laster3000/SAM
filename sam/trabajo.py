"""Modo TRABAJO experimental de SAM con dos modelos reales, sin evolución.
No lanza servicios, no cambia archivos del proyecto ni certifica la respuesta.
El encargo se lee únicamente de un fichero aportado por la persona.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
from uuid import uuid4
from .architecture import Modo
from .core import Modelo,LlamaCLI,ciclo_dos_modelos,PENDING

MAX_ENCARGO_BYTES=8_000

def atender(texto:str, backend, modelos:tuple[Modelo,Modelo]) -> dict:
    if not isinstance(texto,str) or not 1<=len(texto.strip().encode("utf-8"))<=MAX_ENCARGO_BYTES:
        raise ValueError("Encargo vacío o demasiado largo")
    if len(modelos)!=2:
        raise ValueError("Modo TRABAJO requiere dos modelos")
    respuesta=ciclo_dos_modelos(backend,modelos[0],modelos[1],texto)
    return {"schema":"sam.work.v1","modo":Modo.TRABAJO.value,
            "fecha_utc":datetime.now(timezone.utc).isoformat(),
            "resultado":respuesta,
            "estado":"RESPUESTA_CANDIDATA_SIN_VALIDACION_EXTERNA",
            "estado_tCSA":PENDING,"modificacion_de_codigo":False,
            "entrenamiento_de_pesos":False,
            "advertencia":"Dos modelos han propuesto y criticado; no constituye validación de verdad o competencia general."}

def ejecutar(argv=None):
    p=argparse.ArgumentParser(description="SAM TRABAJO experimental; nada se publica en GitHub automáticamente")
    p.add_argument("--request-file",required=True)
    p.add_argument("--model-a",required=True)
    p.add_argument("--model-b",required=True)
    p.add_argument("--llama-cli",required=True)
    p.add_argument("--output-dir",default=".sam-private/trabajos")
    a=p.parse_args(argv)
    raw=Path(a.request_file).read_bytes()
    if len(raw)>MAX_ENCARGO_BYTES: raise ValueError("Encargo demasiado grande")
    prompt=raw.decode("utf-8")
    for f in (a.model_a,a.model_b,a.llama_cli):
        if not Path(f).is_file():
            raise ValueError("Archivo del modelo/binario no existe")
    result=atender(prompt,LlamaCLI(a.llama_cli),
                  (Modelo("modelo-creador",a.model_a),Modelo("modelo-critico",a.model_b)))
    dest=Path(a.output_dir)
    dest.mkdir(parents=True,exist_ok=True)
    path=dest/("sam-work-"+uuid4().hex+".json")
    with path.open("x",encoding="utf-8") as h:
        json.dump(result,h,ensure_ascii=False,indent=2)
        h.write("\n")
    print("SAM_TRABAJO_RESULTADO_PRIVADO",str(path),"ESTADO_NO_VERIFICADO")
    return 0

if __name__=="__main__":
    raise SystemExit(ejecutar())
