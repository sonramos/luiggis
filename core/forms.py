# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Ingrediente, Receita, Usuario, Perfil
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


class UserRegistrationForm(UserCreationForm):
    """Formulário de cadastro para o modelo `Usuario` incluindo seleção de `Perfil`."""
    perfil = forms.ModelChoiceField(queryset=Perfil.objects.all(), required=True, label='Tipo de perfil')

    class Meta:
        model = Usuario
        fields = ('username', 'email', 'perfil', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        user.perfil = self.cleaned_data.get('perfil')
        if commit:
            user.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Authentication form that adds Bootstrap classes to widgets."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password'].widget.attrs.update({'class': 'form-control'})