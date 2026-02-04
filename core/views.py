from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    TemplateView,
    ListView, 
    DetailView,
    CreateView, 
    UpdateView, 
    DeleteView,
    View
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Ingrediente, Categoria, Receita, Usuario, Perfil, IngredienteReceita, Dieta, Refeicao, AgendaAlimentar, ListaDeCompra, IngredienteListaCompra # Importe os Models
from .forms import IngredienteForm, ReceitaIAForm, PerfilUsuarioForm, ReceitaForm, DietaForm, RefeicaoForm, AgendaAlimentarForm, ListaDeCompraForm, IngredienteListaCompraForm # Importe os Forms
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
        
        # Verificar se uma dieta foi passada como parâmetro
        dieta_id = self.request.GET.get('dieta')
        context['dieta_id'] = dieta_id
        
        if dieta_id:
            try:
                dieta = Dieta.objects.get(id=dieta_id, usuario=self.request.user)
                # Obter apenas ingredientes permitidos pela dieta
                context['ingredientes_disponiveis'] = list(
                    dieta.get_ingredientes_permitidos().values_list('nome', flat=True)
                )
                context['ingredientes_por_categoria'] = dieta.get_ingredientes_permitidos().select_related('categoria').order_by('categoria__nome', 'nome')
                context['dieta'] = dieta
            except Dieta.DoesNotExist:
                # Fallback para todos os ingredientes se dieta não existe
                context['ingredientes_disponiveis'] = list(Ingrediente.objects.values_list('nome', flat=True))
                context['ingredientes_por_categoria'] = Ingrediente.objects.select_related('categoria').order_by('categoria__nome', 'nome')
        else:
            # Sem dieta especificada, mostrar todos os ingredientes
            context['ingredientes_disponiveis'] = list(Ingrediente.objects.values_list('nome', flat=True))
            context['ingredientes_por_categoria'] = Ingrediente.objects.select_related('categoria').order_by('categoria__nome', 'nome')
        
        return context

    def form_valid(self, form):
        ingredientes_ids = self.request.POST.getlist('ingredientes_ids')
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


# --- Vistas para Dieta ---

class DietaListView(LoginRequiredMixin, ListView):
    """Lista todas as dietas do usuário logado."""
    model = Dieta
    template_name = 'core/dieta_lista.html'
    context_object_name = 'dietas'
    paginate_by = 10
    
    def get_queryset(self):
        return Dieta.objects.filter(usuario=self.request.user).order_by('-id')


class DietaCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova dieta."""
    model = Dieta
    form_class = DietaForm
    template_name = 'core/dieta_form.html'
    
    def get_form_kwargs(self):
        """Passa o usuário ao formulário."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Dieta criada com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('listar_dietas')


class DietaUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma dieta existente."""
    model = Dieta
    form_class = DietaForm
    template_name = 'core/dieta_form.html'
    
    def get_queryset(self):
        return Dieta.objects.filter(usuario=self.request.user)
    
    def get_form_kwargs(self):
        """Passa o usuário ao formulário."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Dieta atualizada com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('listar_dietas')
class DietaDeleteView(LoginRequiredMixin, DeleteView):
    """Deleta uma dieta."""
    model = Dieta
    template_name = 'core/dieta_confirmar_delete.html'
    
    def get_queryset(self):
        return Dieta.objects.filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Dieta removida com sucesso.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('listar_dietas')


# --- Vistas para Refeição ---

class RefeicaoListView(LoginRequiredMixin, TemplateView):
    """Lista todas as refeições do usuário logado com paginação manual."""
    template_name = 'core/refeicao_lista.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        refeicoes_list = Refeicao.objects.filter(usuario=user).order_by('-date', '-id')
        page = self.request.GET.get('page', 1)
        paginator = Paginator(refeicoes_list, 10)  # 10 refeições por página
        
        try:
            refeicoes = paginator.page(page)
        except PageNotAnInteger:
            refeicoes = paginator.page(1)
        except EmptyPage:
            refeicoes = paginator.page(paginator.num_pages)
        
        context['refeicoes'] = refeicoes
        return context


class RefeicaoCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova refeição."""
    model = Refeicao
    form_class = RefeicaoForm
    template_name = 'core/refeicao_form.html'
    
    def get_form_kwargs(self):
        """Passa o usuário ao formulário para filtrar receitas."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Refeição criada com sucesso.')
        return super().form_valid(form)
    
    def get_initial(self):
        """Pré-preenche a data se passada como parâmetro na URL."""
        initial = super().get_initial()
        data_param = self.request.GET.get('data')
        if data_param:
            initial['date'] = data_param
        return initial
    
    def get_success_url(self):
        # Se veio de uma agenda, volta para lá
        agenda_id = self.request.GET.get('agenda_id')
        if agenda_id:
            return reverse_lazy('agenda_semanal', kwargs={'pk': agenda_id})
        return reverse_lazy('listar_refeicoes')


class RefeicaoSelecionarOuCriarView(LoginRequiredMixin, TemplateView):
    """View que permite selecionar uma refeição existente ou criar uma nova para uma agenda e dia específicos."""
    template_name = 'core/refeicao_selecionar_ou_criar.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário tem acesso à agenda."""
        self.agenda_pk = kwargs.get('agenda_pk')
        self.day_num = kwargs.get('day_num')
        try:
            self.agenda = AgendaAlimentar.objects.get(pk=self.agenda_pk, usuario=request.user)
        except AgendaAlimentar.DoesNotExist:
            messages.error(request, 'Agenda não encontrada.')
            return redirect('listar_agendas')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Passa refeições do usuário e formulário para o contexto."""
        from datetime import datetime, timedelta
        context = super().get_context_data(**kwargs)
        context['agenda'] = self.agenda
        context['agenda_pk'] = self.agenda_pk
        context['day_num'] = self.day_num
        
        DIAS_SEMANA = {
            0: 'Domingo',
            1: 'Segunda',
            2: 'Terça',
            3: 'Quarta',
            4: 'Quinta',
            5: 'Sexta',
            6: 'Sábado'
        }
        context['dia_selecionado'] = DIAS_SEMANA.get(self.day_num, 'Desconhecido')
        
        # Refeições existentes do usuário
        context['refeicoes_usuario'] = Refeicao.objects.filter(usuario=self.request.user).order_by('-date')
        
        # Calcular a data do dia selecionado
        today = datetime.now().date()
        sunday = today - timedelta(days=today.weekday() + 1)
        selected_date = sunday + timedelta(days=self.day_num)
        
        # Formulário para criar nova refeição com data inicial
        context['form'] = RefeicaoForm(user=self.request.user, initial={'date': selected_date})
        context['receitas_disponiveis'] = Receita.objects.filter(owner=self.request.user).exists()
        
        return context


class RefeicaoAdicionarExistenteView(LoginRequiredMixin, View):
    """View para adicionar uma refeição já existente a uma agenda em um dia específico."""
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário tem acesso à agenda e à refeição."""
        self.agenda_pk = kwargs.get('agenda_pk')
        self.day_num = kwargs.get('day_num')
        self.refeicao_pk = kwargs.get('refeicao_pk')
        
        try:
            self.agenda = AgendaAlimentar.objects.get(pk=self.agenda_pk, usuario=request.user)
            self.refeicao = Refeicao.objects.get(pk=self.refeicao_pk, usuario=request.user)
        except (AgendaAlimentar.DoesNotExist, Refeicao.DoesNotExist):
            messages.error(request, 'Agenda ou refeição não encontrada.')
            return redirect('listar_agendas')
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
        """Associa a refeição à agenda, copiando-a para o dia específico."""
        from .models import RefeicaoAgenda
        from datetime import datetime, timedelta
        
        # Calcular a data do dia selecionado
        today = datetime.now().date()
        sunday = today - timedelta(days=today.weekday() + 1)
        selected_date = sunday + timedelta(days=self.day_num)
        
        # Criar uma cópia da refeição com a nova data
        refeicao_copia = Refeicao.objects.create(
            usuario=self.refeicao.usuario,
            date=selected_date,
            tipo_refeicao=self.refeicao.tipo_refeicao
        )
        
        # Copiar receitas da refeição original
        refeicao_copia.receitas.set(self.refeicao.receitas.all())
        
        # Associar à agenda
        RefeicaoAgenda.objects.create(
            agenda_alimentar=self.agenda,
            refeicao=refeicao_copia
        )
        
        messages.success(request, 'Refeição adicionada à agenda com sucesso!')
        return redirect('agenda_semanal', pk=self.agenda_pk)


class RefeicaoCreateAgendaDiaView(LoginRequiredMixin, CreateView):
    """Cria uma nova refeição e a associa a um dia específico de uma agenda."""
    model = Refeicao
    form_class = RefeicaoForm
    template_name = 'core/refeicao_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Verifica se o usuário tem acesso à agenda."""
        self.agenda_pk = kwargs.get('agenda_pk')
        self.day_num = kwargs.get('day_num')
        try:
            self.agenda = AgendaAlimentar.objects.get(pk=self.agenda_pk, usuario=request.user)
        except AgendaAlimentar.DoesNotExist:
            messages.error(request, 'Agenda não encontrada.')
            return redirect('listar_agendas')
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        """Passa o usuário ao formulário para filtrar receitas e pré-preenche a data."""
        from datetime import datetime, timedelta
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        
        # Calcular a data do dia selecionado (baseado na semana atual)
        today = datetime.now().date()
        # Encontrar o domingo desta semana
        sunday = today - timedelta(days=today.weekday() + 1)
        # Adicionar o dia selecionado
        selected_date = sunday + timedelta(days=self.day_num)
        
        # Pré-preencher a data no formulário
        if 'data' not in kwargs:
            kwargs['data'] = {}
        kwargs['initial'] = {'date': selected_date}
        
        return kwargs
    
    def form_valid(self, form):
        """Salva a refeição e associa à agenda no dia específico."""
        form.instance.usuario = self.request.user
        response = super().form_valid(form)
        
        # Associa a refeição à agenda via RefeicaoAgenda
        from .models import RefeicaoAgenda
        RefeicaoAgenda.objects.create(
            agenda_alimentar=self.agenda,
            refeicao=self.object
        )
        
        messages.success(self.request, 'Refeição criada e adicionada à agenda com sucesso.')
        return response
    
    def get_context_data(self, **kwargs):
        """Passa a agenda e dia para o contexto."""
        context = super().get_context_data(**kwargs)
        context['agenda_id'] = self.agenda_pk
        context['day_num'] = self.day_num
        DIAS_SEMANA = {
            0: 'Domingo',
            1: 'Segunda',
            2: 'Terça',
            3: 'Quarta',
            4: 'Quinta',
            5: 'Sexta',
            6: 'Sábado'
        }
        context['dia_selecionado'] = DIAS_SEMANA.get(self.day_num, 'Desconhecido')
        return context
    
    def get_success_url(self):
        return reverse_lazy('agenda_semanal', kwargs={'pk': self.agenda_pk})


class RefeicaoUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma refeição existente."""
    model = Refeicao
    form_class = RefeicaoForm
    template_name = 'core/refeicao_form.html'
    
    def get_queryset(self):
        return Refeicao.objects.filter(usuario=self.request.user)
    
    def get_form_kwargs(self):
        """Passa o usuário ao formulário para filtrar receitas."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        """Passa o tipo de refeição para o template."""
        context = super().get_context_data(**kwargs)
        if self.object:
            # Pega o display do tipo de refeição
            context['tipo_refeicao_display'] = self.object.get_tipo_refeicao_display()
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Refeição atualizada com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('listar_refeicoes')


class RefeicaoDeleteView(LoginRequiredMixin, DeleteView):
    """Deleta uma refeição."""
    model = Refeicao
    template_name = 'core/refeicao_confirmar_delete.html'
    
    def get_queryset(self):
        return Refeicao.objects.filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Refeição removida com sucesso.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('listar_refeicoes')


# --- Vistas para Agenda Alimentar ---

class AgendaAlimentarListView(LoginRequiredMixin, ListView):
    """Lista todas as agendas do usuário logado."""
    model = AgendaAlimentar
    template_name = 'core/agenda_lista.html'
    context_object_name = 'agendas'
    paginate_by = 10
    
    def get_queryset(self):
        return AgendaAlimentar.objects.filter(usuario=self.request.user).order_by('-id')


class AgendaAlimentarCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova agenda alimentar."""
    model = AgendaAlimentar
    form_class = AgendaAlimentarForm
    template_name = 'core/agenda_form.html'
    
    def form_valid(self, form):
        form.instance.usuario = self.request.user
        messages.success(self.request, 'Agenda criada com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('listar_agendas')


class AgendaAlimentarUpdateView(LoginRequiredMixin, UpdateView):
    """Edita uma agenda existente."""
    model = AgendaAlimentar
    form_class = AgendaAlimentarForm
    template_name = 'core/agenda_form.html'
    
    def get_queryset(self):
        return AgendaAlimentar.objects.filter(usuario=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Agenda atualizada com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('listar_agendas')


class AgendaAlimentarDeleteView(LoginRequiredMixin, DeleteView):
    """Deleta uma agenda."""
    model = AgendaAlimentar
    template_name = 'core/agenda_confirmar_delete.html'
    
    def get_queryset(self):
        return AgendaAlimentar.objects.filter(usuario=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Agenda removida com sucesso.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('listar_agendas')


class AgendaAlimentarWeeklyView(LoginRequiredMixin, DetailView):
    """
    View para gerenciar a agenda semanal de um usuário.
    Permite adicionar até 6 refeições por dia e copiar o cardápio para outros dias.
    """
    model = AgendaAlimentar
    template_name = 'core/agenda_semanal.html'
    context_object_name = 'agenda'
    
    def get_queryset(self):
        return AgendaAlimentar.objects.filter(usuario=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        agenda = self.object
        
        # Dias da semana (0=domingo, 6=sábado)
        DIAS_SEMANA = {
            0: 'Domingo',
            1: 'Segunda',
            2: 'Terça',
            3: 'Quarta',
            4: 'Quinta',
            5: 'Sexta',
            6: 'Sábado'
        }
        
        context['DIAS_SEMANA'] = DIAS_SEMANA
        context['receitas'] = Receita.objects.filter(owner=self.request.user)
        
        # Construir estrutura de refeições por dia
        from datetime import datetime, timedelta
        refeicoes_por_dia = {}
        
        # Buscar todas as refeições associadas a esta agenda via RefeicaoAgenda
        from .models import RefeicaoAgenda
        agenda_refeicoes = RefeicaoAgenda.objects.filter(agenda_alimentar=agenda).select_related('refeicao')
        
        for ar in agenda_refeicoes:
            if ar.refeicao:
                # Converter isoweekday (1=segunda, 7=domingo) para weekday (0=domingo, 6=sábado)
                iso_day = ar.refeicao.date.isoweekday()
                weekday = 0 if iso_day == 7 else iso_day
                if weekday not in refeicoes_por_dia:
                    refeicoes_por_dia[weekday] = []
                refeicoes_por_dia[weekday].append(ar.refeicao)
        
        context['refeicoes_por_dia'] = refeicoes_por_dia
        
        return context


# --- Vistas para Lista de Compra ---

class ListaDeCompraListView(LoginRequiredMixin, ListView):
    """Lista todas as listas de compra do usuário logado."""
    model = ListaDeCompra
    template_name = 'core/lista_compra_lista.html'
    context_object_name = 'listas'
    paginate_by = 10
    
    def get_queryset(self):
        return ListaDeCompra.objects.all().order_by('-data_criacao')


class ListaDeCompraCreateView(LoginRequiredMixin, CreateView):
    """Cria uma nova lista de compra."""
    model = ListaDeCompra
    form_class = ListaDeCompraForm
    template_name = 'core/lista_compra_form.html'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == 'POST':
            data = kwargs['data'].copy()
            # Extrair ingredientes selecionados
            ingredientes_selecionados = self.request.POST.getlist('ingredientes')
            data['ingredientes'] = ingredientes_selecionados
            kwargs['data'] = data
        return kwargs
    
    def form_valid(self, form):
        lista = form.save()
        
        # Adicionar ingredientes à lista
        ingredientes_selecionados = self.request.POST.getlist('ingredientes')
        for ing_id in ingredientes_selecionados:
            try:
                ingrediente = Ingrediente.objects.get(id=ing_id)
                quantidade_gramas = self.request.POST.get(f'gramas_{ing_id}')
                quantidade_ml = self.request.POST.get(f'ml_{ing_id}')
                
                IngredienteListaCompra.objects.create(
                    lista_de_compra=lista,
                    ingrediente=ingrediente,
                    quantidade_gramas=int(quantidade_gramas) if quantidade_gramas else None,
                    quantidade_ml=int(quantidade_ml) if quantidade_ml else None,
                )
            except (Ingrediente.DoesNotExist, ValueError):
                continue
        
        messages.success(self.request, 'Lista de compra criada com sucesso.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('listar_listas_compra')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ingredientes'] = Ingrediente.objects.all().order_by('nome')
        return context


class ListaDeCompraDeleteView(LoginRequiredMixin, DeleteView):
    """Deleta uma lista de compra."""
    model = ListaDeCompra
    template_name = 'core/lista_compra_confirmar_delete.html'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Lista de compra removida com sucesso.')
        return super().delete(request, *args, **kwargs)
    
    def get_success_url(self):
        return reverse_lazy('listar_listas_compra')


class ListaDeCompraPrintView(LoginRequiredMixin, DetailView):
    """View para exibir a lista de compra em formato imprimível."""
    model = ListaDeCompra
    template_name = 'core/lista_compra_imprimir.html'
    context_object_name = 'lista'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lista = self.object
        
        # Agrupar ingredientes por categoria
        ingredientes = IngredienteListaCompra.objects.filter(
            lista_de_compra=lista
        ).select_related('ingrediente', 'ingrediente__categoria')
        
        # Agrupar por categoria
        por_categoria = {}
        for ing_lista in ingredientes:
            categoria = ing_lista.ingrediente.categoria.nome if ing_lista.ingrediente.categoria else 'Sem categoria'
            if categoria not in por_categoria:
                por_categoria[categoria] = []
            por_categoria[categoria].append(ing_lista)
        
        context['ingredientes_por_categoria'] = por_categoria
        context['total_ingredientes'] = ingredientes.count()
        
        return context