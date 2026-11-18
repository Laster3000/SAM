from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest
from sam.curriculum import cargar
from sam.learning import Memoria
from sam.ledger_union import combinar
from sam.quality import separar, auditar_ledger

def make(path,run_id,task):
    mem=Memoria(path)
    mem.agregar(run_id,task,{"respuesta_final":task.expected,
        "evaluacion_final":{"verificada":True}},success=True,evaluation_set="practice")
    mem.cerrar()
    return path/"eventos.jsonl"

class TestUnionLedgers(unittest.TestCase):
    def test_combina_sin_perder_o_repetir(self):
        tasks,_=separar(cargar())
        exact=[t for t in tasks if t.grade=="exact" and t.expected is not None]
        with TemporaryDirectory() as d:
            root=Path(d)
            a=make(root/"a","run-a",exact[0])
            b=make(root/"b","run-b",exact[1])
            out=root/"unido.jsonl"
            r=combinar([a,b,a],out)
            self.assertEqual(r["eventos_unicos"],2)
            self.assertEqual(r["duplicados"],1)
            self.assertEqual(auditar_ledger(out)["events"],2)
            self.assertEqual(out.read_bytes().count(b"\n"),2)
    def test_conflicto_duplicado_detiene_sin_sobrescribir(self):
        tasks,_=separar(cargar())
        a_task=next(t for t in tasks if t.grade=="exact" and t.expected is not None)
        with TemporaryDirectory() as d:
            root=Path(d)
            a=make(root/"a","run-a",a_task)
            b=root/"b.jsonl"
            event=json.loads(a.read_text(encoding="utf-8"))
            event["utc"]="2020-01-01T00:00:00+00:00"
            b.write_text(json.dumps(event,ensure_ascii=False)+"\n",encoding="utf-8")
            out=root/"result.jsonl"
            out.write_text("sin tocar",encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Conflicto"):
                combinar([a,b],out)
            self.assertEqual(out.read_text(encoding="utf-8"),"sin tocar")
    def test_rechaza_jsonl_corrupto(self):
        tasks,_=separar(cargar())
        t=next(x for x in tasks if x.grade=="exact" and x.expected is not None)
        with TemporaryDirectory() as d:
            root=Path(d)
            a=make(root/"a","run-a",t)
            b=root/"b.jsonl";b.write_text("{}\n",encoding="utf-8")
            with self.assertRaises(ValueError):
                combinar([a,b],root/"out.jsonl")

if __name__=="__main__":
    unittest.main()
