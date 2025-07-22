from consultoriodigital.urls import path
from cdigital.views import index, clientes, agenda, atendimentos, usuarios
from . import views
from django.views import static
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),

    #path('login/', views.login_view, name='login'),
    
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/lista/', views.lista_clientes, name='lista_clientes'), 
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('clientes/excluir/<int:pk>/', views.excluir_cliente, name='excluir_cliente'),
    path('autocomplete/cliente/', views.autocomplete_cliente, name='autocomplete_cliente'),

    path('convenios/', views.convenios, name='convenios'),
    path('convenios/editar/<int:id>/', views.editar_convenio, name='editar_convenio'),
    path('convenios/excluir/<int:id>/', views.excluir_convenio, name='excluir_convenio'),
    
    path('atendimentos/', views.atendimentos_do_dia, name='atendimentos_do_dia'),
    path('atendimentos/', views.atendimentos, name='atendimentos'),
    path('atendimento/editar/<int:agenda_id>/', views.editar_atendimento, name='editar_atendimento'),
    path('atendimento/excluir/<int:atendimento_id>/', views.excluir_atendimento, name='excluir_atendimento'),

    
    path('usuarios/', views.usuarios, name='usuarios'),    
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),    
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),

    path('bancos/', views.bancos, name='bancos'),
    path('bancos/criar/', views.criar_banco, name='criar_banco'),
    path('bancos/editar/<int:id>/', views.editar_banco, name='editar_banco'),
    path('bancos/excluir/<int:id>/', views.excluir_banco, name='excluir_banco'),

    path('atualizar_banco/', views.atualizar_banco, name='atualizar_banco'),

    path('despesas/', views.lista_despesas, name='despesas'),
    path('despesas/criar/', views.criar_despesa, name='criar_despesa'),
    path('despesas/excluir/<int:id>/', views.excluir_despesa, name='excluir_despesa'),
    path('despesas/editar/<int:id>/', views.editar_despesa, name='editar_despesa'),

    path('receitas/', views.lista_receitas, name='receitas'),
    path('receitas/criar/', views.criar_receita, name='criar_receita'),
    path('receitas/excluir/<int:id>/', views.excluir_receita, name='excluir_receita'),
    path('receitas/editar/<int:id>/', views.editar_receita, name='editar_receita'),

    path('contas-pagar/', views.contas_pagar, name='contas_pagar'),
    path('contas-receber/', views.contas_receber, name='contas_receber'),
    path('entradas-monetarias/', views.entradas_monetarias, name='entradas_monetarias'),
    path('saidas-monetarias/', views.saidas_monetarias, name='saidas_monetarias'),

    path('contas-pagar/pagar/<int:conta_id>/', views.pagar_conta, name='pagar_conta'),
    path('receber-conta/', views.receber_conta, name='receber_conta'),

    path('agenda/', views.agenda, name='agenda'),
    path('agenda/editar/<int:id>/', views.editar_agenda, name='editar_agenda'),
    path('agenda/excluir/<int:id>/', views.excluir_agenda, name='excluir_agenda'),
    path('', views.index, name='index'),
    path('logout/', views.logout_view, name='logout'),

    path('empresa/', views.dados_empresa, name='dados_empresa'),
    path('empresa/excluir/<int:id>/', views.excluir_empresa, name='excluir_empresa'),

    path('servicos/', views.servicos, name='servicos'),
    path('servicos/editar/<int:id>/', views.editar_servico, name='editar_servico'),
    path('servicos/excluir/<int:id>/', views.excluir_servico, name='excluir_servico'),

    
    
    #path('contato/', contato, name='contato'),    
]
