import unittest
from sam.architecture import Arquitectura,Componente,Modo,CRITICOS

class TestArquitectura(unittest.TestCase):
    def setUp(self):
        self.items=[
            Componente("autoridad","1",frozenset({"identidad"}),protegido=True),
            Componente("creador","1",frozenset({"crear","explorar"})),
            Componente("critico","1",frozenset({"criticar"}),dependencias=frozenset({"autoridad"})),
        ]
    def test_trabajo_no_puede_mutar(self):
        a=Arquitectura(self.items,Modo.TRABAJO)
        with self.assertRaises(PermissionError):
            a.proponer_fusion(["creador","critico"])
        self.assertEqual(a.disponibles_trabajo(),[])
    def test_evolucion_aislada_fusion(self):
        a=Arquitectura(self.items,Modo.EVOLUCION)
        before=a.manifest()
        plan=a.proponer_fusion(["creador","critico"])
        self.assertEqual(plan["estado"],"CANDIDATE_PENDING_TCSA")
        self.assertFalse(plan["aplicado"])
        self.assertFalse(plan["promocion_automatica"])
        self.assertEqual(plan["rollback"]["sha256"],before["revision_sha256"])
        self.assertEqual(a.manifest(),before)
    def test_critico_protegido_no_fusionar(self):
        a=Arquitectura(self.items,Modo.EVOLUCION)
        with self.assertRaises(PermissionError):
            a.proponer_fusion(["autoridad","creador"])
    def test_poda_reversible_y_dependencias(self):
        a=Arquitectura(self.items,Modo.EVOLUCION)
        with self.assertRaises(PermissionError):
            a.proponer_poda("autoridad")
        self.assertFalse(a.proponer_poda("creador")["borrado_definitivo"])
    def test_division_incompatible(self):
        a=Arquitectura(self.items,Modo.EVOLUCION)
        with self.assertRaises(ValueError):
            a.proponer_division("creador",{"crear"},{"inventado"})
        with self.assertRaises(ValueError):
            a.proponer_division("creador",{"crear"},{"crear"})
        self.assertEqual(len(a.proponer_division("creador",{"crear"},{"explorar"})["salidas"]),2)
    def test_invariantes_de_dependencias(self):
        with self.assertRaises(ValueError):
            Arquitectura([Componente("creador","1",frozenset({"crear"}),dependencias=frozenset({"sin_nombre"}))])
        with self.assertRaises(ValueError):
            Arquitectura([Componente("agente_a","1",frozenset({"a"}),dependencias=frozenset({"agente_b"})),
                          Componente("agente_b","1",frozenset({"b"}),dependencias=frozenset({"agente_a"}))])
    def test_proteccion_nunca_omitida(self):
        for name in CRITICOS:
            with self.assertRaises(PermissionError):
                Componente(name,"1",frozenset({"funcion"}))
    def test_disponibles_de_trabajo_exigen_licencia_y_prueba(self):
        items=[Componente("creador","1",frozenset({"crear"}),evidencia="VERIFICADA_INDEPENDIENTEMENTE",licencia="Apache-2.0"),
               Componente("critico","1",frozenset({"criticar"}),evidencia="NO_PROBADA",licencia="Apache-2.0")]
        self.assertEqual(Arquitectura(items,Modo.TRABAJO).disponibles_trabajo(),["crear"])
        with self.assertRaises(PermissionError):
            Arquitectura(items,Modo.EVOLUCION).disponibles_trabajo()

if __name__=="__main__":
    unittest.main()
