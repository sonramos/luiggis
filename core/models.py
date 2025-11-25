# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- Modelos Sem Relacionamento de Chave Estrangeira Imediato ---

class Perfil(models.Model):
    """
    Representa os diferentes tipos de perfil de usuário.
    Tabela: PERFIL
    """
    # id é criado automaticamente
    tipo = models.CharField(max_length=30)

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfis"

    def __str__(self):
        return self.tipo

class RestricaoAlimentar(models.Model):
    """
    Representa as restrições alimentares que um usuário pode ter.
    Tabela: RESTRICAO_ALIMENTAR
    """
    # id é criado automaticamente
    tipo = models.CharField(max_length=30)
    descricao = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Restrição Alimentar"
        verbose_name_plural = "Restrições Alimentares"

    def __str__(self):
        return self.tipo

class Categoria(models.Model):
    """
    Representa as categorias de ingredientes (ex: Legumes, Carnes, Temperos).
    """
    nome = models.CharField(max_length=50, unique=True)
    descricao = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        verbose_name = "Categoria de Ingrediente"
        verbose_name_plural = "Categorias de Ingredientes"

    def __str__(self):
        return self.nome

class Ingrediente(models.Model):
    """
    Representa um ingrediente que pode ser usado em receitas.
    Tabela: INGREDIENTE
    """
    # id é criado automaticamente
    nome = models.CharField(max_length=100)

    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.SET_NULL, 
        null=True, # Permite valores nulos no banco de dados
        blank=True, # Permite campo vazio no formulário
        related_name='ingredientes'
    )
    caloria = models.IntegerField(
        help_text="Calorias por porção (ex: 100g)."
    )

    class Meta:
        verbose_name = "Ingrediente"
        verbose_name_plural = "Ingredientes"

    def __str__(self):
        return self.nome

class Receita(models.Model):
    """
    Representa uma receita, podendo ser gerada por IA.
    Tabela: RECEITA
    """
    # id é criado automaticamente
    titulo = models.CharField(max_length=100)
    instrucoes = models.TextField()
    tempo_preparo = models.IntegerField(
        help_text="Tempo de preparo em minutos."
    )
    prompt_geracao = models.TextField(
        blank=True,
        null=True,
        help_text="Prompt usado para gerar a receita pela IA, se aplicável."
    )
    is_ai_generated = models.BooleanField(default=False)
    
    # Relação N:M com Ingrediente (através da tabela IngredienteReceita)
    ingredientes = models.ManyToManyField(
        Ingrediente,
        through='IngredienteReceita',
        related_name='receitas'
    )

    class Meta:
        verbose_name = "Receita"
        verbose_name_plural = "Receitas"

    def __str__(self):
        return self.titulo

class ListaDeCompra(models.Model):
    """
    Representa uma lista de compras de ingredientes.
    Tabela: LISTA_DE_COMPRA
    """
    # id é criado automaticamente
    data_criacao = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    # Relação N:M com Ingrediente
    ingredientes = models.ManyToManyField(
        Ingrediente,
        through='IngredienteListaCompra',
        related_name='listas_de_compra'
    )

    class Meta:
        verbose_name = "Lista de Compra"
        verbose_name_plural = "Listas de Compra"

    def __str__(self):
        return f"Lista {self.id} ({self.data_criacao})"

# --- Modelos Com Relacionamentos de Chave Estrangeira ---

# Utilizamos o AbstractUser do Django para a autenticação padrão
class Usuario(AbstractUser):
    """
    Estende o modelo de usuário padrão do Django.
    Tabela: USUARIO (e usa a tabela auth_user)
    """
    # O AbstractUser já fornece: id, username, password_hash (password), email, is_active.

    # Adicionado para evitar conflito por AbstractUser já ter esses campos
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='core_usuario_set', # Nome único
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='core_user_permissions_set', # Nome único
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    # FK_PERFIL_id -> Relação 1:N com PERFIL (ON DELETE CASCADE)
    perfil = models.ForeignKey(
        Perfil,
        on_delete=models.CASCADE,
        related_name='usuarios',
        verbose_name='Perfil'
    )
    
    # Relação N:M com RestricaoAlimentar (através da tabela UsuarioRestricao)
    restricoes = models.ManyToManyField(
        RestricaoAlimentar,
        through='UsuarioRestricao',
        related_name='usuarios'
    )

    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.username

class AgendaAlimentar(models.Model):
    """
    Representa a agenda alimentar do usuário.
    Tabela: AGENDA_ALIMENTAR
    """
    # id é criado automaticamente
    is_google_agenda = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # FK_USUARIO_id -> Relação 1:N com USUARIO (ON DELETE CASCADE)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='agendas_alimentares'
    )

    class Meta:
        verbose_name = "Agenda Alimentar"
        verbose_name_plural = "Agendas Alimentares"

    def __str__(self):
        return f"Agenda de {self.usuario.username}"

class Dieta(models.Model):
    """
    Representa uma dieta definida para um usuário.
    Tabela: DIETA
    """
    # id é criado automaticamente
    min_refeicao = models.IntegerField()
    max_refeicao = models.IntegerField()
    total_caloria = models.IntegerField()
    link = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    # FK_USUARIO_id -> Relação 1:N com USUARIO (ON DELETE CASCADE)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='dietas'
    )
    
    # Relação N:M com Ingrediente (através da tabela IngredienteDieta)
    ingredientes_restritos = models.ManyToManyField(
        Ingrediente,
        through='IngredienteDieta',
        related_name='dietas'
    )

    class Meta:
        verbose_name = "Dieta"
        verbose_name_plural = "Dietas"

    def __str__(self):
        return f"Dieta de {self.usuario.username} ({self.total_caloria} cal)"

class Refeicao(models.Model):
    """
    Representa uma refeição registrada (ex: Café da Manhã, Almoço).
    Tabela: REFEICAO
    """
    CAFE_MANHA = 1
    ALMOCO = 2
    JANTAR = 3
    LANCHE = 4
    CEIA = 5

    TIPO_REFEICAO_CHOICES = [
        (CAFE_MANHA, 'Café da Manhã'),
        (ALMOCO, 'Almoço'),
        (JANTAR, 'Jantar'),
        (LANCHE, 'Lanche'),
        (CEIA, 'Ceia'),
    ]

    # id é criado automaticamente
    date = models.DateField()

    # utiliza Choices para tipo_refeicao
    tipo_refeicao = models.IntegerField(
        choices=TIPO_REFEICAO_CHOICES,
        help_text="Tipo da refeição (Café da Manhã, Almoço, etc.)."
    )
    
    # FK_USUARIO_id -> Relação 1:N com USUARIO (ON DELETE RESTRICT)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.RESTRICT,
        related_name='refeicoes'
    )
    
    # Relação N:M com Receita
    receitas = models.ManyToManyField(
        Receita,
        through='ReceitaRefeicao',
        related_name='refeicoes'
    )
    
    # Relação N:M com Dieta (através da tabela RefeicaoDieta)
    dietas = models.ManyToManyField(
        Dieta,
        through='RefeicaoDieta',
        related_name='refeicoes_incluidas'
    )
    
    # Relação N:M com AgendaAlimentar (através da tabela RefeicaoAgenda)
    agendas = models.ManyToManyField(
        AgendaAlimentar,
        through='RefeicaoAgenda',
        related_name='refeicoes_agendadas'
    )

    class Meta:
        verbose_name = "Refeição"
        verbose_name_plural = "Refeições"

    def __str__(self):
        return f"Refeição de {self.usuario.username} em {self.date}"

# --- Modelos de Junção (Many-to-Many com Campos Extras) ---
# Tabelas N:M explícitas

class IngredienteReceita(models.Model):
    """
    Tabela de junção entre Ingrediente e Receita.
    Tabela: INGREDIENTE_RECEITA
    """
    # id é criado automaticamente
    
    # fk_INGREDIENTE_id (ON DELETE RESTRICT)
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.RESTRICT
    )
    
    # fk_RECEITA_id (ON DELETE RESTRICT)
    receita = models.ForeignKey(
        Receita,
        on_delete=models.RESTRICT
    )
    
    # Exemplo: Você poderia adicionar um campo 'quantidade' aqui.

    class Meta:
        unique_together = ('ingrediente', 'receita')
        verbose_name = "Ingrediente em Receita"
        verbose_name_plural = "Ingredientes em Receitas"
        
    def __str__(self):
        return f"{self.ingrediente.nome} em {self.receita.titulo}"

class ReceitaRefeicao(models.Model):
    """
    Tabela de junção entre Receita e Refeicao.
    Tabela: RECEITA_REFEICAO
    """
    # Django cria o 'id' automaticamente se não for definido.

    # fk_RECEITA_id (ON DELETE SET NULL)
    receita = models.ForeignKey(
        Receita,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # fk_REFEICAO_id (ON DELETE SET NULL)
    refeicao = models.ForeignKey(
        Refeicao,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('receita', 'refeicao')
        verbose_name = "Receita em Refeição"
        verbose_name_plural = "Receitas em Refeições"

class RefeicaoDieta(models.Model):
    """
    Tabela de junção entre Refeicao e Dieta.
    Tabela: REFEICAO_DIETA
    """
    # id é criado automaticamente
    
    # fk_DIETA_id (ON DELETE SET NULL)
    dieta = models.ForeignKey(
        Dieta,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # fk_REFEICAO_id (ON DELETE SET NULL)
    refeicao = models.ForeignKey(
        Refeicao,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('dieta', 'refeicao')
        verbose_name = "Refeição em Dieta"
        verbose_name_plural = "Refeições em Dietas"

class RefeicaoAgenda(models.Model):
    """
    Tabela de junção entre Refeicao e AgendaAlimentar.
    Tabela: REFEICAO_AGENDA
    """
    # id é criado automaticamente
    
    # fk_AGENDA_ALIMENTAR_id (ON DELETE SET NULL)
    agenda_alimentar = models.ForeignKey(
        AgendaAlimentar,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # fk_REFEICAO_id (ON DELETE SET NULL)
    refeicao = models.ForeignKey(
        Refeicao,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('agenda_alimentar', 'refeicao')
        verbose_name = "Refeição em Agenda"
        verbose_name_plural = "Refeições em Agendas"

class IngredienteDieta(models.Model):
    """
    Tabela de junção entre Ingrediente e Dieta (para ingredientes restritos).
    Tabela: INGREDIENTE_DIETA
    """
    # id é criado automaticamente
    
    # fk_INGREDIENTE_id (ON DELETE RESTRICT)
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.RESTRICT
    )
    
    # fk_DIETA_id (ON DELETE SET NULL)
    dieta = models.ForeignKey(
        Dieta,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('ingrediente', 'dieta')
        verbose_name = "Ingrediente em Dieta"
        verbose_name_plural = "Ingredientes em Dietas"

class UsuarioRestricao(models.Model):
    """
    Tabela de junção entre Usuario e RestricaoAlimentar.
    Tabela: USUARIO_RESTRICAO
    """
    # id é criado automaticamente
    
    # fk_RESTRICAO_ALIMENTAR_id (ON DELETE SET NULL)
    restricao_alimentar = models.ForeignKey(
        RestricaoAlimentar,
        on_delete=models.SET_NULL,
        null=True
    )
    
    # fk_USUARIO_id (ON DELETE SET NULL)
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('restricao_alimentar', 'usuario')
        verbose_name = "Restrição de Usuário"
        verbose_name_plural = "Restrições de Usuários"

class IngredienteListaCompra(models.Model):
    """
    Tabela de junção entre Ingrediente e ListaDeCompra.
    Tabela: INGREDIENTE_LISTA_COMPRA
    """
    # Django cria o 'id' automaticamente se não for definido.

    # fk_INGREDIENTE_id (ON DELETE RESTRICT)
    ingrediente = models.ForeignKey(
        Ingrediente,
        on_delete=models.RESTRICT
    )
    
    # fk_LISTA_DE_COMPRA_id (ON DELETE SET NULL)
    lista_de_compra = models.ForeignKey(
        ListaDeCompra,
        on_delete=models.SET_NULL,
        null=True
    )

    class Meta:
        unique_together = ('ingrediente', 'lista_de_compra')
        verbose_name = "Ingrediente em Lista de Compra"
        verbose_name_plural = "Ingredientes em Listas de Compra"