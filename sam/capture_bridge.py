"""Puerta de captura SAM SOLO loopback, token en entorno y consentimiento por envío.

No hay sincronización automática con ChatGPT ni acceso público; requiere
un adaptador autorizado y un canal seguro configurado independientemente.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
import os
from .knowledge_ingest import Bandeja, DEFAULT_DATABASE, MAX_DOCUMENT_BYTES


def handler_factory(database: str, token: str):
    if not isinstance(token,str) or len(token) < 32:
        raise ValueError("Token local debe tener al menos 32 caracteres")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            # No escribir cuerpos, tokens ni datos del usuario en logs.
            return

        def reply(self, status: int, payload: dict):
            body=json.dumps(payload,ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type","application/json; charset=utf-8")
            self.send_header("Content-Length",str(len(body)))
            self.send_header("Cache-Control","no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path=="/healthz":
                self.reply(200,{"ok":True,"binding":"LOOPBACK_ONLY"})
            else:
                self.reply(404,{"error":"ruta desconocida"})

        def do_POST(self):
            if self.path!="/v1/ingest":
                self.reply(404,{"error":"ruta desconocida"})
                return
            auth=self.headers.get("Authorization","")
            if not hmac.compare_digest(auth,"Bearer "+token):
                self.reply(401,{"error":"no autorizado"})
                return
            length=self.headers.get("Content-Length","")
            if not length.isdecimal() or not 0 < int(length) <= MAX_DOCUMENT_BYTES + 4096:
                self.reply(413,{"error":"tamaño de petición no permitido"})
                return
            try:
                data=json.loads(self.rfile.read(int(length)).decode("utf-8"))
                if not isinstance(data,dict):
                    raise ValueError("El contenido debe ser un objeto")
                box=Bandeja(database)
                try:
                    result=box.ingresar(data.get("text"),
                        fuente=data.get("source_id"),
                        consentimiento=data.get("consent") is True)
                finally:
                    box.cerrar()
                self.reply(201 if result["nuevo"] else 200,result)
            except (UnicodeError,ValueError,PermissionError,json.JSONDecodeError) as exc:
                self.reply(400,{"error":str(exc)})

    return Handler


def main(argv=None):
    p=argparse.ArgumentParser(description="Puente privado SAM, solo 127.0.0.1")
    p.add_argument("--database",default=DEFAULT_DATABASE)
    p.add_argument("--port",type=int,default=8768)
    p.add_argument("--token-env",default="SAM_CAPTURE_TOKEN")
    a=p.parse_args(argv)
    if not 1<=a.port<=65535:
        p.error("Puerto inválido")
    token=os.environ.get(a.token_env,"")
    handler=handler_factory(a.database,token)
    server=ThreadingHTTPServer(("127.0.0.1",a.port),handler)
    print("SAM_CAPTURE_LOOPBACK_READY puerto="+str(a.port),flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__=="__main__":
    raise SystemExit(main())
