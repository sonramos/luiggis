# core/forms.py
from django import forms
from .models import Ingrediente, Receita

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