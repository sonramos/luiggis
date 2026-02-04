# core/api_urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    PerfilViewSet, RestricaoAlimentarViewSet, CategoriaViewSet,
    IngredienteViewSet, ReceitaViewSet, UsuarioViewSet,
    ListaDeCompraViewSet, AgendaAlimentarViewSet, DietaViewSet,
    RefeicaoViewSet
)

# Cria o router e registra os viewsets
router = DefaultRouter()
# router.register(r'perfis', PerfilViewSet, basename='perfil')
router.register(r'restricoes', RestricaoAlimentarViewSet, basename='restricao')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'ingredientes', IngredienteViewSet, basename='ingrediente')
router.register(r'receitas', ReceitaViewSet, basename='receita')
router.register(r'agendas', AgendaAlimentarViewSet, basename='agenda')
router.register(r'dietas', DietaViewSet, basename='dieta')
router.register(r'refeicoes', RefeicaoViewSet, basename='refeicao')
# router.register(r'usuarios', UsuarioViewSet, basename='usuario')
# router.register(r'listas-compra', ListaDeCompraViewSet, basename='lista-compra')

urlpatterns = [
    path('', include(router.urls)),
]
