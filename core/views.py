from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView, 
    DetailView,
    CreateView, 
    UpdateView, 
    DeleteView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Ingrediente, Categoria, Receita, Usuario, Perfil
from .forms import IngredienteForm, ReceitaIAForm, PerfilUsuarioForm, ReceitaForm
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from google import genai 
import os
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# --- Landing Page ---

class LandingPageView(TemplateView):
    """Exibe a página inicial/landing page do aplicativo."""
    template_name = 'core/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_ingredientes'] = Ingrediente.objects.count()
        context['total_receitas'] = Receita.objects.count()
        context['total_receitas_ia'] = Receita.objects.filter(is_ai_generated=True).count()
        return context


# --- Vistas para Categoria ---

class CategoriaListView(TemplateView):
    template_name = 'core/categoria_lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        categorias_list = Categoria.objects.all().order_by('nome')
        page = self.request.GET.get('page', 1)
        paginator = Paginator(categorias_list, 9)  # 12 categorias por página
        
        try:
            categorias = paginator.page(page)
        except PageNotAnInteger:
            categorias = paginator.page(1)
        except EmptyPage:
            categorias = paginator.page(paginator.num_pages)
        
        context['categorias'] = categorias
        return context


# --- Vistas para Ingrediente (CRUD) ---

class IngredienteListView(TemplateView):
    """Exibe a lista de todos os ingredientes com paginação manual."""
    template_name = 'core/ingrediente_lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        ingredientes_list = Ingrediente.objects.all().order_by('nome')
        page = self.request.GET.get('page', 1)
        paginator = Paginator(ingredientes_list, 12)  # 12 ingredientes por página
        
        try:
            ingredientes = paginator.page(page)
        except PageNotAnInteger:
            ingredientes = paginator.page(1)
        except EmptyPage:
            ingredientes = paginator.page(paginator.num_pages)
        
        context['ingredientes'] = ingredientes
        return context


class IngredienteCreateView(LoginRequiredMixin, CreateView):
    """Permite adicionar um novo ingrediente (exige login)."""
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'core/ingrediente_form.html'
    success_url = reverse_lazy('lista_ingredientes')
    

class IngredienteUpdateView(LoginRequiredMixin, UpdateView):
    """Permite editar um ingrediente existente (exige login)."""
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'core/ingrediente_form.html'
    success_url = reverse_lazy('lista_ingredientes')


class IngredienteDeleteView(LoginRequiredMixin, DeleteView):
    """Permite excluir um ingrediente (exige login)."""
    model = Ingrediente
    template_name = 'core/ingrediente_confirmar_delete.html'
    context_object_name = 'ingrediente'
    success_url = reverse_lazy('lista_ingredientes')


# --- Vistas para Receita ---

class ReceitaListView(LoginRequiredMixin, TemplateView):
    """Exibe a lista de receitas do usuário logado com paginação manual."""
    template_name = 'core/receita_lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        if user.is_authenticated:
            receitas_list = Receita.objects.filter(owner=user).order_by('-id')
        else:
            receitas_list = Receita.objects.none()
        
        page = self.request.GET.get('page', 1)
        paginator = Paginator(receitas_list, 9)  # 9 receitas por página
        
        try:
            receitas = paginator.page(page)
        except PageNotAnInteger:
            receitas = paginator.page(1)
        except EmptyPage:
            receitas = paginator.page(paginator.num_pages)
        
        context['receitas'] = receitas
        return context


class OwnerRequiredMixin:
    """Mixin simples que verifica se o usuário requisitante é o dono do objeto."""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        if obj.owner is None:
            if not user.is_superuser:
                raise PermissionDenied
        elif obj.owner != user and not user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ReceitaDetailView(DetailView):
    """Exibe os detalhes de uma receita gerada."""
    model = Receita
    template_name = 'core/receita_detalhe.html'
    context_object_name = 'receita'


class GerarReceitaIAView(LoginRequiredMixin, CreateView):
    """Exibe o formulário de prompt e processa a geração da receita via IA."""
    model = Receita
    form_class = ReceitaIAForm
    template_name = 'core/receita_geracao_ia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredientes_disponiveis'] = list(Ingrediente.objects.values_list('nome', flat=True))
        return context

    def form_valid(self, form):
        prompt = form.instance.prompt_geracao
        
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY não configurada no ambiente.")
            
        try:
            client = genai.Client(api_key=api_key)

            system_instruction = (
                "Você é um chef IA. Dada a lista de ingredientes e restrições do usuário, "
                "gere uma receita completa. O resultado deve ser em JSON no formato: "
                '{"titulo": "Nome da Receita", "instrucoes": "Passos...", "tempo_preparo": 30}'
            )

            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                )
            )

            import json
            receita_data = json.loads(response.text)
            
            form.instance.titulo = receita_data.get('titulo', 'Receita Gerada')
            form.instance.instrucoes = receita_data.get('instrucoes', 'Instruções não geradas.')
            form.instance.tempo_preparo = receita_data.get('tempo_preparo', 20)
            form.instance.is_ai_generated = True
            form.instance.owner = self.request.user

            return super().form_valid(form)

        except Exception as e:
            form.add_error(None, f"Erro ao gerar receita com IA: {e}")
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('detalhes_receita', kwargs={'pk': self.object.pk})


class ReceitaUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Permite que o dono (ou superuser) edite uma receita."""
    model = Receita
    form_class = ReceitaForm
    template_name = 'core/receita_form.html'
    success_url = reverse_lazy('lista_receitas')


class ReceitaDeleteView(LoginRequiredMixin, OwnerRequiredMixin, DeleteView):
    """Permite que o dono (ou superuser) exclua uma receita."""
    model = Receita
    template_name = 'core/receita_confirmar_delete.html'
    context_object_name = 'receita'
    success_url = reverse_lazy('lista_receitas')


class RegisterView(FormView):
    """Página de cadastro de usuário."""
    template_name = 'core/register.html'
    form_class = UserRegistrationForm
    success_url = reverse_lazy('landing')

    def form_valid(self, form):
        user = form.save(commit=False)
        try:
            perfil_default = Perfil.objects.get(tipo__iexact='usuario')
        except Perfil.DoesNotExist:
            perfil_default = Perfil.objects.first()

        if perfil_default:
            user.perfil = perfil_default

        user.save()
        login(self.request, user)
        return super().form_valid(form)


class PerfilDetailView(LoginRequiredMixin, TemplateView):
    """Exibe os dados de perfil do usuário logado."""
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        context['restricoes'] = user.restricoes.all()
        context['perfil'] = user.perfil
        return context


class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    """Permite que o usuário edite seu perfil e restricoes."""
    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = 'core/profile_form.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('perfil')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Perfil atualizado com sucesso.')
        return response


def logout_view(request):
    """Faz logout do usuário e redireciona para a landing."""
    logout(request)
    return redirect('landing')