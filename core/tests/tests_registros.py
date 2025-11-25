from django.test import TestCase
from core.models import Categoria

class CategoriaLoopTest(TestCase):

    def test_multiplas_categorias(self):
        nomes = ["Carboidrato", "Proteína", "Gordura Boa"]

        for nome in nomes:
            Categoria.objects.create(nome=nome)
            print(f"🟢 Categoria criada: {nome}")

        total = Categoria.objects.count()
        print("\n📌 Total de categorias criadas:", total)

        self.assertEqual(total, 3)
