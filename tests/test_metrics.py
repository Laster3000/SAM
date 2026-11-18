import unittest
from sam.metrics import resumir

class TestLearningEvidence(unittest.TestCase):
    def test_no_se_confunde_contador_con_aprendizaje(self):
        eventos=[
            {"domain":"fisica","task_id":"res-1","correct":True,
             "payload":{"evaluation_set":"holdout"}},
            {"domain":"fisica","task_id":"res-1","correct":False,
             "payload":{"evaluation_set":"holdout"}},
            {"domain":"matematicas","task_id":"practice-1","correct":True,
             "payload":{"evaluation_set":"practice"}}
        ]
        x=resumir(eventos)
        self.assertEqual(x["holdout_unicos"],1)
        self.assertEqual(x["holdout_intentos"],2)
        self.assertEqual(x["holdout_repeticiones"],1)
        self.assertFalse(x["aprendizaje_demostrado"])
        self.assertFalse(x["generalizacion_certificada"])
        self.assertFalse(x["benchmark_independiente"])
    def test_cero_casos(self):
        x=resumir([])
        self.assertEqual(x["holdout_unicos"],0)
        self.assertEqual(x["dominios"],{})
        self.assertFalse(x["pesos_entrenados"])
    def test_dataset_desconocido_rechazado(self):
        with self.assertRaises(ValueError):
            resumir([{"domain":"a","task_id":"a","correct":True,
                      "payload":{"evaluation_set":"promoted"}}])

if __name__=="__main__":
    unittest.main()
