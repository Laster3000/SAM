"""R008: automejora como propuesta verificable, sin ejecución arbitraria."""
from __future__ import annotations
import ast
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

from sam.core import Modelo, PENDING
from sam.curriculum import cargar
from sam.learning import Memoria
from sam.quality import separar
from sam.self_evolve import (
    detectar_fallos, codigo_candidato, experimentar, guardar_candidato,
)


class FakeBackend:
    def __init__(self, sugerencia="ESTRATEGIA: descomponer"):
        self.calls=[]
        self.sugerencia=sugerencia

    def generar(self, modelo, instrucciones, pregunta):
        self.calls.append((modelo.nombre,instrucciones,pregunta))
        if "diseñador de métodos" in instrucciones:
            return self.sugerencia
        if "crítico independiente de estrategias" in instrucciones:
            return "Revisa si la estrategia transfiere y busca contraejemplos."
        match=re.search(r"(\d+) × (\d+)",pregunta)
        if match and "Descompón el problema" in instrucciones:
            return "RESPUESTA: "+str(int(match[1])*int(match[2]))
        return "RESPUESTA: 0"


class TestAutoMejora(unittest.TestCase):
    def setUp(self):
        self.models=(Modelo("A","/a"),Modelo("B","/b"))
        practice,hold=separar(cargar())
        self.practica=practice
        self.holdout=hold
        self.aritmetica=[t for t in practice
                         if t.domain=="matematicas" and t.skill=="aritmetica"]
        self.assertGreaterEqual(len(self.aritmetica),5)

    def marcar_fallos(self,mem):
        for i,t in enumerate(self.aritmetica[:2]):
            mem.agregar("historico-"+str(i),t,
                        {"respuesta_final":"0","evaluacion_final":{"verificada":False}},
                        success=False,evaluation_set="practice")

    def test_sin_datos_no_hay_candidatos(self):
        with TemporaryDirectory() as d:
            mem=Memoria(d)
            model=FakeBackend()
            r=experimentar(mem,self.practica,self.models,model,max_cases=2)
            self.assertEqual(r["resultado"],"SIN_ERRORES_RECURRENTES_SUFICIENTES")
            self.assertEqual(model.calls,[])
            mem.cerrar()

    def test_detecta_fallos_distintos_pero_ignora_holdout(self):
        with TemporaryDirectory() as d:
            mem=Memoria(d)
            self.marcar_fallos(mem)
            h=next(t for t in self.holdout if t.skill=="aritmetica")
            mem.agregar("hold",h,{},success=False,evaluation_set="holdout")
            focus=detectar_fallos(mem)
            self.assertEqual(focus[0]["fallos_en_tareas_distintas"],2)
            self.assertEqual(focus[0]["habilidad"],"aritmetica")
            mem.cerrar()

    def test_codigo_limitado_catalogo_no_inyeccion(self):
        source=codigo_candidato("descomponer")
        tree=ast.parse(source)
        self.assertTrue(any(isinstance(x,ast.FunctionDef) for x in tree.body))
        self.assertFalse(any(isinstance(x,(ast.Import,ast.ImportFrom,ast.Call))
                             for x in ast.walk(tree)))
        with self.assertRaises(ValueError):
            codigo_candidato("__import__('os').system('id')")

    def test_mejora_exploratoria_y_ausencia_ejecucion(self):
        with TemporaryDirectory() as d:
            mem=Memoria(Path(d)/"db")
            self.marcar_fallos(mem)
            model=FakeBackend()
            report=experimentar(mem,self.practica,self.models,model,max_cases=2)
            self.assertEqual(report["estado"],PENDING)
            self.assertFalse(report["codigo_ejecutado"])
            self.assertEqual(report["resumen"]["ejercicios"],2)
            self.assertEqual(report["resumen"]["aciertos_actual"],0)
            self.assertEqual(report["resumen"]["aciertos_candidato"],2)
            self.assertEqual(report["resultado"],"MEJORA_EXPLORATORIA_CANDIDATA")
            self.assertTrue(all(t["id"] not in [x.id for x in self.aritmetica[:2]]
                                for t in report["casos"]))
            self.assertEqual(report["propuesta"]["origen"],"MODELO")
            assert len(model.calls)==6
            for _,inst,prompt in model.calls[2:]:
                self.assertNotIn("Resultado comprobado",prompt)
                self.assertNotIn("Referencia esperada",prompt)
            paths=guardar_candidato(report,Path(d)/"propuestas")
            self.assertTrue(Path(paths["reporte"]).is_file())
            self.assertEqual(len(list((Path(d)/"propuestas").glob("*.py"))),1)
            mem.cerrar()

    def test_inyeccion_de_modelo_no_se_convierte_en_codigo(self):
        with TemporaryDirectory() as d:
            mem=Memoria(Path(d)/"db")
            self.marcar_fallos(mem)
            model=FakeBackend("ESTRATEGIA: import\nimport os")
            report=experimentar(mem,self.practica,self.models,model,max_cases=2)
            self.assertEqual(report["propuesta"]["origen"],"REGLA_DE_RESPALDO")
            self.assertEqual(report["propuesta"]["estrategia"],"descomponer")
            self.assertFalse(report["codigo_ejecutado"])
            mem.cerrar()

if __name__=="__main__":
    unittest.main()
