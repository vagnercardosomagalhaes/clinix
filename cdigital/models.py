from django.db import models
from django.utils.text import slugify
from django.db.models import signals
from django.contrib.auth.hashers import make_password, is_password_usable
from django.utils import timezone

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
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.nomeconvenio
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nomeconvenio)
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
    profissional = models.ForeignKey(Usuarios, on_delete=models.CASCADE, related_name='agendamentos')

    def __str__(self):
        return f"{self.cliente.nome} - {self.data} {self.hora_inicio} - {self.hora_fim}"





    
    
    

