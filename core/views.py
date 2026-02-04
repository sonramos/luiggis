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
from .models import Ingrediente, Categoria, Receita, Usuario, Perfil, IngredienteReceita # Importe os Models
from .forms import IngredienteForm, ReceitaIAForm, PerfilUsuarioForm, ReceitaForm # Importe os Forms
from .forms import UserRegistrationForm
from django.contrib.auth import login
from django.views.generic import FormView
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from google import genai 
import os

# --- Landing Page ---

class LandingPageView(TemplateView):
    """Exibe a página inicial/landing page do aplicativo."""
    template_name = 'core/landing.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passa estatísticas para a landing page
        context['total_ingredientes'] = Ingrediente.objects.count()
        context['total_receitas'] = Receita.objects.count()
        context['total_receitas_ia'] = Receita.objects.filter(is_ai_generated=True).count()
        return context


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

# AUTORIZACAO: exige login para criar ingredientes
class IngredienteCreateView(LoginRequiredMixin, CreateView):
    """ Permite adicionar um novo ingrediente (exige login). """
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'core/ingrediente_form.html'
    success_url = reverse_lazy('lista_ingredientes') # Redireciona para a lista após o sucesso

# AUTORIZACAO: exige login para editar ingredientes
class IngredienteUpdateView(LoginRequiredMixin, UpdateView):
    """ Permite editar um ingrediente existente (exige login). """
    model = Ingrediente
    form_class = IngredienteForm
    template_name = 'core/ingrediente_form.html'
    success_url = reverse_lazy('lista_ingredientes')

# AUTORIZACAO: exige login para excluir ingredientes
class IngredienteDeleteView(LoginRequiredMixin, DeleteView):
    """ Permite excluir um ingrediente (exige login). """
    model = Ingrediente
    template_name = 'core/ingrediente_confirmar_delete.html'
    context_object_name = 'ingrediente'
    success_url = reverse_lazy('lista_ingredientes')


# --- Vistas para Receita ---

# AUTORIZACAO: lista apenas receitas do usuário logado (requere autenticação)
class ReceitaListView(ListView):
    """ Exibe a lista de receitas do usuário logado (minhas receitas). """
    model = Receita
    template_name = 'core/receita_lista.html'
    context_object_name = 'receitas'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Receita.objects.filter(owner=user).order_by('-id')
        return Receita.objects.none()  # não exibe receitas para anonimos


# AUTORIZACAO: Somente owner ou superuser pode editar/excluir o objeto (aplica a Receitas)
class OwnerRequiredMixin:
    """Mixin simples que verifica se o usuário requisitante é o dono do objeto."""
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        # Se não há owner, apenas superuser pode administrar
        if obj.owner is None:
            if not user.is_superuser:
                raise PermissionDenied
        # Se há owner, apenas o owner (ou superuser) pode administrar
        elif obj.owner != user and not user.is_superuser:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


# --- Vistas para Receita ---

class ReceitaDetailView(DetailView):
    """ Exibe os detalhes de uma receita gerada. """
    model = Receita
    template_name = 'core/receita_detalhe.html'
    context_object_name = 'receita'


# AUTORIZACAO: exige login para gerar receita via IA e atribui owner ao criar
class GerarReceitaIAView(LoginRequiredMixin, CreateView):
    """
    Exibe o formulário de prompt e processa a geração da receita via IA.
    """
    model = Receita
    form_class = ReceitaIAForm
    template_name = 'core/receita_geracao_ia.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Passamos a lista de ingredientes disponíveis para o template, 
        # caso queira dar opções para o prompt.
        context['ingredientes_disponiveis'] = list(Ingrediente.objects.values_list('nome', flat=True))
        return context

    def form_valid(self, form):
        ingredientes_ids = self.request.POST.getlist('ingredientes_ids')
        prompt = form.instance.prompt_geracao
        
        # 1. Configurar o Cliente IA
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # Em um projeto real, você faria um tratamento de erro melhor
            raise EnvironmentError("GEMINI_API_KEY não configurada no ambiente.")
            
        try:
            client = genai.Client(api_key=api_key)

            # 2. Formular o Prompt para a IA
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

            # 3. Processar e Salvar o Resultado
            import json
            receita_data = json.loads(response.text)
            
            # Atualiza a instância do formulário com os dados da IA
            form.instance.titulo = receita_data.get('titulo', 'Receita Gerada')
            form.instance.instrucoes = receita_data.get('instrucoes', 'Instruções não geradas.')
            form.instance.tempo_preparo = receita_data.get('tempo_preparo', 20)
            form.instance.is_ai_generated = True
            # Atribui o owner como o usuário logado
            form.instance.owner = self.request.user

            # Salva o Model Receita
            response = super().form_valid(form)

            # 4. Cria os relacionamentos na tabela IngredienteReceita
            if self.object and ingredientes_ids:
                objetos_relacionamento = []
                for ing_id in ingredientes_ids:
                    try:
                        ingrediente = Ingrediente.objects.get(id=ing_id)
                        objetos_relacionamento.append(
                            IngredienteReceita(
                                receita=self.object,
                                ingrediente=ingrediente,
                                quantidade=0, # Ou algum valor padrão, já que a IA gera o texto
                                unidade_medida='un' # Ajuste conforme seu model
                            )
                        )
                    except Ingrediente.DoesNotExist:
                        continue
                
                # Salva todos de uma vez (mais performático)
                IngredienteReceita.objects.bulk_create(objetos_relacionamento)

            return response

        except Exception as e:
            form.add_error(None, f"Erro ao gerar receita com IA: {e}")
            return self.form_invalid(form)

    def get_success_url(self):
        """Redireciona para a página da receita criada para exibir o resultado."""
        return reverse_lazy('detalhes_receita', kwargs={'pk': self.object.pk})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Buscamos todos os ingredientes ordenados por categoria para o agrupamento funcionar
        context['ingredientes_por_categoria'] = Ingrediente.objects.select_related('categoria').all().order_by('categoria__nome', 'nome')
        return context


# AUTORIZACAO: apenas owner ou superuser pode editar esta receita
class ReceitaUpdateView(LoginRequiredMixin, OwnerRequiredMixin, UpdateView):
    """Permite que o dono (ou superuser) edite uma receita."""
    model = Receita
    form_class = ReceitaForm
    template_name = 'core/receita_form.html'
    success_url = reverse_lazy('lista_receitas')


# AUTORIZACAO: apenas owner ou superuser pode excluir esta receita
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
        # Não permitimos escolha de `perfil` no cadastro público.
        # Atribuímos o perfil padrão 'Usuário' automaticamente.
        user = form.save(commit=False)
        try:
            perfil_default = Perfil.objects.get(tipo__iexact='usuario')
        except Perfil.DoesNotExist:
            perfil_default = Perfil.objects.first()

        if perfil_default:
            user.perfil = perfil_default

        user.save()
        # Autentica e faz login automático
        login(self.request, user)
        return super().form_valid(form)


# AUTORIZACAO: requer login para exibir perfil do usuário autenticado
class PerfilDetailView(LoginRequiredMixin, TemplateView):
    """Exibe os dados de perfil do usuário logado."""
    template_name = 'core/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['user'] = user
        # inclui restrições e perfil
        context['restricoes'] = user.restricoes.all()
        context['perfil'] = user.perfil
        return context


# AUTORIZACAO: requer login para editar perfil (aplicação de autorização no perfil próprio)
class PerfilUpdateView(LoginRequiredMixin, UpdateView):
    """Permite que o usuário edite seu `perfil` e `restricoes`."""
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
    """Faz logout do usuário e redireciona para a landing.

    Aceita GET e POST para facilitar uso a partir de um link simples na navbar.
    """
    logout(request)
    return redirect('landing')