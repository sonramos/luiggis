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
    # Editar/Excluir receitas (apenas para donos ou superuser)
    path('receitas/editar/<int:pk>/', views.ReceitaUpdateView.as_view(), name='editar_receita'),
    path('receitas/excluir/<int:pk>/', views.ReceitaDeleteView.as_view(), name='excluir_receita'),
    
    # Geração de Receita via IA
    path('receitas/gerar/', views.GerarReceitaIAView.as_view(), name='receita_geracao_ia'),

    # Dietas
    path('dietas/', views.DietaListView.as_view(), name='listar_dietas'),
    path('dietas/criar/', views.DietaCreateView.as_view(), name='criar_dieta'),
    path('dietas/<int:pk>/editar/', views.DietaUpdateView.as_view(), name='editar_dieta'),
    path('dietas/<int:pk>/excluir/', views.DietaDeleteView.as_view(), name='excluir_dieta'),

    # Refeições
    path('refeicoes/', views.RefeicaoListView.as_view(), name='listar_refeicoes'),
    path('refeicoes/criar/', views.RefeicaoCreateView.as_view(), name='criar_refeicao'),
    path('agendas/<int:agenda_pk>/dia/<int:day_num>/refeicao/', views.RefeicaoSelecionarOuCriarView.as_view(), name='selecionar_ou_criar_refeicao'),
    path('agendas/<int:agenda_pk>/dia/<int:day_num>/refeicao/criar/', views.RefeicaoCreateAgendaDiaView.as_view(), name='criar_refeicao_agenda_dia'),
    path('agendas/<int:agenda_pk>/dia/<int:day_num>/refeicao/<int:refeicao_pk>/adicionar/', views.RefeicaoAdicionarExistenteView.as_view(), name='adicionar_refeicao_existente'),
    path('refeicoes/<int:pk>/editar/', views.RefeicaoUpdateView.as_view(), name='editar_refeicao'),
    path('refeicoes/<int:pk>/excluir/', views.RefeicaoDeleteView.as_view(), name='excluir_refeicao'),

    # Agendas Alimentares
    path('agendas/', views.AgendaAlimentarListView.as_view(), name='listar_agendas'),
    path('agendas/criar/', views.AgendaAlimentarCreateView.as_view(), name='criar_agenda'),
    path('agendas/<int:pk>/editar/', views.AgendaAlimentarUpdateView.as_view(), name='editar_agenda'),
    path('agendas/<int:pk>/excluir/', views.AgendaAlimentarDeleteView.as_view(), name='excluir_agenda'),
    path('agendas/<int:pk>/semanal/', views.AgendaAlimentarWeeklyView.as_view(), name='agenda_semanal'),

    # Listas de Compra
    path('listas-compra/', views.ListaDeCompraListView.as_view(), name='listar_listas_compra'),
    path('listas-compra/criar/', views.ListaDeCompraCreateView.as_view(), name='criar_lista_compra'),
    path('listas-compra/<int:pk>/excluir/', views.ListaDeCompraDeleteView.as_view(), name='excluir_lista_compra'),
    path('listas-compra/<int:pk>/imprimir/', views.ListaDeCompraPrintView.as_view(), name='imprimir_lista_compra'),

    # Autenticação
    path('accounts/login/', auth_views.LoginView.as_view(template_name='core/login.html', authentication_form=CustomAuthenticationForm), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.RegisterView.as_view(), name='register'),
    # Perfil do usuário
    path('accounts/profile/', views.PerfilDetailView.as_view(), name='perfil'),
    path('accounts/profile/editar/', views.PerfilUpdateView.as_view(), name='perfil_editar'),
]