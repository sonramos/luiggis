# core/forms.py
from django import forms
from .models import Ingrediente

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