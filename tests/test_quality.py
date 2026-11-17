import json, tempfile, unittest
from pathlib import Path
from sam.core import Modelo, PENDING
from sam.curriculum import Tarea, cargar
from sam.learning import Memoria, ejecutar_sesion
from sam.quality import separar, es_reservada, ejemplos_verificados, contexto_ejemplos, auditar_ledger

class FakeModel:
    def generar(self, modelo, instrucciones, pregunta):
        if "crítico independiente" in instrucciones.lower():
            return "Verifica unidades y límites."
        return "RESPUESTA: 323"

class TestQuality(unittest.TestCase):
    def test_partition_stable(self):
        train, hold=separar(cargar())
        self.assertGreater(len(train),600)
        self.assertGreater(len(hold),80)
        self.assertTrue(all(not es_reservada(t.id) for t in train))
        self.assertTrue(all(es_reservada(t.id) for t in hold))
        self.assertFalse({x.id for x in train}&{x.id for x in hold})
    def test_memoria_y_holdout_aislados(self):
        train,hold=separar(cargar())
        sample=next(t for t in train if t.source.startswith("generador:"))
        same=next(t for t in train if t.id!=sample.id and t.skill==sample.skill)
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            mem.agregar("run",sample,{"respuesta_final":sample.expected,
                 "evaluacion_final":{"verificada":True}},success=True)
            data=ejemplos_verificados(mem,same)
            self.assertEqual(len(data),1)
            self.assertIn("NO instrucciones",contexto_ejemplos(data))
            self.assertEqual(ejemplos_verificados(mem,hold[0]),[])
            mem.cerrar()
    def test_nunca_reutiliza_error(self):
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            train,_=separar(cargar())
            a=next(t for t in train if t.source.startswith("generador:"))
            b=next(t for t in train if t.id!=a.id and t.skill==a.skill)
            mem.agregar("r",a,{},success=False)
            self.assertEqual(ejemplos_verificados(mem,b),[])
            mem.cerrar()
    def test_auditoria_refuta_suplantacion(self):
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            t=Tarea("a","matematicas","s","17×19","323","generador:aritmetica")
            mem.agregar("run-x",t,{"respuesta_final":"323",
                       "evaluacion_final":{"verificada":True}},success=True)
            path=Path(d)/"eventos.jsonl"
            self.assertEqual(auditar_ledger(path)["events"],1)
            obj=json.loads(path.read_text())
            obj["evento_id"]="0"*64
            path.write_text(json.dumps(obj,ensure_ascii=False)+"\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"evento_id"):
                auditar_ledger(path)
            mem.cerrar()
    def test_auditoria_no_acepta_respuesta_falsa(self):
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            t=Tarea("a","matematicas","s","17×19","323","generador:aritmetica")
            mem.agregar("run-y",t,{"respuesta_final":"0",
                       "evaluacion_final":{"verificada":True}},success=True)
            with self.assertRaisesRegex(ValueError,"respuesta aprobada"):
                auditar_ledger(Path(d)/"eventos.jsonl")
            mem.cerrar()
    def test_holdout_sin_ejemplos(self):
        _,hold=separar(cargar())
        with tempfile.TemporaryDirectory() as d:
            mem=Memoria(d)
            result=ejecutar_sesion(mem,hold[:2],(Modelo("A","/a"),Modelo("B","/b")),
                                   FakeModel(),2,holdout=True)
            self.assertEqual(result["dataset"],"holdout")
            self.assertTrue(all(x["ejemplos_recuperados"]==0 for x in result["cases"]))
            self.assertEqual(result["canonical_state"],PENDING)
            self.assertEqual(auditar_ledger(Path(d)/"eventos.jsonl")["by_dataset"]["holdout"],2)
            mem.cerrar()
if __name__=="__main__":
    unittest.main()
