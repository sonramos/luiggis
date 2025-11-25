from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView, 
    CreateView, 
    UpdateView, 
    DeleteView
)
from .models import Ingrediente, Categoria # Importe os Models
from .forms import IngredienteForm # Importe o Form


# --- Vistas para Categoria (Opcional) ---

class CategoriaListView(ListView):
    model = Categoria
    template_name = 'core/categoria_lista.html'
    context_object_name = 'categorias'


# --- Vistas para Ingrediente (CRUD) ---

class IngredienteListView(ListView):
    """ Exibe a lista de todos os ingredientes. """
    model = Ingrediente
    template_name = 'core/ingrediente_lista.html'
    context_object_name = 'ingredientes' # Nome que será usado no template

class IngredienteCreateView(CreateView):
    """ Permite adicionar um novo ingrediente. """
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'core/ingrediente_form.html'
    success_url = reverse_lazy('lista_ingredientes') # Redireciona para a lista após o sucesso

class IngredienteUpdateView(UpdateView):
    """ Permite editar um ingrediente existente. """
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'core/ingrediente_form.html'
    success_url = reverse_lazy('lista_ingredientes')

class IngredienteDeleteView(DeleteView):
    """ Permite excluir um ingrediente. """
    model = Ingrediente
    template_name = 'core/ingrediente_confirmar_delete.html'
    context_object_name = 'ingrediente'
    success_url = reverse_lazy('lista_ingredientes')