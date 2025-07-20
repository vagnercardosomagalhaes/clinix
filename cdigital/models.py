from django.db import models
from django.utils.text import slugify
from django.db.models import signals
from django.contrib.auth.hashers import make_password, is_password_usable
from django.utils import timezone
from django.core.validators import RegexValidator


class Base(models.Model):

    criado = models.DateTimeField('Data de criação',auto_now_add=True)
    modigicado = models.DateTimeField('Data de atualização',auto_now=True)
    ativo = models.BooleanField('Ativo', default=True)

    class Meta:
        abstract = True

class Clientes(Base):
    nome = models.CharField('Nome', max_length=100)
    data_nascimento = models.DateField('Data de Nascimento', blank=True, null=True)
    cpf = models.CharField('CPF', max_length=14, unique=True, blank=True, null=True)
    email = models.EmailField('Email', unique=True)
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True)
    endereco = models.CharField('Endereço', max_length=255, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100, blank=True, null=True)
    cidade = models.CharField('Cidade', max_length=100, blank=True, null=True)
    estado = models.CharField('Estado', max_length=2, blank=True, null=True)
    cep = models.CharField('CEP', max_length=10, blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.nome
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


def clientes_pre_save(sender, instance, **kwargs):
    instance.slug = slugify(instance.nome)

signals.pre_save.connect(clientes_pre_save, sender=Clientes)

class Usuarios(models.Model):
    nome = models.CharField('Nome', max_length=100)
    email = models.EmailField('Email', unique=True)
    login = models.CharField('Login', max_length=100, unique=True, null=True, blank=True)
    senha = models.CharField('Senha', max_length=128)
    is_admin = models.BooleanField('É Administrador?', default=False)
    is_medico = models.BooleanField('É Médico',default=False)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.nome

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)

        # Só criptografa se ainda não estiver criptografada
        if self.senha and not self.senha.startswith('pbkdf2_'):
            self.senha = make_password(self.senha)

        super().save(*args, **kwargs)

class Convenios(Base):
    nomeconvenio = models.CharField('Nome', max_length=100, unique=True)
    valor_repasse = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.nomeconvenio

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Armazena o nome original para detectar alterações no save()
        self._original_nomeconvenio = self.nomeconvenio

    def save(self, *args, **kwargs):
        if not self.slug or self.nomeconvenio != self._original_nomeconvenio:
            base_slug = slugify(self.nomeconvenio)
            slug = base_slug
            contador = 1
            # Garante que o slug é único, ignorando o próprio registro se for edição
            while Convenios.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Agenda(models.Model):
    criado = models.DateTimeField(default=timezone.now)
    profissional = models.ForeignKey(Usuarios, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='agendas')
    convenio = models.ForeignKey(Convenios, null=True, blank=True, on_delete=models.SET_NULL)
    telefone = models.CharField('Telefone', max_length=15, blank=True, null=True)    
    data = models.DateField('Data')
    hora_inicio = models.TimeField('Hora de Início')
    hora_fim = models.TimeField('Hora de Fim')
    descricao = models.TextField('Descrição', blank=True, null=True)

    def __str__(self):
        return f"{self.cliente.nome} - {self.cliente.telefone}- {self.data} {self.hora_inicio} - {self.hora_fim}"

class Atendimentos(Base):
    cliente = models.ForeignKey(Clientes, on_delete=models.CASCADE, related_name='atendimentos')
    data = models.DateField('Data')
    hora_inicio = models.TimeField('Hora de Início')
    hora_fim = models.TimeField('Hora de Fim')
    descricao = models.TextField('Descrição', blank=True, null=True)
    finalizado = models.BooleanField(default=False)
    profissional = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='agendamentos')

    def __str__(self):
        return f"{self.cliente.nome} - {self.data} {self.hora_inicio} - {self.hora_fim}"


class Banco(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    simbolo = models.CharField(max_length=10, blank=True, null=True)
    agencia = models.CharField(max_length=20, blank=True, null=True)
    conta = models.CharField(max_length=20, blank=True, null=True)

    #class Meta:
    #    db_table = 'cdigital_banco'  # garante nome explícito da tabela
    #    verbose_name = 'Banco'
    #    verbose_name_plural = 'Bancos'

    def __str__(self):
        return f"{self.nome} ({self.simbolo})" if self.simbolo else self.nome

class Despesa(models.Model):
    codigo = models.CharField(max_length=10,
        validators=[RegexValidator(regex=r'^\d+$', message='Código deve conter apenas números')],
        unique=True,
    )
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"
    
class Receita(models.Model):
    codigo = models.CharField(max_length=10,
        validators=[RegexValidator(regex=r'^\d+$', message='Código deve conter apenas números')],
        unique=True,
    )
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"    
    
class ContaPagar(models.Model):
    vencimento = models.DateField()
    despesa = models.ForeignKey('Despesa', on_delete=models.PROTECT)
    credor = models.CharField(max_length=100)
    descricao = models.CharField(max_length=200, blank=True)
    conta_origem = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.credor} - {self.valor} em {self.vencimento}"


class ContaReceber(models.Model):
    vencimento = models.DateField()
    cliente = models.CharField(max_length=255)
    receita = models.ForeignKey(Receita, on_delete=models.CASCADE)
    descricao = models.CharField(max_length=255, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    conta_destino = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.cliente} - {self.valor} em {self.vencimento}"   

class EntradasMonetarias(models.Model):
    vencimento = models.DateField()
    cliente = models.CharField(max_length=100)
    receita = models.ForeignKey('Receita', on_delete=models.PROTECT)
    convenio = models.ForeignKey('Convenios', on_delete=models.SET_NULL, null=True, blank=True)
    descricao = models.CharField(max_length=200, blank=True)
    conta_destino = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    recebido = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.cliente} - {self.valor} em {self.vencimento}"
    
class SaidasMonetarias(models.Model):
    vencimento = models.DateField()
    credor = models.CharField(max_length=100)
    despesa = models.ForeignKey(Despesa, on_delete=models.PROTECT)
    descricao = models.CharField(max_length=200, blank=True)
    conta_origem = models.ForeignKey(Banco, on_delete=models.SET_NULL, null=True, blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    pago = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.credor} - {self.valor} em {self.vencimento}"    