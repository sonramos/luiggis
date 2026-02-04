# core/api_views.py
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import (
    Perfil, RestricaoAlimentar, Categoria, Ingrediente, Receita,
    ListaDeCompra, Usuario, AgendaAlimentar, Dieta, Refeicao
)
from .serializers import (
    PerfilSerializer, RestricaoAlimentarSerializer, CategoriaSerializer,
    IngredienteSerializer, IngredienteDetailSerializer,
    ReceitaSerializer, ReceitaDetailSerializer,
    UsuarioSerializer, UsuarioCreateSerializer,
    ListaDeCompraSerializer, AgendaAlimentarSerializer,
    DietaSerializer, RefeicaoSerializer
)


# --- Permissions Customizadas ---

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permissão customizada para permitir que apenas o dono do objeto possa editá-lo.
    """
    def has_object_permission(self, request, view, obj):
        # Permissões de leitura são permitidas para qualquer requisição
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Permissões de escrita só para o dono
        return obj.owner == request.user or request.user.is_superuser


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permissão para que apenas o dono ou admin possa acessar/editar.
    """
    def has_object_permission(self, request, view, obj):
        # Admin pode tudo
        if request.user.is_superuser:
            return True
        
        # Verifica se o objeto tem atributo 'owner' ou 'usuario'
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False


# --- ViewSets ---

class PerfilViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet somente leitura para Perfis.
    GET /api/perfis/ - Lista todos os perfis
    GET /api/perfis/{id}/ - Detalhes de um perfil
    """
    queryset = Perfil.objects.all()
    serializer_class = PerfilSerializer
    permission_classes = [permissions.AllowAny]


class RestricaoAlimentarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet somente leitura para Restrições Alimentares.
    GET /api/restricoes/ - Lista todas as restrições
    GET /api/restricoes/{id}/ - Detalhes de uma restrição
    """
    queryset = RestricaoAlimentar.objects.filter(is_active=True)
    serializer_class = RestricaoAlimentarSerializer
    permission_classes = [permissions.AllowAny]


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Categorias.
    GET /api/categorias/ - Lista todas as categorias
    POST /api/categorias/ - Criar categoria (requer autenticação)
    GET /api/categorias/{id}/ - Detalhes de uma categoria
    PUT/PATCH /api/categorias/{id}/ - Atualizar categoria (requer autenticação)
    DELETE /api/categorias/{id}/ - Deletar categoria (requer autenticação)
    """
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nome', 'descricao']
    ordering_fields = ['nome', 'id']
    ordering = ['nome']


class IngredienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Ingredientes.
    GET /api/ingredientes/ - Lista todos os ingredientes
    POST /api/ingredientes/ - Criar ingrediente (requer autenticação)
    GET /api/ingredientes/{id}/ - Detalhes de um ingrediente
    PUT/PATCH /api/ingredientes/{id}/ - Atualizar ingrediente (requer autenticação)
    DELETE /api/ingredientes/{id}/ - Deletar ingrediente (requer autenticação)
    
    Filtros disponíveis: categoria, nome, caloria, exclude_restricoes
    Busca: nome
    Ordenação: nome, caloria, id
    """
    queryset = Ingrediente.objects.select_related('categoria').all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['categoria', 'categoria__nome']
    search_fields = ['nome']
    ordering_fields = ['nome', 'caloria', 'id']
    ordering = ['nome']
    
    def get_queryset(self):
        """
        Filtra ingredientes excluindo aqueles que têm restrições do usuário.
        Parâmetro: ?exclude_restricoes=user_id
        """
        queryset = Ingrediente.objects.select_related('categoria').all()
        exclude_restricoes = self.request.query_params.get('exclude_restricoes', None)
        
        if exclude_restricoes and self.request.user.is_authenticated:
            # Se parâmetro foi passado, filtra por ID do usuário
            try:
                user_id = int(exclude_restricoes)
                user = Usuario.objects.get(id=user_id)
                user_restricoes = user.restricoes.all()
                # Excluir ingredientes que têm alguma restrição do usuário
                queryset = queryset.exclude(restricoes__in=user_restricoes).distinct()
            except (ValueError, Usuario.DoesNotExist):
                pass
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return IngredienteDetailSerializer
        return IngredienteSerializer


class ReceitaViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Receitas.
    GET /api/receitas/ - Lista receitas do usuário logado (ou todas se admin)
    POST /api/receitas/ - Criar receita (requer autenticação)
    GET /api/receitas/{id}/ - Detalhes de uma receita
    PUT/PATCH /api/receitas/{id}/ - Atualizar receita (requer ser o dono)
    DELETE /api/receitas/{id}/ - Deletar receita (requer ser o dono)
    GET /api/receitas/minhas/ - Lista apenas minhas receitas
    GET /api/receitas/ia/ - Lista receitas geradas por IA
    
    Filtros disponíveis: is_ai_generated, owner
    Busca: titulo, instrucoes
    Ordenação: titulo, tempo_preparo, id
    """
    serializer_class = ReceitaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_ai_generated', 'owner']
    search_fields = ['titulo', 'instrucoes']
    ordering_fields = ['titulo', 'tempo_preparo', 'id']
    ordering = ['-id']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Usuários autenticados veem suas próprias receitas
            # Admins veem todas
            if user.is_superuser:
                return Receita.objects.select_related('owner').prefetch_related('ingredientes').all()
            return Receita.objects.filter(owner=user).select_related('owner').prefetch_related('ingredientes')
        # Usuários não autenticados não veem receitas
        return Receita.objects.none()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReceitaDetailSerializer
        return ReceitaSerializer
    
    def perform_create(self, serializer):
        # Atribui o usuário logado como owner
        serializer.save(owner=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def minhas(self, request):
        """Endpoint customizado para listar apenas receitas do usuário logado."""
        receitas = Receita.objects.filter(owner=request.user)
        serializer = self.get_serializer(receitas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def ia(self, request):
        """Endpoint customizado para listar receitas geradas por IA."""
        receitas = self.get_queryset().filter(is_ai_generated=True)
        serializer = self.get_serializer(receitas, many=True)
        return Response(serializer.data)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Usuários.
    GET /api/usuarios/ - Lista usuários (apenas admin)
    POST /api/usuarios/ - Criar usuário (registro público)
    GET /api/usuarios/{id}/ - Detalhes de um usuário (apenas próprio ou admin)
    PUT/PATCH /api/usuarios/{id}/ - Atualizar usuário (apenas próprio ou admin)
    DELETE /api/usuarios/{id}/ - Deletar usuário (apenas admin)
    GET /api/usuarios/me/ - Retorna dados do usuário logado
    """
    queryset = Usuario.objects.select_related('perfil').prefetch_related('restricoes').all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            # Registro público
            return [permissions.AllowAny()]
        elif self.action in ['list', 'destroy']:
            # Apenas admin pode listar todos ou deletar
            return [permissions.IsAdminUser()]
        else:
            # Outras ações requerem autenticação
            return [permissions.IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Usuario.objects.all()
        elif user.is_authenticated:
            # Usuários comuns só veem a si mesmos
            return Usuario.objects.filter(id=user.id)
        return Usuario.objects.none()
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Retorna os dados do usuário logado."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class ListaDeCompraViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Listas de Compra.
    GET /api/listas-compra/ - Lista todas as listas de compra
    POST /api/listas-compra/ - Criar lista de compra
    GET /api/listas-compra/{id}/ - Detalhes de uma lista
    PUT/PATCH /api/listas-compra/{id}/ - Atualizar lista
    DELETE /api/listas-compra/{id}/ - Deletar lista
    """
    queryset = ListaDeCompra.objects.prefetch_related('ingredientes').all()
    serializer_class = ListaDeCompraSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['data_criacao', 'id']
    ordering = ['-data_criacao']


class AgendaAlimentarViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Agendas Alimentares.
    GET /api/agendas/ - Lista agendas do usuário logado
    POST /api/agendas/ - Criar agenda
    GET /api/agendas/{id}/ - Detalhes de uma agenda
    PUT/PATCH /api/agendas/{id}/ - Atualizar agenda
    DELETE /api/agendas/{id}/ - Deletar agenda
    """
    serializer_class = AgendaAlimentarSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_active', 'is_google_agenda']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return AgendaAlimentar.objects.all()
        return AgendaAlimentar.objects.filter(usuario=user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class DietaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Dietas.
    GET /api/dietas/ - Lista dietas do usuário logado
    POST /api/dietas/ - Criar dieta
    GET /api/dietas/{id}/ - Detalhes de uma dieta
    PUT/PATCH /api/dietas/{id}/ - Atualizar dieta
    DELETE /api/dietas/{id}/ - Deletar dieta
    """
    serializer_class = DietaSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['total_caloria', 'id']
    ordering = ['-id']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Dieta.objects.all()
        return Dieta.objects.filter(usuario=user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class RefeicaoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Refeições.
    GET /api/refeicoes/ - Lista refeições do usuário logado
    POST /api/refeicoes/ - Criar refeição
    GET /api/refeicoes/{id}/ - Detalhes de uma refeição
    PUT/PATCH /api/refeicoes/{id}/ - Atualizar refeição
    DELETE /api/refeicoes/{id}/ - Deletar refeição
    """
    serializer_class = RefeicaoSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tipo_refeicao', 'date']
    ordering_fields = ['date', 'tipo_refeicao', 'id']
    ordering = ['-date', 'tipo_refeicao']
    
    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Refeicao.objects.all()
        return Refeicao.objects.filter(usuario=user)
    
    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)
