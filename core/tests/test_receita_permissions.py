from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Perfil, Receita

User = get_user_model()

class ReceitaPermissionTests(TestCase):

    def setUp(self):
        perfil = Perfil.objects.create(tipo='usuario')
        self.owner = User.objects.create_user(username='owner', password='pass', perfil=perfil)
        self.other = User.objects.create_user(username='other', password='pass', perfil=perfil)
        self.receita = Receita.objects.create(titulo='Test', instrucoes='Do', tempo_preparo=10, owner=self.owner)

    def test_owner_can_edit(self):
        self.client.login(username='owner', password='pass')
        url = reverse('editar_receita', kwargs={'pk': self.receita.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_owner_cannot_edit(self):
        self.client.login(username='other', password='pass')
        url = reverse('editar_receita', kwargs={'pk': self.receita.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_non_owner_cannot_delete(self):
        self.client.login(username='other', password='pass')
        url = reverse('excluir_receita', kwargs={'pk': self.receita.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_owner_can_delete(self):
        self.client.login(username='owner', password='pass')
        url = reverse('excluir_receita', kwargs={'pk': self.receita.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
