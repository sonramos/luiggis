from django.contrib import admin
from .models import Categoria, Ingrediente, Receita, Usuario, Perfil, RestricaoAlimentar

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('tipo',)
    search_fields = ('tipo',)

@admin.register(RestricaoAlimentar)
class RestricaoAlimentarAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descricao', 'is_active')
    search_fields = ('tipo',)
    list_filter = ('is_active',)
    ordering = ('tipo',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    list_filter = ('nome',)

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'caloria', 'get_porcao_display')
    search_fields = ('nome',)
    list_filter = ('categoria', 'restricoes')
    ordering = ('nome',)
    filter_horizontal = ('restricoes',)

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tempo_preparo', 'is_ai_generated', 'owner')
    search_fields = ('titulo',)
    list_filter = ('is_ai_generated',)
    readonly_fields = ('is_ai_generated',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'perfil', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('perfil', 'is_active')
    ordering = ('username',)
