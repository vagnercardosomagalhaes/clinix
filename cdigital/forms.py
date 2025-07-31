from django import forms
from .models import Clientes, Usuarios, Convenios
from .models import Agenda, Atendimentos 
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from .models import Receita, Convenios, Empresa, Servico




class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'cnpj', 'registro_ans']

#*****************************************************************************
class ServicosForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['codigo', 'descricao']        

#*****************************************************************************
class Conveniosform(forms.ModelForm):
    class Meta:
        model = Convenios
        fields = '__all__'
        exclude = ['slug']  
         
    def clean_nomeconvenio(self):
        nome = self.cleaned_data['nomeconvenio']
        qs = Convenios.objects.filter(nomeconvenio__iexact=nome)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError('Já existe um convênio com esse nome.')
        return nome
#*****************************************************************************
#     
class Clientesform(forms.ModelForm):
    class Meta:
        model = Clientes
        #fields = ['nome', 'data_nascimento', 'cpf', 'email', 'telefone', 'endereco', 'bairro', 'cidade', 'estado', 'cep']
        fields = '__all__'
        widgets = {
            'slug': forms.HiddenInput(),
            'sexo': forms.Select(attrs={'class': 'form-control campo-sexo'}),
            'convenio': forms.Select(attrs={'class': 'form-control campo-convenio'}),
            'carteirinha': forms.TextInput(attrs={'class': 'form-control campo-carteirinha'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date','class': 'form-control input-medio'},format='%Y-%m-%d'),
            'email': forms.EmailInput(attrs={'class': 'form-control campo-email','placeholder': 'Digite seu email'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control campo-telefone1','placeholder': 'Digite seu telefone'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control campo-endereco','placeholder': 'Digite seu endereço'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control campo-bairro','placeholder': 'Digite seu bairro'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control campo-cidade','placeholder': 'Digite sua cidade'}),
            'estado': forms.TextInput(attrs={'class': 'form-control campo-estado','placeholder': 'Digite seu estado'}),
            'cep': forms.TextInput(attrs={'class': 'form-control campo-cep','placeholder': 'Digite seu CEP'}),
            
        }
         
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.data_nascimento:
            self.initial['data_nascimento'] = self.instance.data_nascimento.strftime('%Y-%m-%d')      

class UsuariosForm(forms.ModelForm):
    senha2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Repita sua senha',
            'class': 'form-control'
        }),
        required=False,
        help_text='Para trocar a senha, preencha os dois campos de senha. Deixe em branco para manter a senha atual.',
    )

    class Meta:
        model = Usuarios
        fields = ['nome', 'email', 'login', 'senha', 'senha2', 'is_admin', 'is_medico', 'crm']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
            'senha': forms.PasswordInput(attrs={'class': 'form-control'}),
            'crm': forms.TextInput(attrs={'class': 'form-control'}),
            'is_admin': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_medico': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].required = True

        if self.instance and self.instance.pk:
            self.fields['senha2'].help_text = (
                'Para trocar a senha, preencha os dois campos de senha. '
                'Deixe em branco para manter a senha atual.'
            )

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        senha2 = cleaned_data.get("senha2")
        is_medico = cleaned_data.get('is_medico')
        crm = cleaned_data.get('crm')

        if is_medico and not crm:
            self.add_error('crm', 'O campo CRM é obrigatório para médicos.')

        if senha or senha2:
            if not senha or not senha2:
                raise ValidationError("Ambos os campos de senha devem ser preenchidos.")
            if senha != senha2:
                raise ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if self.cleaned_data['senha']:  # Evita sobrescrever se senha estiver vazia (em edição)
            usuario.senha = make_password(self.cleaned_data['senha'])

        if commit:
            usuario.save()
        return usuario

#*****************************************************************************
class LoginForm(forms.Form):
    login = forms.CharField(label="Usuário", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['profissional','cliente', 'data', 'hora_inicio', 'hora_fim', 'descricao', 'convenio']
        widgets = {
            'data': forms.DateInput(attrs={
                'class': 'form-control',
                'id': 'id_data',
                'autocomplete': 'off',}),
            'hora_inicio': forms.TimeInput(attrs={'id': 'id_hora_inicio','placeholder': '00:00'}),
            'hora_fim': forms.TimeInput(attrs={'id': 'id_hora_fim','placeholder': '00:00'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control'}),
            
        }
    

class AtendimentosForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Clientes.objects.all(), label='Cliente')
    data = forms.DateField(label='Data')
    hora_inicio = forms.TimeField(label='Hora de Início')
    hora_fim = forms.TimeField(label='Hora de Fim')
    descricao = forms.CharField(widget=forms.Textarea, required=False, label='Descrição')



class AtendimentosModelForm(forms.ModelForm):
    class Meta:
        model = Atendimentos
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
            'descricao': forms.Textarea(attrs={'rows': 4}),
            'codigo_tuss': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_tuss': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AgendaModelForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time'}),
            'descricao': forms.Textarea(attrs={'rows': 4}),
            
        }   

class ClientesModelForm(forms.ModelForm):
    class Meta:
        model = Clientes
        fields = '__all__'
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'}),
        }      

class UsuariosModelForm(forms.ModelForm):
    class Meta:
        model = Usuarios
        exclude = ['slug']  # Excluímos o slug pois ele será gerado automaticamente

        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Digite seu nome',
                'class': 'form-control',
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Digite seu email',
                'class': 'form-control',
            }),
            'senha': forms.PasswordInput(attrs={
                'placeholder': 'Digite sua senha',
                'class': 'form-control',
            }),
            'is_admin': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }

        labels = {
            'nome': 'Nome completo',
            'email': 'Email',
            'senha': 'Senha',
            'is_admin': 'Administrador?',
        }
   


