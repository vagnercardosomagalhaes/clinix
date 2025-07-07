from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Clientes, Usuarios, Agenda, Atendimentos
from .forms import Clientesform, UsuariosForm, AgendaForm, AtendimentosForm
from .forms import ClientesModelForm, UsuariosModelForm, AgendaModelForm, AtendimentosModelForm


def index(request):    
    return render(request, 'index.html')

def clientes(request):
    if str(request.method) == 'POST':
        form = Clientesform(request.POST or None)
        if form.is_valid():
            # Salva o cliente no banco de dados
            #cli = form.save(commit=False)
            form.save()
            messages.success(request, 'Cliente cadastrado com sucesso!')
            return redirect('clientes')
        else:
            messages.error(request, 'Erro ao cadastrar cliente. Verifique os dados e tente novamente.')
    else:
        form = ClientesModelForm()
        context = {
            'form': form,
        }
    #return render(request, 'clientes.html',context)
    return render(request, 'clientes.html', {'form': form})


def editar_cliente(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    form = Clientesform(request.POST or None, instance=cliente)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')

    return render(request, 'editar_cliente.html', {'form': form, 'cliente': cliente})


def lista_clientes(request):
    clientes = Clientes.objects.all()
    return render(request, 'lista_clientes.html', {'clientes': clientes})


    
def atendimentos(request):
    return render(request, 'atendimentos.html')

def agenda(request):
    return render(request, 'agenda.html')

def usuarios(request):   
    if request.method == 'POST':
        form = UsuariosForm(request.POST)
        if form.is_valid():
            form.save()  # salva o usuário com senha criptografada
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('usuarios')  # redirecione conforme sua lógica
        else:
            messages.error(request, 'Erro ao cadastrar usuário. Verifique os dados e tente novamente.')
            form = UsuariosForm(request.POST)
    else:
        form = UsuariosForm()

    # Busca todos os usuários para exibir na lista
    usuarios_lista = Usuarios.objects.all()    

    return render(request, 'usuarios.html', {
        'form': form,
        'usuarios_lista': usuarios_lista,
        })

def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuarios, pk=pk)
    if request.method == 'POST':
        form = UsuariosForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário alterado com sucesso!')
            return redirect('usuarios')
    else:
        form = UsuariosForm(instance=usuario)
    return render(request, 'editar_usuario.html', {'form': form})

def excluir_usuario(request, pk):
    usuario = get_object_or_404(Usuarios, pk=pk)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('usuarios')