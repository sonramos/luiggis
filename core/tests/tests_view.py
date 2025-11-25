from django.test import TestCase
from django.urls import reverse

class CategoriaListViewTest(TestCase):

    def test_resposta_status(self):
        url = reverse("lista_categorias")
        response = self.client.get(url)

        print("\n🟣 Status da resposta:", response.status_code)
        print("🟣 Template usado:", response.templates[0].name)

        self.assertEqual(response.status_code, 200)
