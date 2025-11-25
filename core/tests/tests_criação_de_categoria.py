from django.test import TestCase
from core.models import Categoria

class CategoriaPrintTest(TestCase):

    def test_criar_categoria(self):
        categoria = Categoria.objects.create(
            nome="Proteína",
            descricao="Rica em aminoácidos"
        )

        print("\n🟢 Categoria criada:", categoria.nome)
        print("🟢 Descrição:", categoria.descricao)

        self.assertEqual(categoria.nome, "Proteína")
        self.assertTrue(Categoria.objects.exists())