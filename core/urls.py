from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import CustomAuthenticationForm

urlpatterns = [
    # Landing Page
    path('', views.LandingPageView.as_view(), name='landing'),
    
    # Categoria (Opcional, mas útil para o CRUD completo)
    path('categorias/', views.CategoriaListView.as_view(), name='lista_categorias'),
    
    # Lista de Ingredientes (Read)
    path('ingredientes/', views.IngredienteListView.as_view(), name='lista_ingredientes'),
    
    # Adicionar Ingrediente (Create)
    path('ingredientes/adicionar/', views.IngredienteCreateView.as_view(), name='adicionar_ingrediente'),
    
    # Detalhe e Edição de Ingrediente (Update)
    path('ingredientes/editar/<int:pk>/', views.IngredienteUpdateView.as_view(), name='editar_ingrediente'),
    
    # Excluir Ingrediente (Delete)
    path('ingredientes/excluir/<int:pk>/', views.IngredienteDeleteView.as_view(), name='excluir_ingrediente'),

    # Receitas
    path('receitas/', views.ReceitaListView.as_view(), name='lista_receitas'),
    path('receitas/<int:pk>/', views.ReceitaDetailView.as_view(), name='detalhes_receita'),
    
    # Geração de Receita via IA
    path('receitas/gerar/', views.GerarReceitaIAView.as_view(), name='receita_geracao_ia'),

    # Autenticação
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    # Perfil do usuário
    path('accounts/profile/', views.PerfilDetailView.as_view(), name='perfil'),
    path('accounts/profile/editar/', views.PerfilUpdateView.as_view(), name='perfil_editar'),
]