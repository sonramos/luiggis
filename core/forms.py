# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Ingrediente, Receita, Usuario, Perfil, RestricaoAlimentar, Dieta, Refeicao, AgendaAlimentar, ListaDeCompra, IngredienteListaCompra
from django.contrib.auth.forms import AuthenticationForm


class IngredienteChoiceField(forms.ModelChoiceField):
    """Campo customizado que exibe a porção padrão do ingrediente."""
    def label_from_instance(self, obj):
        porcao = obj.get_porcao_display()
        return f"{obj.nome} ({porcao})"

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        # Defina os campos que o usuário poderá editar
        fields = ['nome', 'categoria', 'caloria', 'porcao_padrao_gramas', 'porcao_padrao_ml', 'restricoes'] 
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Banana Prata'}),
            'caloria': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 90 (por 100g)'}),
            'porcao_padrao_gramas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 120'}),
            'porcao_padrao_ml': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 200'}),
            'restricoes': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'porcao_padrao_gramas': 'Porção padrão (gramas)',
            'porcao_padrao_ml': 'Porção padrão (mililitros)',
            'restricoes': 'Restrições alimentares associadas',
        }

class ReceitaIAForm(forms.ModelForm):
    """
    Formulário para geração de receita via IA.
    Apenas o prompt_geracao é obrigatório; outros campos serão preenchidos pela IA.
    """
    class Meta:
        model = Receita
        fields = ['prompt_geracao']
        widgets = {
            'prompt_geracao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
            }),
        }
        labels = {
            'prompt_geracao': 'Descreva os ingredientes e o tipo de receita desejado',
        }


class ReceitaForm(forms.ModelForm):
    """Form usado para edição manual de uma receita."""
    ingredientes = forms.ModelMultipleChoiceField(
        queryset=Ingrediente.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'}),
    )
    
    class Meta:
        model = Receita
        fields = ['titulo', 'instrucoes', 'tempo_preparo', 'ingredientes']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da receita'}),
            'instrucoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customizar o campo de ingredientes para exibir porção
        self.fields['ingredientes'].queryset = Ingrediente.objects.all()
        self.fields['ingredientes'].label_from_instance = lambda obj: f"{obj.nome} ({obj.get_porcao_display()})"


class UserRegistrationForm(UserCreationForm):
    """Formulário de cadastro público para o modelo `Usuario`.

    A seleção de `perfil` foi removida do formulário público. Novos usuários
    receberão automaticamente o perfil padrão (ex: 'Usuário').
    """

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'seu@email.com'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classe Bootstrap aos campos de senha
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Authentication form that adds Bootstrap classes to widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})


class PerfilUsuarioForm(forms.ModelForm):
    """Formulário para que o usuário edite seu `perfil` e `restricoes`.

    - `perfil`: escolha de `Perfil` (FK)
    - `restricoes`: múltipla seleção de `RestricaoAlimentar` (M2M através de `UsuarioRestricao`)
    """
    restricoes = forms.ModelMultipleChoiceField(
        queryset=RestricaoAlimentar.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Restrições Alimentares'
    )

    class Meta:
        model = Usuario
        fields = ('perfil', 'restricoes')
        widgets = {
            'perfil': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mantém queryset atualizado
        self.fields['perfil'].queryset = Perfil.objects.all()


class DietaForm(forms.ModelForm):
    """Formulário para criação/edição de Dieta."""
    restricoes = forms.ModelMultipleChoiceField(
        queryset=RestricaoAlimentar.objects.filter(is_active=True),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label='Restrições Alimentares da Dieta'
    )
    
    def __init__(self, *args, user=None, **kwargs):
        """Inicializa o formulário pré-preenchendo restrições do perfil do usuário."""
        super().__init__(*args, **kwargs)
        
        if user:
            # Obter restrições do perfil do usuário
            restricoes_perfil = user.perfil.restricoes.filter(is_active=True)
            
            # Pré-preencher as restrições do perfil
            if restricoes_perfil.exists():
                self.fields['restricoes'].initial = restricoes_perfil
                
                # Armazenar as restrições obrigatórias para uso no clean()
                self.restricoes_obrigatorias = set(restricoes_perfil.values_list('id', flat=True))
            else:
                self.restricoes_obrigatorias = set()
        else:
            self.restricoes_obrigatorias = set()
    
    def clean(self):
        """Validação customizada - garante que restrições obrigatórias estejam selecionadas."""
        cleaned_data = super().clean()
        restricoes_selecionadas = cleaned_data.get('restricoes')
        
        if restricoes_selecionadas:
            ids_selecionados = set(r.id for r in restricoes_selecionadas)
            # Verificar se todas as restrições obrigatórias foram mantidas
            if not self.restricoes_obrigatorias.issubset(ids_selecionados):
                raise forms.ValidationError(
                    'Você deve manter as restrições alimentares do seu perfil selecionadas.'
                )
        elif self.restricoes_obrigatorias:
            # Se há restrições obrigatórias mas nenhuma foi selecionada
            raise forms.ValidationError(
                'Você deve manter as restrições alimentares do seu perfil selecionadas.'
            )
        
        return cleaned_data
    
    class Meta:
        model = Dieta
        fields = ['min_refeicao', 'max_refeicao', 'total_caloria', 'link', 'restricoes']
        widgets = {
            'min_refeicao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 3'}),
            'max_refeicao': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 5'}),
            'total_caloria': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 2000'}),
            'link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }
        labels = {
            'min_refeicao': 'Número mínimo de refeições por dia',
            'max_refeicao': 'Número máximo de refeições por dia',
            'total_caloria': 'Total de calorias por dia',
            'link': 'Link ou referência (opcional)',
        }


class RefeicaoForm(forms.ModelForm):
    """Formulário para criação/edição de Refeição."""
    receitas = forms.ModelMultipleChoiceField(
        queryset=Receita.objects.all(),
        required=True,
        widget=forms.CheckboxSelectMultiple(),
        label='Receitas',
        error_messages={
            'required': 'Selecione pelo menos uma receita para a refeição.'
        }
    )
    
    def __init__(self, *args, user=None, **kwargs):
        """Inicializa o formulário filtrando receitas do usuário."""
        super().__init__(*args, **kwargs)
        if user:
            # Filtrar apenas receitas do usuário logado
            self.fields['receitas'].queryset = Receita.objects.filter(owner=user)
        else:
            self.fields['receitas'].queryset = Receita.objects.none()
    
    class Meta:
        model = Refeicao
        fields = ['date', 'tipo_refeicao', 'receitas']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'tipo_refeicao': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'date': 'Data da refeição',
            'tipo_refeicao': 'Tipo de refeição',
            'receitas': 'Receitas incluídas',
        }


class AgendaAlimentarForm(forms.ModelForm):
    """Formulário para criação/edição de Agenda Alimentar."""
    class Meta:
        model = AgendaAlimentar
        fields = ['is_google_agenda']
        widgets = {
            'is_google_agenda': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_google_agenda': 'Sincronizar com Google Calendar (experimental)',
        }


class ListaDeCompraForm(forms.ModelForm):
    """Formulário para criação de Lista de Compra."""
    ingredientes = forms.ModelMultipleChoiceField(
        queryset=Ingrediente.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        label='Ingredientes'
    )
    
    class Meta:
        model = ListaDeCompra
        fields = ['is_active']
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_active': 'Lista ativa',
        }


class IngredienteListaCompraForm(forms.ModelForm):
    """Formulário para adicionar ingredientes com quantidade em uma lista de compra."""
    class Meta:
        model = IngredienteListaCompra
        fields = ['ingrediente', 'quantidade_gramas', 'quantidade_ml']
        widgets = {
            'ingrediente': forms.Select(attrs={'class': 'form-select'}),
            'quantidade_gramas': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 200'}),
            'quantidade_ml': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 500'}),
        }
        labels = {
            'ingrediente': 'Ingrediente',
            'quantidade_gramas': 'Quantidade (gramas)',
            'quantidade_ml': 'Quantidade (mililitros)',
        }