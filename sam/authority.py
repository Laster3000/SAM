"""RAMSES DICE: puerta prototipo de órdenes humanas; los modelos no la pueden emitir.

IMPORTANTE: el canal de entrada confiable debe autenticar a la persona FUERA de SAM.
El texto RAMSES DICE, actor='owner' o una firma inventada no conceden permisos.
Este módulo valida un ticket que firma exclusivamente un gateway autorizado.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import hmac
import json
import time

PREFIX = "RAMSES DICE"
MAX_SKEW = 120
MAX_ACTION_SIZE = 2000

@dataclass(frozen=True)
class Ticket:
    text: str
    nonce: str
    issued_at: int
    authenticated_actor: str
    origin: str
    mac: str

def _payload(text: str, nonce: str, issued_at: int, actor: str, origin: str) -> bytes:
    return json.dumps(
        {"text": text, "nonce": nonce, "issued_at": issued_at,
         "authenticated_actor": actor, "origin": origin},
        sort_keys=True, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")

def emitir_en_gateway_externo(text: str, nonce: str, now: int, actor: str, key: bytes) -> Ticket:
    """Solo para proceso de ingreso humano confiable. NO EXPONER como herramienta a SAM."""
    if not text.strip().upper().startswith(PREFIX + " "):
        raise ValueError("No es una orden RAMSES DICE")
    if not key or len(key) < 32:
        raise ValueError("Clave de gateway débil")
    if actor != "owner_authenticated":
        raise PermissionError("El gateway no autenticó al dueño")
    origin = "trusted-human-ingress"
    mac = hmac.new(key, _payload(text, nonce, now, actor, origin), hashlib.sha256).hexdigest()
    return Ticket(text, nonce, now, actor, origin, mac)

class PuertaAutoridad:
    def __init__(self, key: bytes, *, now_fn=time.time):
        if not key or len(key) < 32:
            raise ValueError("Falta secreto seguro inyectado por el gateway")
        self._key = key
        self._now = now_fn
        self._nonces: set[str] = set()

    def verificar(self, ticket: Ticket) -> dict:
        if (not isinstance(ticket, Ticket)
                or ticket.authenticated_actor != "owner_authenticated"
                or ticket.origin != "trusted-human-ingress"):
            raise PermissionError("Falta identidad humana autenticada")
        if (not ticket.text.strip().upper().startswith(PREFIX + " ")
                or len(ticket.text) > MAX_ACTION_SIZE or len(ticket.nonce) < 16
                or abs(self._now() - ticket.issued_at) > MAX_SKEW
                or ticket.nonce in self._nonces):
            raise PermissionError("Orden no válida, caducada o repetida")
        message = _payload(ticket.text, ticket.nonce, ticket.issued_at,
                           ticket.authenticated_actor, ticket.origin)
        mac = hmac.new(self._key, message, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, ticket.mac):
            raise PermissionError("Firma incorrecta")
        self._nonces.add(ticket.nonce)
        return {
            "estado": "AUTHENTICATED_OWNER_DIRECTIVE",
            "texto": ticket.text[len(PREFIX):].strip(),
            "prioridad": "alta_sujeta_a_permisos",
            "limites": "No modifica políticas de seguridad, licencias, permisos ni acciones protegidas",
            "audit_nonce": ticket.nonce
        }
