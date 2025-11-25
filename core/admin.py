from django.contrib import admin
from .models import Categoria, Ingrediente, Receita, Usuario, Perfil

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('tipo',)
    search_fields = ('tipo',)

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'descricao')
    search_fields = ('nome',)
    list_filter = ('nome',)

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'caloria')
    search_fields = ('nome',)
    list_filter = ('categoria',)
    ordering = ('nome',)

@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tempo_preparo', 'is_ai_generated')
    search_fields = ('titulo',)
    list_filter = ('is_ai_generated',)
    readonly_fields = ('is_ai_generated',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'perfil', 'is_active')
    search_fields = ('username', 'email')
    list_filter = ('perfil', 'is_active')
    ordering = ('username',)
