# core/serializers.py
from rest_framework import serializers
from .models import (
    Perfil, RestricaoAlimentar, Categoria, Ingrediente, Receita,
    ListaDeCompra, Usuario, AgendaAlimentar, Dieta, Refeicao
)


class PerfilSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Perfil."""
    class Meta:
        model = Perfil
        fields = ['id', 'tipo']
        read_only_fields = ['id']


class RestricaoAlimentarSerializer(serializers.ModelSerializer):
    """Serializer para o modelo RestricaoAlimentar."""
    class Meta:
        model = RestricaoAlimentar
        fields = ['id', 'tipo', 'descricao', 'is_active']
        read_only_fields = ['id']


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Categoria."""
    ingredientes_count = serializers.IntegerField(
        source='ingredientes.count',
        read_only=True
    )
    
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'descricao', 'ingredientes_count']
        read_only_fields = ['id']


class IngredienteSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Ingrediente."""
    categoria_nome = serializers.CharField(
        source='categoria.nome',
        read_only=True
    )
    
    class Meta:
        model = Ingrediente
        fields = ['id', 'nome', 'categoria', 'categoria_nome', 'caloria']
        read_only_fields = ['id']


class IngredienteDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para Ingrediente com informações da categoria."""
    categoria = CategoriaSerializer(read_only=True)
    receitas_count = serializers.IntegerField(
        source='receitas.count',
        read_only=True
    )
    
    class Meta:
        model = Ingrediente
        fields = ['id', 'nome', 'categoria', 'caloria', 'receitas_count']
        read_only_fields = ['id']


class ReceitaSerializer(serializers.ModelSerializer):
    """Serializer básico para o modelo Receita."""
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True
    )
    ingredientes_count = serializers.IntegerField(
        source='ingredientes.count',
        read_only=True
    )
    
    class Meta:
        model = Receita
        fields = [
            'id', 'titulo', 'instrucoes', 'tempo_preparo',
            'prompt_geracao', 'is_ai_generated', 'owner',
            'owner_username', 'ingredientes_count'
        ]
        read_only_fields = ['id', 'owner', 'is_ai_generated']
    
    def create(self, validated_data):
        # Atribui o usuário logado como owner
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class ReceitaDetailSerializer(serializers.ModelSerializer):
    """Serializer detalhado para Receita com ingredientes."""
    owner_username = serializers.CharField(
        source='owner.username',
        read_only=True
    )
    ingredientes = IngredienteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Receita
        fields = [
            'id', 'titulo', 'instrucoes', 'tempo_preparo',
            'prompt_geracao', 'is_ai_generated', 'owner',
            'owner_username', 'ingredientes'
        ]
        read_only_fields = ['id', 'owner', 'is_ai_generated']


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Usuario."""
    perfil_tipo = serializers.CharField(
        source='perfil.tipo',
        read_only=True
    )
    restricoes = RestricaoAlimentarSerializer(many=True, read_only=True)
    receitas_count = serializers.IntegerField(
        source='receitas.count',
        read_only=True
    )
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'perfil', 'perfil_tipo', 'restricoes', 'receitas_count',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined', 'receitas_count']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de usuários via API."""
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, required=True, label='Confirmar Senha', style={'input_type': 'password'})
    
    class Meta:
        model = Usuario
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'password', 'password2', 'perfil'
        ]
        read_only_fields = ['id']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "As senhas não correspondem."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')
        
        # Define perfil padrão se não fornecido
        if 'perfil' not in validated_data or validated_data['perfil'] is None:
            try:
                perfil_default = Perfil.objects.get(tipo__iexact='usuario')
                validated_data['perfil'] = perfil_default
            except Perfil.DoesNotExist:
                perfil_default = Perfil.objects.first()
                if perfil_default:
                    validated_data['perfil'] = perfil_default
        
        user = Usuario.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ListaDeCompraSerializer(serializers.ModelSerializer):
    """Serializer para o modelo ListaDeCompra."""
    ingredientes = IngredienteSerializer(many=True, read_only=True)
    ingredientes_count = serializers.IntegerField(
        source='ingredientes.count',
        read_only=True
    )
    
    class Meta:
        model = ListaDeCompra
        fields = ['id', 'data_criacao', 'is_active', 'ingredientes', 'ingredientes_count']
        read_only_fields = ['id', 'data_criacao']


class AgendaAlimentarSerializer(serializers.ModelSerializer):
    """Serializer para o modelo AgendaAlimentar."""
    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True
    )
    
    class Meta:
        model = AgendaAlimentar
        fields = ['id', 'is_google_agenda', 'is_active', 'usuario', 'usuario_username']
        read_only_fields = ['id']


class DietaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Dieta."""
    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True
    )
    ingredientes_restritos = IngredienteSerializer(many=True, read_only=True)
    
    class Meta:
        model = Dieta
        fields = [
            'id', 'min_refeicao', 'max_refeicao', 'total_caloria',
            'link', 'is_active', 'usuario', 'usuario_username',
            'ingredientes_restritos'
        ]
        read_only_fields = ['id']


class RefeicaoSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Refeicao."""
    usuario_username = serializers.CharField(
        source='usuario.username',
        read_only=True
    )
    tipo_refeicao_display = serializers.CharField(
        source='get_tipo_refeicao_display',
        read_only=True
    )
    receitas = ReceitaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Refeicao
        fields = [
            'id', 'date', 'tipo_refeicao', 'tipo_refeicao_display',
            'usuario', 'usuario_username', 'receitas'
        ]
        read_only_fields = ['id']
