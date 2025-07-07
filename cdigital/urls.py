from consultoriodigital.urls import path
from cdigital.views import index, clientes, agenda, atendimentos, usuarios
from . import views
from django.views import static
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', index, name='index'),
    path('clientes/', clientes, name='clientes'),
    path('atendimentos/', atendimentos, name='atendimentos'),
    path('agenda/', agenda, name='agenda'),
    path('usuarios/', usuarios, name='usuarios'),
    path('clientes/', views.clientes, name='clientes'),
    path('clientes/lista/', views.lista_clientes, name='lista_clientes'), 
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='editar_cliente'),
    path('usuarios/editar/<int:pk>/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/excluir/<int:pk>/', views.excluir_usuario, name='excluir_usuario'),
    #path('contato/', contato, name='contato'),    
]
