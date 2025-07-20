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
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect, get_object_or_404
from .models import Banco
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.management import call_command
import configparser
from django.conf import settings
from copy import deepcopy
from django.db import connections
from .models import Despesa
from .models import Receita
from django.db.models import Sum
from .models import ContaPagar, Banco
from django.db.models.functions import TruncDate
from django.utils.dateparse import parse_date
from .models import ContaReceber
from .models import EntradasMonetarias, Receita
from .models import SaidasMonetarias
from .models import Receita, Convenios
from django.core.exceptions import ValidationError
from decimal import Decimal


class ClienteDBMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lê o nome do banco do .ini
        config = configparser.ConfigParser()
        config.read('C:\\cdigital\\bd.ini')
        nome_banco = config.get('database', 'nome', fallback=None)

        if nome_banco:
            db_config = deepcopy(settings.DATABASES['default'])
            db_config['NAME'] = nome_banco
            settings.DATABASES['cliente_db'] = db_config

            # Garante que a conexão antiga seja descartada
            if 'cliente_db' in connections:
                connections['cliente_db'].close()
                del connections['cliente_db']

        response = self.get_response(request)
        return response


@csrf_exempt
def atualizar_banco(request):
    if request.method != "POST":
        return JsonResponse({"erro": "Método não permitido."}, status=405)

    config = configparser.ConfigParser()
    config.read('C:\\cdigital\\bd.ini')
    nome_banco = config.get('database', 'nome', fallback=None)

    if not nome_banco:
        return JsonResponse({"erro": "Banco não definido no arquivo de configuração bd.ini"}, status=400)

    # Atualiza ou cria configuração do banco dinâmico
    if 'cliente_db' not in settings.DATABASES:
        db_config = deepcopy(settings.DATABASES['default'])
        db_config['NAME'] = nome_banco
        settings.DATABASES['cliente_db'] = db_config
    else:
        settings.DATABASES['cliente_db']['NAME'] = nome_banco

    # Fecha conexão antiga para forçar nova conexão
    if 'cliente_db' in connections:
        connections['cliente_db'].close()
        del connections['cliente_db']

    try:
        call_command('makemigrations')
        call_command('migrate', 'cdigital', database='cliente_db')
        return JsonResponse({"mensagem": f"✅ Banco `{nome_banco}` atualizado com sucesso."})
    except Exception as e:
        return JsonResponse({"erro": f"❌ Erro ao migrar banco: {str(e)}"}, status=500)


@never_cache
def index(request):
    login_ok = False

    # FORÇA DESLOGAR do Django auth (caso esteja autenticado)
    request.session.pop('_auth_user_id', None)
    request.session.pop('_auth_user_backend', None)
    request.session.pop('_auth_user_hash', None)

    # === 1. Lê nome do banco do .ini ===
    config = configparser.ConfigParser()
    config.read('C:\\cdigital\\bd.ini')
    nome_banco = config.get('database', 'nome', fallback=None)

    if not nome_banco:
        messages.error(request, 'Banco de dados não definido no bd.ini.')
        return render(request, 'index.html', {'login_ok': False})

    # === 2. Registra o banco dinamicamente se não existir ===
    if nome_banco not in settings.DATABASES:
        db_config = deepcopy(settings.DATABASES['default'])
        db_config['NAME'] = nome_banco
        settings.DATABASES[nome_banco] = db_config

    # === 3. Garante que conexão está reiniciada ===
    if nome_banco in connections:
        connections[nome_banco].close()
        del connections[nome_banco]

    # === 4. Lógica de login ===
    if request.method == 'POST':
        login = request.POST.get('login', '').strip()
        senha = request.POST.get('senha', '').strip()

        if login == 'adm' and senha == 'adm':
            request.session['usuario_id'] = 0
            request.session['usuario_nome'] = 'Administrador'
            request.session['usuario_is_admin'] = True
            login_ok = True
        else:
            try:
                usuario = Usuarios.objects.using(nome_banco).get(login__iexact=login)
                if check_password(senha, usuario.senha):
                    request.session['usuario_id'] = usuario.id
                    request.session['usuario_nome'] = usuario.nome
                    request.session['usuario_is_admin'] = usuario.is_admin
                    login_ok = True
                else:
                    messages.error(request, 'Senha incorreta.')
            except Usuarios.DoesNotExist:
                messages.error(request, 'Usuário não encontrado.')

    elif request.session.get('usuario_id') is not None:
        login_ok = True

    return render(request, 'index.html', {'login_ok': login_ok})     
                                                                    
#*******************************************************************************

def logout_view(request):
    request.session.flush()  # remove tudo da sessão, inclusive chaves do Django auth
    return redirect('/')

#*******************************************************************************
def convenios(request):
    if request.method == 'POST':
        form = Conveniosform(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Convênio cadastrado com sucesso!')
            return redirect('convenios')
        else:
            messages.error(request, 'Erro ao cadastrar o convênio. Verifique os dados e tente novamente.')
    else:
        form = Conveniosform()

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
            messages.error(request, 'Erro ao atualizar o convênio.')
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
            request.session['usuario_is_admin'] = usuario.administrador
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
            #usuario.senha = make_password(usuario.senha)
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

#*************************************************************************
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
#****************************************************************************
def excluir_usuario(request, pk):
    usuario = get_object_or_404(Usuarios, pk=pk)
    usuario.delete()
    messages.success(request, 'Usuário excluído com sucesso!')
    return redirect('usuarios')

#****************************************************************************

def bancos(request):
    bancos = Banco.objects.using('cliente_db').all().order_by('nome')
    return render(request, 'bancos.html', {'bancos': bancos})

def criar_banco(request):
    if request.method == 'POST':
        Banco.objects.create(
            nome=request.POST['nome'],
            simbolo=request.POST['simbolo'],
            agencia=request.POST['agencia'],
            conta=request.POST['conta']
        )
    return redirect('bancos')

def editar_banco(request, id):
    banco = get_object_or_404(Banco, id=id)
    if request.method == 'POST':
        banco.nome = request.POST['nome']
        banco.simbolo = request.POST['simbolo']
        banco.agencia = request.POST['agencia']
        banco.conta = request.POST['conta']
        banco.save()
    return redirect('bancos')

def excluir_banco(request, id):
    banco = get_object_or_404(Banco, id=id)
    banco.delete()
    return redirect('bancos')

#*****************************************************************************
def lista_despesas(request):
    despesas = Despesa.objects.all()
    return render(request, 'despesas.html', {'despesas': despesas})

def criar_despesa(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nome = request.POST.get('nome')
        Despesa.objects.create(codigo=codigo, nome=nome)
    return redirect('despesas')

def excluir_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id)
    despesa.delete()
    return redirect('despesas')

def editar_despesa(request, id):
    despesa = get_object_or_404(Despesa, id=id)
    if request.method == 'POST':
        despesa.codigo = request.POST.get('codigo')
        despesa.nome = request.POST.get('nome')
        despesa.save()
    return redirect('despesas')
#**********************************************************************************
def lista_receitas(request):
    receitas = Receita.objects.all()
    return render(request, 'receitas.html', {'receitas': receitas})

def criar_receita(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        nome = request.POST.get('nome')
        Receita.objects.create(codigo=codigo, nome=nome)
    return redirect('receitas')

def excluir_receita(request, id):
    receita = get_object_or_404(Receita, id=id)
    receita.delete()
    return redirect('receitas')

def editar_receita(request, id):
    receita = get_object_or_404(Receita, id=id)
    if request.method == 'POST':
        receita.codigo = request.POST.get('codigo')
        receita.nome = request.POST.get('nome')
        receita.save()
    return redirect('receitas')
#***************************************************************************************
@csrf_exempt
def contas_pagar(request):
    if request.method == 'POST':
        conta_id = request.POST.get('id')
        vencimento = request.POST.get('vencimento')
        despesa_str = request.POST.get('despesa')
        credor = request.POST.get('credor')
        descricao = request.POST.get('descricao')
        conta_origem_id = request.POST.get('conta_origem')
        valor = request.POST.get('valor')

        # Validação mínima para campos obrigatórios
        if not (vencimento and despesa_str and credor and valor and conta_origem_id):
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            return redirect('contas_pagar')

        # Extrai o código da despesa (supondo que veio no formato "01 - Luz")
        codigo = despesa_str.split(' - ')[0].strip().zfill(2)
        despesa_obj = Despesa.objects.filter(codigo=codigo).first()

        if not despesa_obj:
            messages.error(request, f'Despesa "{despesa_str}" não encontrada.')
            return redirect('contas_pagar')

        # Busca o banco (conta origem)
        conta_origem_obj = None
        if conta_origem_id:
            conta_origem_obj = get_object_or_404(Banco, id=conta_origem_id)

        try:
            valor_decimal = Decimal(valor.replace(',', '.'))
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('contas_pagar')

        if conta_id:
            # Atualiza conta existente
            conta = get_object_or_404(ContaPagar, id=conta_id)
            conta.vencimento = vencimento
            conta.despesa = despesa_obj
            conta.credor = credor
            conta.descricao = descricao
            conta.valor = valor_decimal
            conta.conta_origem = conta_origem_obj
            conta.save()
            messages.success(request, 'Conta atualizada com sucesso.')
        else:
            # Cria nova conta
            ContaPagar.objects.create(
                vencimento=vencimento,
                despesa=despesa_obj,
                credor=credor,
                descricao=descricao,
                valor=valor_decimal,
                conta_origem=conta_origem_obj
            )
            messages.success(request, 'Conta cadastrada com sucesso.')

        return redirect('contas_pagar')

    # GET
    contas = ContaPagar.objects.all().order_by('-vencimento')
    data_de = request.GET.get('data_de')
    data_ate = request.GET.get('data_ate')

    if data_de and data_ate:
        contas = contas.filter(vencimento__range=[data_de, data_ate])

    total = contas.aggregate(Sum('valor'))['valor__sum'] or 0
    credores = ContaPagar.objects.values_list('credor', flat=True).distinct()
    bancos = Banco.objects.all()

    return render(request, 'contas_pagar.html', {
        'contas': contas,
        'despesas': Despesa.objects.all(),
        'credores': credores,
        'bancos': bancos,
        'data_de': data_de,
        'data_ate': data_ate,
        'total': total,
    })

#******************************************************************************************
@csrf_exempt
def contas_receber(request):
    if request.method == 'POST':
        conta_id = request.POST.get('id')
        vencimento = request.POST.get('vencimento')
        cliente = request.POST.get('Cliente')
        receita_id = request.POST.get('receita')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        conta_destino_id = request.POST.get('conta_destino')

        # Validação básica
        if not (vencimento and cliente and receita_id and valor and conta_destino_id):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('contas_receber')

        try:
            receita = Receita.objects.get(id=receita_id)
        except Receita.DoesNotExist:
            messages.error(request, 'Receita inválida.')
            return redirect('contas_receber')

        try:
            valor_decimal = Decimal(valor.replace(',', '.'))
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('contas_receber')

        try:
            conta_destino = Banco.objects.get(id=conta_destino_id)
        except Banco.DoesNotExist:
            messages.error(request, 'Conta destino inválida.')
            return redirect('contas_receber')

        if conta_id:
            conta = get_object_or_404(ContaReceber, id=conta_id)
            conta.vencimento = vencimento
            conta.cliente = cliente
            conta.receita = receita
            conta.descricao = descricao
            conta.valor = valor_decimal
            conta.conta_destino = conta_destino
            conta.save()
            messages.success(request, 'Conta atualizada com sucesso.')
        else:
            ContaReceber.objects.create(
                vencimento=vencimento,
                cliente=cliente,
                receita=receita,
                descricao=descricao,
                valor=valor_decimal,
                conta_destino=conta_destino
            )
            messages.success(request, 'Conta cadastrada com sucesso.')

        return redirect('contas_receber')

    # GET - Listagem
    contas = ContaReceber.objects.all().order_by('-vencimento')
    data_de = request.GET.get('data_de')
    data_ate = request.GET.get('data_ate')

    if data_de and data_ate:
        contas = contas.filter(vencimento__range=[data_de, data_ate])

    total = contas.aggregate(Sum('valor'))['valor__sum'] or 0
    clientes = ContaReceber.objects.values_list('cliente', flat=True).distinct()

    return render(request, 'contas_receber.html', {
        'contas': contas,
        'clientes': clientes,
        'receitas': Receita.objects.all(),
        'bancos': Banco.objects.all(),
        'data_de': data_de,
        'data_ate': data_ate,
        'total': total,
    })
#***********************************************************************************************
def entradas_monetarias(request):
    if request.method == 'POST':
        entrada_id = request.POST.get('id')
        vencimento = request.POST.get('vencimento')
        cliente = request.POST.get('Cliente')
        receita_id = request.POST.get('receita')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        conta_id = request.POST.get('conta')  # novo campo

        # Converte valor
        try:
            valor_decimal = float(valor.replace(',', '.'))
        except:
            valor_decimal = 0

        # Busca receita e conta
        receita = Receita.objects.filter(id=receita_id).first()
        conta_destino = Banco.objects.filter(id=conta_id).first()

        # Cria entrada se dados forem válidos
        if receita and conta_destino and valor_decimal:
           if entrada_id:  # UPDATE
                entrada = EntradasMonetarias.objects.get(id=entrada_id)
                entrada.vencimento = vencimento
                entrada.cliente = cliente
                entrada.receita = receita
                entrada.descricao = descricao
                entrada.valor = valor_decimal
                entrada.conta_destino = conta_destino
                entrada.save()
                messages.success(request, 'Entrada monetária alterada com sucesso.')
           else:  # CREATE
                EntradasMonetarias.objects.create(
                    vencimento=vencimento,
                    cliente=cliente,
                    receita=receita,
                    descricao=descricao,
                    valor=valor_decimal,
                    conta_destino=conta_destino
                )
                messages.success(request, 'Entrada monetária cadastrada com sucesso.')

        return redirect('entradas_monetarias')

    # Filtros
    data_de = request.GET.get('data_de')
    data_ate = request.GET.get('data_ate')
    entradas = EntradasMonetarias.objects.all()

    if data_de:
        entradas = entradas.filter(vencimento__gte=data_de)
    if data_ate:
        entradas = entradas.filter(vencimento__lte=data_ate)

    entradas = entradas.order_by('-vencimento')
    total = entradas.aggregate(Sum('valor'))['valor__sum'] or 0

    clientes = EntradasMonetarias.objects.values_list('cliente', flat=True).distinct()
    receitas = Receita.objects.all()
    bancos = Banco.objects.all()  # novo

    return render(request, 'entradas_monetarias.html', {
        'entradas': entradas,
        'clientes': clientes,
        'receitas': receitas,
        'bancos': bancos,
        'total': total,
        'data_de': data_de,
        'data_ate': data_ate
    })

#***********************************************************************************************
@csrf_exempt
def saidas_monetarias(request):
    if request.method == 'POST':
        saida_id = request.POST.get('id')
        vencimento = request.POST.get('vencimento')
        despesa_id = request.POST.get('despesa')
        credor = request.POST.get('credor')
        descricao = request.POST.get('descricao')
        valor = request.POST.get('valor')
        conta_origem_id = request.POST.get('conta_origem')

        # Validação básica
        if not (vencimento and despesa_id and credor and valor and conta_origem_id):
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('saidas_monetarias')

        try:
            valor_decimal = Decimal(valor.replace(',', '.'))
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('saidas_monetarias')

        despesa_obj = Despesa.objects.filter(id=despesa_id).first()
        banco_obj = Banco.objects.filter(id=conta_origem_id).first()

        if not despesa_obj or not banco_obj:
            messages.error(request, 'Despesa ou conta origem inválida.')
            return redirect('saidas_monetarias')

        if saida_id:
            # Edição
            saida = get_object_or_404(SaidasMonetarias, id=saida_id)
            saida.vencimento = vencimento
            saida.despesa = despesa_obj
            saida.credor = credor
            saida.descricao = descricao
            saida.valor = valor_decimal
            saida.conta_origem = banco_obj
            saida.save()
            messages.success(request, 'Saída atualizada com sucesso.')
        else:
            # Criação
            SaidasMonetarias.objects.create(
                vencimento=vencimento,
                despesa=despesa_obj,
                credor=credor,
                descricao=descricao,
                valor=valor_decimal,
                conta_origem=banco_obj
            )
            messages.success(request, 'Saída cadastrada com sucesso.')

        return redirect('saidas_monetarias')

    # GET
    saidas = SaidasMonetarias.objects.all().order_by('-vencimento')
    data_de = request.GET.get('data_de')
    data_ate = request.GET.get('data_ate')

    if data_de and data_ate:
        saidas = saidas.filter(vencimento__range=[data_de, data_ate])

    total = saidas.aggregate(Sum('valor'))['valor__sum'] or 0
    credores = SaidasMonetarias.objects.values_list('credor', flat=True).distinct()
    despesas = Despesa.objects.all()
    bancos = Banco.objects.all()

    return render(request, 'saidas_monetarias.html', {
        'saidas': saidas,
        'credores': credores,
        'despesas': despesas,
        'bancos': bancos,
        'data_de': data_de,
        'data_ate': data_ate,
        'total': total,
    })

def pagar_conta(request, conta_id):
    conta = get_object_or_404(ContaPagar, id=conta_id)

    # Cria saída monetária com os dados da conta
    SaidasMonetarias.objects.create(
        vencimento=conta.vencimento,
        despesa=conta.despesa,
        credor=conta.credor,
        descricao=conta.descricao,
        valor=conta.valor,
        conta_origem=conta.conta_origem  # se esse campo existir nos dois modelos
    )

    # Remove a conta da tabela de contas a pagar
    conta.delete()

    # Mensagem de sucesso
    messages.success(request, "Conta paga com sucesso.")
    return redirect('contas_pagar')

#*******************************************************************************
@csrf_exempt
def receber_conta(request):
    if request.method == 'POST':
        id_original = request.POST.get('id')
        vencimento = request.POST.get('vencimento')
        receita_id = request.POST.get('receita')
        cliente = request.POST.get('cliente')
        descricao = request.POST.get('descricao')
        conta_destino_id = request.POST.get('conta_destino')
        valor = request.POST.get('valor')

        try:
            valor_decimal = Decimal(valor.replace(',', '.'))
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('contas_receber')

        receita = Receita.objects.filter(id=receita_id).first()
        banco = Banco.objects.filter(id=conta_destino_id).first()

        if not receita or not banco:
            messages.error(request, 'Receita ou conta destino inválida.')
            return redirect('contas_receber')

        EntradasMonetarias.objects.create(
            vencimento=vencimento,
            receita=receita,
            cliente=cliente,
            descricao=descricao,
            valor=valor_decimal,
            conta_destino=banco
        )

        ContaReceber.objects.filter(id=id_original).delete()
        messages.success(request, 'Conta recebida com sucesso.')
        return redirect('contas_receber')