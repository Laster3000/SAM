"""Contratos para captura privada, diversidad y comparación sin fuga de referencias."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sam.core import Modelo, PENDING
from sam.curriculum import Tarea, cargar
from sam.diversity import seleccionar_diverso, cobertura
from sam.knowledge_ingest import Bandeja, ingresar_archivos
from sam.capture_bridge import handler_factory
from sam.quality import separar
from sam.strategy_eval import comparar_estrategias


class BackendFalso:
    def __init__(self):
        self.calls = []

    def generar(self, modelo, instrucciones, pregunta):
        self.calls.append((modelo.nombre,instrucciones,pregunta))
        return "RESPUESTA: 1234567"


class TestCapturaYVariedad(unittest.TestCase):
    def test_solo_con_consentimiento(self):
        with TemporaryDirectory() as d:
            b = Bandeja(Path(d) / "private.sqlite3")
            with self.assertRaises(PermissionError):
                b.ingresar("texto",fuente="voz",consentimiento=False)
            self.assertEqual(b.contar(),0)
            b.cerrar()

    def test_privado_deduplicacion_y_busqueda(self):
        with TemporaryDirectory() as d:
            b = Bandeja(Path(d) / "private.sqlite3")
            a=b.ingresar("La termodinámica ayuda a entender refrigeración.",
                        fuente="conversacion-autorizada",consentimiento=True)
            otra=b.ingresar("La termodinámica ayuda a entender refrigeración.",
                        fuente="conversacion-autorizada",consentimiento=True)
            self.assertTrue(a["nuevo"])
            self.assertFalse(otra["nuevo"])
            self.assertEqual(b.contar(),1)
            self.assertEqual(b.buscar("refrigeración")[0]["id"],a["id"])
            self.assertEqual(a["estado"],"CAPTURADO_SIN_VERIFICAR")
            self.assertEqual(a["ubicacion"],"PRIVADO_LOCAL")
            self.assertEqual(b.buscar("palabra inexistente"),[])
            b.cerrar()

    def test_lote_original_y_repetido(self):
        with TemporaryDirectory() as d:
            root=Path(d)
            files=[]
            for i in range(3):
                p=root/f"fuente-{i}.md"
                p.write_text("Concepto original "+str(i),encoding="utf-8")
                files.append(p)
            b=Bandeja(root/"private.sqlite3")
            r=ingresar_archivos(b,files,"proyecto",True)
            self.assertEqual(r["nuevos"],3)
            self.assertEqual(ingresar_archivos(b,files,"proyecto",True)["duplicados"],3)
            b.cerrar()

    def test_puerta_token_exigido(self):
        with self.assertRaises(ValueError):
            handler_factory("local.sqlite3","token-corto")
        handler_factory("local.sqlite3","t"*32)

    def test_variedad_real_dominios_y_habilidades(self):
        practice,_=separar(cargar())
        a=seleccionar_diverso(practice,{},21,0)
        c=cobertura(a)
        self.assertGreaterEqual(len(c["dominios"]),6)
        self.assertGreaterEqual(len(c["habilidades"]),12)
        self.assertEqual(len({x.id for x in a}),len(a))
        b=seleccionar_diverso(practice,{},21,1)
        self.assertNotEqual([x.id for x in a],[x.id for x in b])

    def test_comparacion_reservada_sin_fuga_ni_memoria(self):
        _,hold=separar(cargar())
        exact=[t for t in hold if t.grade=="exact"]
        original=Tarea("demo","matematicas","test","¿Cuánto da?", "1234567","original")
        self.assertTrue(exact)
        back=BackendFalso()
        result=comparar_estrategias(
            back,(Modelo("A","/a"),Modelo("B","/b")), exact[:2],max_cases=2)
        self.assertEqual(result["estado"],PENDING)
        self.assertEqual(result["resumen"]["total"],2)
        self.assertEqual(len(back.calls),4)
        for _,inst,prompt in back.calls:
            self.assertIn("RESPUESTA:",inst)
            self.assertNotIn("Ejemplos de PRÁCTICA",prompt)
            self.assertNotIn("Referencia esperada",prompt)
        with self.assertRaises(ValueError):
            comparar_estrategias(back,(Modelo("A","/a"),Modelo("B","/b")),
                                [original])
