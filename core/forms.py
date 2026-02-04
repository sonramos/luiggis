# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Ingrediente, Receita, Usuario, Perfil, RestricaoAlimentar
from django.contrib.auth.forms import AuthenticationForm

class IngredienteForm(forms.ModelForm):
    class Meta:
        model = Ingrediente
        # Defina os campos que o usuário poderá editar
        fields = ['nome', 'categoria', 'caloria'] 
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Banana Prata'}),
            # O campo categoria usará automaticamente um select box com as Categorias cadastradas
            'caloria': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 90 (por 100g)'}),
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
    class Meta:
        model = Receita
        fields = ['titulo', 'instrucoes', 'tempo_preparo', 'ingredientes']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título da receita'}),
            'instrucoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'tempo_preparo': forms.NumberInput(attrs={'class': 'form-control'}),
            'ingredientes': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


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