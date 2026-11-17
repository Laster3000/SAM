import unittest
from sam.chain import siguiente,DEFAULT_CHAIN_LIMIT,main

class TestChain(unittest.TestCase):
    def test_encadena_sin_esperar_hasta_limite(self):
        self.assertEqual(DEFAULT_CHAIN_LIMIT,3)
        self.assertEqual(siguiente("0"),1)
        self.assertEqual(siguiente("1"),2)
        self.assertIsNone(siguiente("2"))
    def test_rechaza_entradas_malformadas(self):
        for s in ("-1","3","NaN","0;echo","99999",""):
            with self.subTest(s=s), self.assertRaises(ValueError):
                siguiente(s)
    def test_limites_disciplinados(self):
        with self.assertRaises(ValueError):
            siguiente(0,0)
        with self.assertRaises(ValueError):
            siguiente(0,999)
        self.assertIsNone(siguiente("0",1))

if __name__=="__main__":
    unittest.main()
