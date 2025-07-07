from django.contrib import admin
from .models import Clientes, Agenda, Atendimentos, Usuarios
# Register your models here.

@admin.register(Clientes)
class ClientesAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'telefone', 'endereco', 'bairro', 'cidade', 'estado', 'cep', 'cpf', 'data_nascimento')
    search_fields = ('nome', 'email')
    list_filter = ('ativo',)
    prepopulated_fields = {'slug': ('nome',)}

@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'data', 'hora_inicio', 'hora_fim', 'descricao')
    search_fields = ('cliente__nome',)
    list_filter = ('data',)

@admin.register(Atendimentos)
class AtendimentosAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'data', 'hora_inicio', 'hora_fim', 'descricao')
    search_fields = ('cliente__nome',)
    list_filter = ('data',)

@admin.register(Usuarios)
class UsuariosAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'is_admin')
    search_fields = ('nome', 'email')
    list_filter = ('is_admin',)

