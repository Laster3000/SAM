import unittest
from sam.core import Modelo
from sam.trabajo import atender

class FakeBackend:
    def __init__(self):self.calls=[]
    def generar(self,modelo,instrucciones,pregunta):
        self.calls.append((modelo.nombre,instrucciones,pregunta))
        return "Verifica las unidades." if "crítico independiente" in instrucciones.lower() else "RESPUESTA: cálculo provisional"

class TestTrabajo(unittest.TestCase):
    def setUp(self):
        self.models=(Modelo("A","/no-model"),Modelo("B","/no-model"))
    def test_dos_modelos_critican_sin_mutar(self):
        backend=FakeBackend()
        out=atender("Explica un problema",backend,self.models)
        self.assertEqual(out["modo"],"TRABAJO")
        self.assertEqual(out["estado"],"RESPUESTA_CANDIDATA_SIN_VALIDACION_EXTERNA")
        self.assertFalse(out["modificacion_de_codigo"])
        self.assertFalse(out["entrenamiento_de_pesos"])
        self.assertEqual(len(backend.calls),3)
        self.assertEqual(out["resultado"]["critico"],"B")
        self.assertFalse(out["resultado"]["evaluacion_final"]["verificada"])
    def test_no_acepta_encargo_invalido(self):
        for texto in ("","x"*9000):
            with self.subTest(n=len(texto)),self.assertRaises(ValueError):
                atender(texto,FakeBackend(),self.models)
    def test_no_acepta_un_solo_modelo(self):
        with self.assertRaises(ValueError):
            atender("Objetivo",FakeBackend(),self.models[:1])

if __name__=="__main__":
    unittest.main()
