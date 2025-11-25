from django.test import TestCase
from core.models import Categoria, Ingrediente, Perfil, Usuario


class CategoriaModelTest(TestCase):
    def test_criar_categoria(self):
        categoria = Categoria.objects.create(
            nome="Proteína",
            descricao="Alimentos ricos em proteína"
        )
        self.assertEqual(categoria.nome, "Proteína")
        self.assertTrue(Categoria.objects.exists())


class IngredienteModelTest(TestCase):
    def test_criar_ingrediente(self):
        categoria = Categoria.objects.create(nome="Carboidrato")

        ingrediente = Ingrediente.objects.create(
            nome="Arroz",
            caloria=130,
            categoria=categoria
        )

        self.assertEqual(ingrediente.nome, "Arroz")
        self.assertEqual(ingrediente.caloria, 130)
        self.assertEqual(ingrediente.categoria.nome, "Carboidrato")


class UsuarioModelTest(TestCase):
    def test_criar_usuario(self):
        perfil = Perfil.objects.create(tipo="Atleta")

        usuario = Usuario.objects.create_user(
            username="caio",
            password="123",
            perfil=perfil
        )

        self.assertEqual(usuario.username, "caio")
        self.assertEqual(usuario.perfil.tipo, "Atleta")
        self.assertTrue(usuario.check_password("123"))
