"""Entrypoint SAM 0.2. Python -m sam.pilot --mode evolucion."""
from pathlib import Path
import argparse
import json
import os
import sys
from .core import Modelo, LlamaCLI, informe, PENDING

def main(argv=None):
    parser = argparse.ArgumentParser(description="SAM: dos modelos libres y prueba trazable")
    parser.add_argument("--mode", choices=["trabajo", "evolucion"], default="evolucion")
    parser.add_argument("--model-a", required=True)
    parser.add_argument("--model-b", required=True)
    parser.add_argument("--llama-cli", default=os.environ.get("LLAMA_BIN", "llama-cli"))
    parser.add_argument("--limit", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--out", default="resultados/sam-piloto.json")
    parser.add_argument("--corpus", default="evaluacion/casos_iniciales.json")
    args = parser.parse_args(argv)
    if args.limit < 1 or args.limit > 5 or args.max_tokens < 32 or args.max_tokens > 256:
        parser.error("Límites: 1-5 casos y 32-256 tokens por inferencia")
    ruta = Path(args.out)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fuente = Path(args.corpus)
    # Corpus público original; no abrir secretos ni documentos locales de AF/TCSA.
    casos = json.loads(fuente.read_text(encoding="utf-8"))["cases"]
    orden = ["es-003", "mat-001", "psi-001", "fis-001", "bio-001"]
    seleccion = [next(x for x in casos if x["id"] == id_) for id_ in orden[:args.limit]]
    modelos = (Modelo("Qwen3-0.6B", args.model_a),
               Modelo("Qwen2.5-0.5B-Instruct", args.model_b))
    try:
        reporte = informe(args.mode, seleccion, *modelos,
                          LlamaCLI(args.llama_cli, timeout=240, max_tokens=args.max_tokens),
                          str(fuente))
    except Exception as exc:
        # Los fallos nunca se convierten en aprendizaje ni se ocultan.
        reporte = {"schema": "sam.run.v0", "version": "0.2.0", "modo": args.mode,
                   "estado_canonico": PENDING, "error": str(exc),
                   "capsulas_candidatas": [], "resultado": "ERROR_REAL_NO_REINTENTAR_SIN_RECONCILIAR"}
        ruta.write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("SAM_ERROR:", str(exc), file=sys.stderr)
        return 1
    ruta.write_text(json.dumps(reporte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("SAM_RUN_OK", json.dumps(reporte["resumen"], ensure_ascii=False))
    print("TCSA:", PENDING, "se requiere reconciliación canónica antes de promocionar")
    return 0

if __name__ == "__main__":
    sys.exit(main())
