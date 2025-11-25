from django.urls import path
from . import views

urlpatterns = [
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
]