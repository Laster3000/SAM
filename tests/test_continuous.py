import tempfile
import json
import unittest
from pathlib import Path
from sam.curriculum import cargar, Tarea
from sam.learning import Memoria, ejecutar_sesion
from sam.core import Modelo
from sam.worker import ejecutar

class ModeloFake:
    def generar(self,modelo,instrucciones,pregunta):
        if "crítico independiente" in instrucciones.lower():
            return "Verifica los supuestos y unidades."
        return "RESPUESTA: 323"

class TestContinuous(unittest.TestCase):
    def test_curriculo_masivo_diverso(self):
        tasks=cargar()
        self.assertGreater(len(tasks),1000)
        self.assertGreaterEqual(len({t.domain for t in tasks}),7)
        self.assertEqual(len(tasks),len(set(t.id for t in tasks)))
        self.assertTrue(any(t.grade=="revision_humana" for t in tasks))
    def test_memoria_prioriza_novedad_y_perdura(self):
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            tasks=[Tarea("a","matematicas","s","17x19","323","test"),
                   Tarea("b","matematicas","s","2+2","4","test")]
            chosen=mem.elegir(tasks,2)
            self.assertEqual(len(chosen),2)
            mem.agregar("run-001",chosen[0],{},success=True)
            self.assertEqual(mem.elegir(tasks,1)[0].id,chosen[1].id)
            mem.cerrar()
            mem2=Memoria(d)
            self.assertEqual(len(mem2.estadisticas()),1)
            self.assertEqual(len((Path(d)/"eventos.jsonl").read_text().splitlines()),1)
            mem2.cerrar()
    def test_lote_2_agentes_sin_promocion(self):
        with tempfile.TemporaryDirectory() as d:
            m=Memoria(d)
            tasks=[Tarea("a","matematicas","s","17x19","323","fuente"),
                   Tarea("b","interdominios","analogia","analiza","ref","fuente","revision_humana")]
            result=ejecutar_sesion(m,tasks,(Modelo("A","/a"),Modelo("B","/b")),ModeloFake(),2)
            self.assertEqual(result["resumen"]["evaluadas"],2)
            self.assertEqual(result["resumen"]["correctas_literalmente"],1)
            self.assertTrue(all(x["estado"]=="CANDIDATE_PENDING_TCSA" for x in result["capsulas_candidatas"]))
            self.assertEqual(result["canonical_state"],"CANDIDATE_PENDING_TCSA")
            m.cerrar()
    def test_importar_idempotente(self):
        with tempfile.TemporaryDirectory() as d:
            a=Memoria(Path(d)/"a")
            t=Tarea("a","matematicas","s","p","1","s")
            a.agregar("id",t,{},success=False)
            a.cerrar()
            b=Memoria(Path(d)/"b")
            b.importar_jsonl(Path(d)/"a"/"eventos.jsonl")
            b.importar_jsonl(Path(d)/"a"/"eventos.jsonl")
            self.assertEqual(b.estadisticas()["a"]["intentos"],1)
            b.cerrar()
    def test_cli_dry_run(self):
        self.assertEqual(ejecutar(["--dry-run"]),0)

if __name__=="__main__":
    unittest.main()
