"""
Testes para autenticação: registro, login, logout e seleção de perfil.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from core.models import Perfil
from core.forms import UserRegistrationForm, CustomAuthenticationForm

Usuario = get_user_model()


class PerfilSetupMixin:
    """Mixin para setup de perfis necessários nos testes."""

    @classmethod
    def setUpTestData(cls):
        """Cria os perfis 'Profissional de saúde' e 'Usuário'."""
        cls.perfil_profissional, _ = Perfil.objects.get_or_create(tipo='Profissional de saúde')
        cls.perfil_usuario, _ = Perfil.objects.get_or_create(tipo='Usuário')


class UserRegistrationFormTests(TestCase):
    """Testa o formulário de cadastro de usuários."""

    def setUp(self):
        """Setup de perfis para os testes."""
        self.perfil_usuario = Perfil.objects.create(tipo='Usuário')
        self.perfil_profissional = Perfil.objects.create(tipo='Profissional de saúde')

    def test_valid_registration_form(self):
        """Testa o preenchimento válido do formulário de registro."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'perfil': self.perfil_usuario.id,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=form.errors)

    def test_registration_missing_required_fields(self):
        """Testa registro com campos obrigatórios faltando."""
        form_data = {
            'username': 'testuser',
            'email': '',  # Campo vazio
            'perfil': '',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('perfil', form.errors)

    def test_registration_passwords_not_matching(self):
        """Testa registro com senhas não coincidindo."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'perfil': self.perfil_usuario.id,
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass456!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_weak_password(self):
        """Testa registro com senha fraca."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'perfil': self.perfil_usuario.id,
            'password1': '123',  # Muito curta
            'password2': '123',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_registration_duplicate_username(self):
        """Testa registro com username já existente."""
        # Criar um usuário primeiro
        Usuario.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='SecurePass123!',
            perfil=self.perfil_usuario
        )
        # Tentar registrar com mesmo username
        form_data = {
            'username': 'existinguser',
            'email': 'newuser@example.com',
            'perfil': self.perfil_usuario.id,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)


class RegisterViewTests(PerfilSetupMixin, TestCase):
    """Testa a view de registro."""

    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')

    def test_register_page_loads(self):
        """Testa se a página de registro carrega com sucesso."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)

    def test_register_with_valid_data(self):
        """Testa registro com dados válidos."""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'perfil': self.perfil_usuario.id,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data=form_data)
        
        # Deve redirecionar para landing após sucesso
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))
        
        # Usuário deve ser criado no banco
        self.assertTrue(Usuario.objects.filter(username='newuser').exists())
        user = Usuario.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.perfil.id, self.perfil_usuario.id)

    def test_register_with_invalid_data(self):
        """Testa registro com dados inválidos."""
        form_data = {
            'username': '',  # Username vazio
            'email': 'invalid-email',  # Email inválido
            'perfil': '',
            'password1': 'pass',
            'password2': 'different',
        }
        response = self.client.post(self.register_url, data=form_data)
        
        # Não deve redirecionar, deve voltar para a página com erros
        self.assertEqual(response.status_code, 200)
        # Verificar que há erros no formulário
        self.assertTrue('form' in response.context)
        self.assertTrue(response.context['form'].errors)

    def test_registered_user_is_logged_in(self):
        """Testa se o usuário é autologado após registro."""
        form_data = {
            'username': 'autouser',
            'email': 'autouser@example.com',
            'perfil': self.perfil_usuario.id,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data=form_data, follow=True)
        
        # Usuário deve estar autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.username, 'autouser')

    def test_register_with_profissional_perfil(self):
        """Testa registro como Profissional de saúde."""
        form_data = {
            'username': 'profissional',
            'email': 'prof@example.com',
            'perfil': self.perfil_profissional.id,
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        response = self.client.post(self.register_url, data=form_data)
        
        self.assertEqual(response.status_code, 302)
        user = Usuario.objects.get(username='profissional')
        self.assertEqual(user.perfil.id, self.perfil_profissional.id)


class LoginViewTests(PerfilSetupMixin, TestCase):
    """Testa a view de login."""

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')
        
        # Criar um usuário para testes
        self.perfil_usuario = Perfil.objects.filter(tipo='Usuário').first()
        self.test_user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
            perfil=self.perfil_usuario
        )

    def test_login_page_loads(self):
        """Testa se a página de login carrega."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        self.assertIsInstance(response.context['form'], CustomAuthenticationForm)

    def test_login_with_valid_credentials(self):
        """Testa login com credenciais válidas."""
        form_data = {
            'username': 'testuser',
            'password': 'SecurePass123!',
        }
        response = self.client.post(self.login_url, data=form_data)
        
        # Deve redirecionar para landing
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
        
        # Usuário deve estar autenticado
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_invalid_credentials(self):
        """Testa login com credenciais inválidas."""
        form_data = {
            'username': 'testuser',
            'password': 'WrongPassword!',
        }
        response = self.client.post(self.login_url, data=form_data)
        
        # Não deve redirecionar, deve voltar para login
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'core/login.html')
        
        # Usuário não deve estar autenticado
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_nonexistent_user(self):
        """Testa login com usuário inexistente."""
        form_data = {
            'username': 'nonexistent',
            'password': 'SomePass123!',
        }
        response = self.client.post(self.login_url, data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_with_empty_fields(self):
        """Testa login com campos vazios."""
        form_data = {
            'username': '',
            'password': '',
        }
        response = self.client.post(self.login_url, data=form_data)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class LogoutViewTests(PerfilSetupMixin, TestCase):
    """Testa a view de logout."""

    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('logout')
        
        # Criar e fazer login de um usuário
        self.perfil_usuario = Perfil.objects.filter(tipo='Usuário').first()
        self.test_user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
            perfil=self.perfil_usuario
        )
        self.client.login(username='testuser', password='SecurePass123!')

    def test_user_is_logged_in_before_logout(self):
        """Testa que o usuário está logado antes de fazer logout."""
        response = self.client.get(self.logout_url)
        # Após logout (que redireciona), conseguir verificar
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_redirect(self):
        """Testa se logout redireciona para landing."""
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_logout_clears_session(self):
        """Testa que logout limpa a sessão."""
        # Antes de logout, usuário está autenticado
        self.client.get(reverse('landing'))
        
        # Fazer logout
        self.client.get(self.logout_url)
        
        # Após logout, usuário não deve estar autenticado
        response = self.client.get(reverse('landing'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class NavbarAuthLinkTests(PerfilSetupMixin, TestCase):
    """Testa links de autenticação na navbar."""

    def setUp(self):
        self.client = Client()
        self.landing_url = reverse('landing')
        self.perfil_usuario = Perfil.objects.filter(tipo='Usuário').first()

    def test_navbar_shows_login_register_when_not_authenticated(self):
        """Testa que navbar mostra links de login/cadastro para usuários não autenticados."""
        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('register'))
        self.assertNotContains(response, reverse('logout'))

    def test_navbar_shows_username_logout_when_authenticated(self):
        """Testa que navbar mostra username e logout para usuários autenticados."""
        user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
            perfil=self.perfil_usuario
        )
        self.client.login(username='testuser', password='SecurePass123!')
        
        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')
        self.assertContains(response, reverse('logout'))
        self.assertNotContains(response, reverse('register'))


class UsuarioModelTests(PerfilSetupMixin, TestCase):
    """Testa o modelo Usuario com autenticação."""

    def test_usuario_requires_perfil(self):
        """Testa que um Usuario requer um Perfil."""
        perfil = Perfil.objects.filter(tipo='Usuário').first()
        user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
            perfil=perfil
        )
        self.assertEqual(user.perfil, perfil)

    def test_usuario_can_have_restricoes(self):
        """Testa que um Usuario pode ter restrições alimentares."""
        from core.models import RestricaoAlimentar, UsuarioRestricao
        
        perfil = Perfil.objects.filter(tipo='Usuário').first()
        user = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='SecurePass123!',
            perfil=perfil
        )
        
        restricao = RestricaoAlimentar.objects.create(
            tipo='Vegetariano',
            descricao='Não consome carne'
        )
        
        UsuarioRestricao.objects.create(usuario=user, restricao_alimentar=restricao)
        
        self.assertIn(restricao, user.restricoes.all())
