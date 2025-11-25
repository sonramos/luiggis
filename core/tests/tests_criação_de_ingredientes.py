from django.test import TestCase
from core.models import Categoria, Ingrediente

class IngredientePrintTest(TestCase):

    def test_criar_ingrediente(self):
        cat = Categoria.objects.create(nome="Carboidrato")
        ing = Ingrediente.objects.create(
            nome="Arroz",
            caloria=130,
            categoria=cat
        )

        print("\n🟢 Ingrediente criado:", ing.nome)
        print("🟢 Calorias:", ing.caloria)
        print("🟢 Categoria vinculada:", ing.categoria.nome)

        self.assertEqual(ing.categoria.nome, "Carboidrato")
