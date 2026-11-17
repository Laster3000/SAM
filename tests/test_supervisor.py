import unittest
from sam.supervisor import delay

class TestSupervisor(unittest.TestCase):
    def test_escalado_de_reintentos(self):
        self.assertEqual(delay(0),30)
        self.assertEqual(delay(1),60)
        self.assertEqual(delay(2),120)
        self.assertEqual(delay(100),300)
    def test_maximo_controlado(self):
        self.assertEqual(delay(100,10),300)

if __name__=="__main__":
    unittest.main()
