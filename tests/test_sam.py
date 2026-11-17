import unittest
from dataclasses import dataclass
from sam.core import normalizar, evaluar, respuesta_estructurada, capsula_candidata, ciclo_dos_modelos, Modelo
from sam.agents import Agente, combinar_candidato, podar_candidato

class BackendFalso:
    def __init__(self):
        self.n = 0
    def generar(self, modelo, instrucciones, pregunta):
        self.n += 1
        return ["RESPUESTA: error", "Falta comprobar unidades y supuestos", "RESPUESTA: 323"][self.n-1]

class TestSAM(unittest.TestCase):
    def test_normalizacion(self):
        self.assertEqual(normalizar("¡SÍ!"), "si")
    def test_estricto(self):
        self.assertFalse(evaluar("no, pero sí", "no")["verificada"])
        self.assertTrue(evaluar("  Sí  ", "si")["verificada"])
    def test_respuesta_estructurada(self):
        self.assertIsNone(respuesta_estructurada("La respuesta podría ser no."))
        self.assertEqual(respuesta_estructurada("texto\nRESPUESTA: 323\n"), "323")
    def test_ciclo_dos_modelos(self):
        ciclo = ciclo_dos_modelos(BackendFalso(), Modelo("A", "/a"), Modelo("B", "/b"), "17 * 19", "323")
        self.assertTrue(ciclo["mejora_verificada"])
        self.assertIsNotNone(capsula_candidata("id", ciclo, "323", "casos.json"))
    def test_sin_promocion_por_respuesta_falsa(self):
        ciclo = ciclo_dos_modelos(BackendFalso(), Modelo("A", "/a"), Modelo("B", "/b"), "17 * 19", "999")
        self.assertIsNone(capsula_candidata("id", ciclo, "999", "casos.json"))
    def test_fusion_reversible(self):
        a=Agente("a", "1", frozenset({"corregir","optimizar"}))
        b=Agente("b", "2", frozenset({"recapitular"}))
        c=combinar_candidato([a,b],["corregir","recapitular"])
        self.assertFalse(c["promocion_automatica"])
        self.assertTrue(a.activo)
    def test_prohibir_piezas_criticas(self):
        a=Agente("a", "1", frozenset({"permisos","corregir"}))
        with self.assertRaises(ValueError):
            combinar_candidato([a], ["permisos"])
        with self.assertRaises(ValueError):
            podar_candidato(a)
    def test_poda_sin_borrado(self):
        a=Agente("a", "1", frozenset({"corregir"}))
        p=podar_candidato(a)
        self.assertFalse(p["borrado_definitivo"])
        self.assertFalse(p["ejecutado"])

if __name__ == "__main__":
    unittest.main()
