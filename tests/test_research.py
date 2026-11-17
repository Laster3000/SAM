import tempfile
import unittest
from sam.research import Fuente, investigar_lote, temas
from sam.learning import Memoria
from sam.core import Modelo

class FakeBackend:
    def generar(self,modelo,instrucciones,pregunta):
        if "crítico independiente" in instrucciones.lower():
            return "Cuidado con extrapolar sin pruebas."
        return "HIPÓTESIS: podría haber una analogía; verificar antes.\nRESPUESTA: no comprobada"

class TestInvestigar(unittest.TestCase):
    def test_temario_amplio(self):
        t=temas()
        self.assertGreaterEqual(len(t),38)
        self.assertEqual(len(t),len(set(x.id for x in t)))
    def test_fuentes_siempre_candidatas(self):
        def f(consulta):
            return Fuente("Fuente de prueba","https://es.wikipedia.org/?curid=1",
                          "Una explicación corta.", "a"*64,"2026-11-17T00:00:00Z")
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            r=investigar_lote(mem,FakeBackend(),(Modelo("A","/a"),Modelo("B","/b")),2,fetch=f)
            self.assertEqual(len(r["topics"]),2)
            self.assertEqual(r["evaluacion"],"SIN_VERIFICAR_POR_FUENTE_INDEPENDIENTE")
            self.assertTrue(all(x["evidence"]["estatus"]=="CANDIDATE_PENDING_TCSA" for x in r["topics"]))
            mem.cerrar()
    def test_sin_fuente_no_inventa(self):
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            r=investigar_lote(mem,FakeBackend(),(Modelo("A","/a"),Modelo("B","/b")),1,fetch=lambda q: None)
            self.assertEqual(len(r["topics"]),0)
            self.assertEqual(len(r["errors"]),1)
            mem.cerrar()

if __name__=="__main__":
    unittest.main()
