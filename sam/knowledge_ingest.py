"""Bandeja privada SAM: capturas consentidas, duplicados y búsqueda sencilla.

Nunca envía conversaciones a GitHub ni aprueba conocimientos automáticamente.
Para corpus grandes, importar lotes en un almacenamiento local autorizado.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3

MAX_DOCUMENT_BYTES = 2_000_000
MAX_FILES_PER_BATCH = 1000
CHUNK_SIZE = 1400
DEFAULT_DATABASE = ".sam-private/conocimiento.sqlite3"


def _chunks(text: str):
    """Separa sin resumir ni alterar la fuente original."""
    for start in range(0, len(text), CHUNK_SIZE):
        yield text[start:start + CHUNK_SIZE]


class Bandeja:
    def __init__(self, database: str | Path = DEFAULT_DATABASE):
        self.path = Path(database)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path, timeout=30)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.execute("""CREATE TABLE IF NOT EXISTS documentos (
            id TEXT PRIMARY KEY,
            fuente TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            contenido TEXT NOT NULL,
            fecha_utc TEXT NOT NULL,
            estado TEXT NOT NULL,
            visibilidad TEXT NOT NULL CHECK(visibilidad='PRIVADO'),
            bytes INTEGER NOT NULL,
            UNIQUE(fuente,sha256)
        )""")
        self.db.execute("""CREATE TABLE IF NOT EXISTS fragmentos (
            documento_id TEXT NOT NULL REFERENCES documentos(id),
            indice INTEGER NOT NULL,
            contenido TEXT NOT NULL,
            PRIMARY KEY(documento_id,indice)
        )""")
        self.db.execute("CREATE INDEX IF NOT EXISTS idx_fuente ON documentos(fuente)")
        self.db.commit()

    def cerrar(self):
        self.db.close()

    def ingresar(self, texto: str, *, fuente: str, consentimiento: bool) -> dict:
        if consentimiento is not True:
            raise PermissionError("Se necesita consentimiento explícito para la captura")
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("Texto vacío")
        if not isinstance(fuente, str) or not 1 <= len(fuente.strip()) <= 160:
            raise ValueError("Identificador de fuente inválido")
        fuente = fuente.strip()
        data = texto.encode("utf-8")
        if len(data) > MAX_DOCUMENT_BYTES:
            raise ValueError("Documento demasiado grande: dividirlo en partes consentidas")
        digest = sha256(data).hexdigest()
        docid = sha256(fuente.encode("utf-8") + b"\0" + data).hexdigest()
        partes = list(_chunks(texto))
        now = datetime.now(timezone.utc).isoformat()
        with self.db:
            cur = self.db.execute(
                """INSERT OR IGNORE INTO documentos
                   (id,fuente,sha256,contenido,fecha_utc,estado,visibilidad,bytes)
                   VALUES (?,?,?,?,?,?,?,?)""",
                (docid, fuente, digest, texto, now, "CAPTURADO_SIN_VERIFICAR",
                 "PRIVADO", len(data)))
            nuevo = cur.rowcount == 1
            if nuevo:
                self.db.executemany(
                    "INSERT INTO fragmentos(documento_id,indice,contenido) VALUES (?,?,?)",
                    ((docid,i,part) for i,part in enumerate(partes)))
        return {"id": docid, "sha256": digest, "nuevo": nuevo,
                "fragmentos": len(partes), "estado": "CAPTURADO_SIN_VERIFICAR",
                "ubicacion": "PRIVADO_LOCAL"}

    def buscar(self, consulta: str, limite: int = 10) -> list[dict]:
        if not isinstance(consulta,str) or not consulta.strip() or not 1 <= limite <= 50:
            raise ValueError("Consulta o límite inválido")
        # Escapar metacaracteres LIKE para consultas de texto literal.
        needle = consulta.strip().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        rows = self.db.execute(
            """SELECT d.id,d.fuente,d.sha256,f.indice,f.contenido
               FROM fragmentos f JOIN documentos d ON d.id=f.documento_id
               WHERE f.contenido LIKE ? ESCAPE '\\'
               ORDER BY d.fecha_utc DESC,f.indice ASC LIMIT ?""",
            ("%" + needle + "%", limite)).fetchall()
        return [{"id":x[0],"fuente":x[1],"sha256":x[2],
                 "fragmento":x[3],"texto":x[4],"estado":"CAPTURADO_SIN_VERIFICAR"}
                for x in rows]

    def contar(self) -> int:
        return int(self.db.execute("SELECT COUNT(*) FROM documentos").fetchone()[0])


def ingresar_archivos(bandeja: Bandeja, files: list[Path],
                     fuente: str, consentimiento: bool) -> dict:
    if consentimiento is not True:
        raise PermissionError("Consentimiento requerido")
    if len(files) > MAX_FILES_PER_BATCH:
        raise ValueError("Lote supera el límite de archivos")
    resultado = {"archivos":0,"nuevos":0,"duplicados":0,"fallos":[]}
    for f in files:
        try:
            if not f.is_file() or f.suffix.lower() not in (".txt",".md"):
                raise ValueError("Solo se admiten archivos TXT/MD")
            if f.stat().st_size > MAX_DOCUMENT_BYTES:
                raise ValueError("Archivo demasiado grande")
            text = f.read_text(encoding="utf-8")
            recibido = bandeja.ingresar(text, fuente=fuente + ":" + f.name,
                                        consentimiento=True)
            resultado["archivos"] += 1
            resultado["nuevos" if recibido["nuevo"] else "duplicados"] += 1
        except (OSError, UnicodeError, ValueError) as exc:
            resultado["fallos"].append({"archivo":f.name,"error":str(exc)})
    return resultado


def main(argv=None) -> int:
    ap=argparse.ArgumentParser(description="SAM: captura PRIVADA de textos consentidos")
    ap.add_argument("--database",default=DEFAULT_DATABASE)
    group=ap.add_mutually_exclusive_group(required=True)
    group.add_argument("--file")
    group.add_argument("--folder")
    group.add_argument("--search")
    ap.add_argument("--source",default="importacion-autorizada")
    ap.add_argument("--consent",action="store_true",
                    help="Confirma autorización para procesar los textos")
    args=ap.parse_args(argv)
    box=Bandeja(args.database)
    try:
        if args.search is not None:
            output=box.buscar(args.search)
        else:
            if not args.consent:
                ap.error("Importar requiere --consent")
            path=Path(args.file or args.folder)
            files=[path] if args.file else sorted(p for p in path.iterdir() if p.is_file())
            output=ingresar_archivos(box,files,args.source,args.consent)
        print(json.dumps(output,ensure_ascii=False))
    finally:
        box.cerrar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
