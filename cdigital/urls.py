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

    
    path('usuarios/', views.usuarios, name='usuarios'),    
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),    
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),

    path('agenda/', views.agenda, name='agenda'),
    path('agenda/editar/<int:id>/', views.editar_agenda, name='editar_agenda'),
    path('agenda/excluir/<int:id>/', views.excluir_agenda, name='excluir_agenda'),
    path('', views.index, name='index'),
    path('logout/', views.logout_view, name='logout'),
    
    #path('contato/', contato, name='contato'),    
]
