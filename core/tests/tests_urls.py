from django.test import SimpleTestCase
from django.urls import reverse, resolve
from core.views import CategoriaListView


class TestCategoriaURLs(SimpleTestCase):
    def test_url_categorias_resolve(self):
        url = reverse("lista_categorias")
        resolved = resolve(url)
        self.assertEqual(
            resolved.func.view_class,
            CategoriaListView
        )
