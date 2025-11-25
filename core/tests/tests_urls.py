from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import CategoriaListView

class CategoriaURLPrintTest(SimpleTestCase):

    def test_url_categorias(self):
        url = reverse("lista_categorias")
        resolved = resolve(url)

        print("\n🔵 URL testada:", url)
        print("🔵 View encontrada:", resolved.func.view_class.__name__)

        self.assertEqual(resolved.func.view_class, CategoriaListView)
