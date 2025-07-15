from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from .models import Clientes, Usuarios, Agenda, Atendimentos, Convenios
from .forms import Clientesform, UsuariosForm, AgendaForm, AtendimentosForm, Conveniosform
from .forms import ClientesModelForm, UsuariosModelForm, AgendaModelForm, AtendimentosModelForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from cdigital.models import Usuarios  
from datetime import date
from .forms import LoginForm
from django.contrib.auth import login as django_login
from django import forms
from django.db.models import Q
from django.contrib.auth import logout
from django.db.utils import IntegrityError


def index(request):
    login_ok = False

    # FORÇA DESLOGAR do Django auth (caso esteja autenticado)
    request.session.pop('_auth_user_id', None)
    request.session.pop('_auth_user_backend', None)
    request.session.pop('_auth_user_hash', None)

    if request.method == 'POST':
        login = request.POST.get('login', '').strip()
        senha = request.POST.get('senha', '').strip()

        try:
            usuario = Usuarios.objects.get(login__iexact=login)
            if check_password(senha, usuario.senha):
                request.session['usuario_id'] = usuario.id
                request.session['usuario_nome'] = usuario.nome
                request.session['usuario_admin'] = usuario.is_admin
                login_ok = True
            else:
                messages.error(request, 'Senha incorreta.')
        except Usuarios.DoesNotExist:
            messages.error(request, 'Usuário não encontrado.')

    elif 'usuario_id' in request.session:
        login_ok = True

    return render(request, 'index.html', {'login_ok': login_ok})
#*******************************************************************************

def logout_view(request):
    request.session.flush()  # remove tudo da sessão, inclusive chaves do Django auth
    return redirect('/')

#*******************************************************************************
def convenios(request):
    if str(request.method) == 'POST':
        form = Conveniosform(request.POST or None)
        if form.is_valid():            
            try:
                form.save()
                messages.success(request, 'Convênio cadastrado com sucesso!')
                return redirect('convenios')
            except IntegrityError:
                messages.error(request, 'Este convênio já está cadastrado.')
        else:
            messages.error(request, 'Erro ao cadastrar o convenio. Verifique os dados e tente novamente.')
    else:
        form = Conveniosform()
        context = {
            'form': form,
        }

    convenios_cadastrados = Convenios.objects.all().order_by('nomeconvenio')

    return render(request, 'convenios.html', {
        'form': form,
        'convenios_cadastrados': convenios_cadastrados,
    })                                 
#*******************************************************************************
def editar_convenio(request, id):
    convenio = get_object_or_404(Convenios, id=id)
    if request.method == 'POST':
        form = Conveniosform(request.POST, instance=convenio)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Convênio atualizado com sucesso!')
                return redirect('convenios')
            except IntegrityError:
                messages.error(request, 'Já existe um convênio com esse nome.')
    else:
        form = Conveniosform(instance=convenio)

    convenios_cadastrados = Convenios.objects.all().order_by('nomeconvenio')

    return render(request, 'convenios.html', {
        'form': form,
        'editando': True,
        'convenio_id': id,
        'convenios_cadastrados': convenios_cadastrados
    })
#*******************************************************************************
def excluir_convenio(request, id):
    convenio = get_object_or_404(Convenios, id=id)
    convenio.delete()
    messages.success(request, 'Convênio excluído com sucesso!')
    return redirect('convenios')
#*******************************************************************************
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

#*******************************************************************************
def autocomplete_cliente(request):
    termo = request.GET.get('term', '')
    clientes = Clientes.objects.filter(nome__icontains=termo)[:10]
    resultados = [{'label': c.nome, 'value': c.nome, 'id': c.pk, 'telefone': c.telefone} for c in clientes]
    return JsonResponse(resultados, safe=False)

#*******************************************************************************
def login_view(request):
    if request.method == 'POST':
        login = request.POST.get('login')
        senha = request.POST.get('senha')

        try:
            usuario = Usuarios.objects.get(login=login, senha=senha)
            request.session['usuario_id'] = usuario.id
            request.session['usuario_nome'] = usuario.nome
            request.session['usuario_admin'] = usuario.administrador
            return redirect('index')  # ou a página principal do sistema
        except Usuarios.DoesNotExist:
            return render(request, 'index.html', {'erro': 'Login ou senha inválidos'})
    
    return render(request, 'index.html')

#******************************************************************************* Protejção das views com login e verificação de administrador
def login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'usuario_id' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('usuario_admin'):
            return redirect('index')  # Ou mostrar uma página de acesso negado
        return view_func(request, *args, **kwargs)
    return wrapper

#********************************************************************************
@login_required
@admin_required
def usuarios_view(request):
    # apenas admins acessam
    return render(request, 'usuarios.html')

@login_required
@admin_required
def atendimentos_view(request):
    return render(request, 'atendimentos.html')

@login_required
def clientes_view(request):
    return render(request, 'clientes.html')  # qualquer logado acessa

#********************************************************************************
def editar_cliente(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    if request.method == 'POST':
        form = Clientesform(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente atualizado com sucesso!')
            return redirect('clientes')
    else:
        form = Clientesform(instance=cliente)
    
    return render(request, 'editar_cliente.html', {'form': form})

#*******************************************************************************
def excluir_cliente(request, pk):
    cliente = get_object_or_404(Clientes, pk=pk)
    cliente.delete()
    messages.success(request, 'Cliente excluído com sucesso!')
    return redirect('clientes')
#********************************************************************************
def lista_clientes(request):
    busca = request.GET.get('busca', '').strip()
    if busca:
        clientes = Clientes.objects.filter(
            Q(nome__icontains=busca) |
            Q(cpf__icontains=busca)
        )
    else:
        clientes = Clientes.objects.all()

    return render(request, 'lista_clientes.html', {
        'clientes': clientes,
        'busca': busca,
    })
#******************************************************************************
def atendimentos_do_dia(request):
    data_hoje = date.today()
    profissional_id = request.GET.get('profissional')  # captura o profissional do filtro (GET)
    profissionais = Usuarios.objects.filter(is_medico=True)

    # Começa com todos os agendamentos do dia
    atendimentos = Agenda.objects.filter(data=data_hoje)

    # Se selecionou um profissional, filtra por ele
    if profissional_id:
        atendimentos = atendimentos.filter(profissional_id=profissional_id)

    # Ordena por hora de início
    atendimentos = atendimentos.order_by('hora_inicio')

    context = {
        'data_hoje': data_hoje,
        'atendimentos': atendimentos,
        'profissionais': profissionais,
    }

    return render(request, 'atendimentos.html', context)

#*******************************************************************************
    
def atendimentos(request):
    hoje = date.today()
    profissional_id = request.GET.get('profissional')

    profissionais = Usuarios.objects.filter(is_medico=True)
    atendimentos = Atendimentos.objects.filter(data=hoje)

    if profissional_id:
        atendimentos = atendimentos.filter(profissional_id=profissional_id)

    return render(request, 'atendimentos.html', {
        'data_hoje': hoje,
        'profissionais': profissionais,
        'atendimentos': atendimentos
    })

#*******************************************************************************
def editar_atendimento(request, agenda_id):
    agendamento = get_object_or_404(Agenda, id=agenda_id)
    profissionais = Usuarios.objects.filter(is_medico=True)

    if request.method == 'POST':
        descricao = request.POST.get('descricao')
        profissional_id = request.POST.get('profissional')

        # Atualiza o agendamento existente
        agendamento.descricao = descricao
        agendamento.profissional_id = profissional_id
        agendamento.save()

        # Cria um registro de atendimento com base no agendamento
        Atendimentos.objects.create(
            cliente=agendamento.cliente,
            data=agendamento.data,
            hora_inicio=agendamento.hora_inicio,
            hora_fim=agendamento.hora_fim,
            descricao=descricao,
            profissional_id=profissional_id
        )

        messages.success(request, 'Atendimento registrado com sucesso!')
        return redirect('atendimentos')

    # Buscar atendimentos anteriores do mesmo cliente
    atendimentos_anteriores = Atendimentos.objects.filter(
        cliente=agendamento.cliente
    ).order_by('-data','hora_inicio')

    return render(request, 'editar_atendimento.html', {
        'agendamento': agendamento,
        'profissionais': profissionais,
        'atendimentos_anteriores': atendimentos_anteriores
    })
#*******************************************************************************
def agenda(request):
    form = AgendaForm()
    data_filtro = request.GET.get('data')  # captura a data enviada no filtro
    agenda_lista = Agenda.objects.all().order_by('data', 'hora_inicio')

    profissionais = Usuarios.objects.filter(is_medico=True)
    convenios = Convenios.objects.all()

    if data_filtro:
        agenda_lista = agenda_lista.filter(data=data_filtro).order_by('hora_inicio')
    #else:
        #agenda_lista = Agenda.objects.filter(data=date.today()).order_by('hora_inicio')

    if request.method == 'POST':
        form = AgendaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agendamento realizado com sucesso!')
            return redirect('agenda')
        else:
            messages.error(request, 'Erro ao realizar agendamento. Verifique os dados e tente novamente.')
            
    else:
        form = AgendaForm()

   
    context = {
        'form': form,
        'agenda_lista': agenda_lista,
        'data_filtro': data_filtro,
        'profissionais': profissionais,
        'convenios': convenios,
    }
    return render(request, 'agenda.html', context)

#*******************************************************************************

def editar_agenda(request, id):
    agendamento = get_object_or_404(Agenda, pk=id)
    profissionais = Usuarios.objects.all()  # <-- você já pegou aqui, mas não usou no render
    convenios = Convenios.objects.all()    

    if request.method == 'POST':
        form = AgendaForm(request.POST, instance=agendamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Agendamento alterado com sucesso!')
            return redirect('agenda')
    else:
        form = AgendaForm(instance=agendamento)

    context = {
        'form': form,
        'agenda': agendamento,
        'convenios': convenios,
        'profissionais': profissionais,
    }    

    return render(request, 'editar_agenda.html', context)
#*******************************************************************************
def excluir_agenda(request, id):
    agendamento = get_object_or_404(Agenda, pk=id)
    if request.method == 'POST':
        agendamento.delete()
        messages.success(request, 'Agendamento excluído com sucesso!')
        return redirect('agenda')
    return render(request, 'confirmar_exclusao.html', {'agendamento': agendamento})
#*******************************************************************************

def usuarios(request):
    if request.method == 'POST':
        form = UsuariosForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            # criptografa a senha antes de salvar
            usuario.senha = make_password(usuario.senha)
            usuario.save()
            
            messages.success(request, 'Usuário cadastrado com sucesso!')
            return redirect('usuarios')
        else:
            messages.error(request, 'Erro ao cadastrar usuário. Verifique os dados e tente novamente.')
    else:
        form = UsuariosForm()

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
            usuario_temp = form.save(commit=False)

            # Se a senha foi alterada (não é igual ao hash atual)
            if usuario_temp.senha != usuario.senha:
                usuario_temp.senha = make_password(usuario_temp.senha)
            
            usuario_temp.save()
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