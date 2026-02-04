from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Perfil, Ingrediente

User = get_user_model()

class IngredientePermissionTests(TestCase):

    def setUp(self):
        perfil = Perfil.objects.create(tipo='usuario')
        self.user = User.objects.create_user(username='user1', password='pass', perfil=perfil)
        self.ingrediente = Ingrediente.objects.create(nome='Batata', caloria=100)

    def test_anonymous_redirect_create(self):
        url = reverse('adicionar_ingrediente')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_logged_in_can_access_create(self):
        self.client.login(username='user1', password='pass')
        url = reverse('adicionar_ingrediente')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirect_edit(self):
        url = reverse('editar_ingrediente', kwargs={'pk': self.ingrediente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_logged_in_can_access_edit(self):
        self.client.login(username='user1', password='pass')
        url = reverse('editar_ingrediente', kwargs={'pk': self.ingrediente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_anonymous_redirect_delete(self):
        url = reverse('excluir_ingrediente', kwargs={'pk': self.ingrediente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response['Location'])

    def test_logged_in_can_access_delete(self):
        self.client.login(username='user1', password='pass')
        url = reverse('excluir_ingrediente', kwargs={'pk': self.ingrediente.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
