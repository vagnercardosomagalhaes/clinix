from django import forms
from .models import Clientes, Usuarios
from .models import Agenda, Atendimentos 
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password



class Clientesform(forms.ModelForm):
    class Meta:
        model = Clientes
        #fields = ['nome', 'data_nascimento', 'cpf', 'email', 'telefone', 'endereco', 'bairro', 'cidade', 'estado', 'cep']
        exclude = ['slug']
        widgets = {
            'data_nascimento': forms.DateInput(attrs={'type': 'date'},format='%Y-%m-%d'),
            'email': forms.EmailInput(attrs={'placeholder': 'Digite seu email'}),
            'telefone': forms.TextInput(attrs={'placeholder': 'Digite seu telefone'}),
            'endereco': forms.TextInput(attrs={'placeholder': 'Digite seu endereço'}),
            'bairro': forms.TextInput(attrs={'placeholder': 'Digite seu bairro'}),
            'cidade': forms.TextInput(attrs={'placeholder': 'Digite sua cidade'}),
            'estado': forms.TextInput(attrs={'placeholder': 'Digite seu estado'}),
            'cep': forms.TextInput(attrs={'placeholder': 'Digite seu CEP'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.data_nascimento:
            self.initial['data_nascimento'] = self.instance.data_nascimento.strftime('%Y-%m-%d')    

class UsuariosForm(forms.ModelForm):
    senha2 = forms.CharField(
        label='Confirme a senha',
        widget=forms.PasswordInput(attrs={'placeholder': 'Repita sua senha'}),
        required=False,
        help_text='Para trocar a senha, preencha os dois campos de senha. Deixe em branco para manter a senha atual.',
        
    )
    class Meta:
        model = Usuarios
        fields = ['nome', 'email', 'login', 'senha', 'senha2', 'is_admin']
        widgets = {
            'senha': forms.PasswordInput(attrs={'class': 'form-control'}),
            'login': forms.TextInput(attrs={'class': 'form-control'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].required = True

        # Só mostra help_text se for edição (instância já salva no banco)
        if self.instance and self.instance.pk:
            self.fields['senha2'].help_text = (
                'Para trocar a senha, preencha os dois campos de senha. '
                'Deixe em branco para manter a senha atual.'
            )

    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get("senha")
        senha2 = cleaned_data.get("senha2")

        # Se um dos dois estiver preenchido, ambos devem estar e ser iguais
        if senha or senha2:
            if not senha or not senha2:
                raise ValidationError("Ambos os campos de senha devem ser preenchidos.")
            if senha != senha2:
                raise ValidationError("As senhas não coincidem.")

            return cleaned_data
    
    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.senha = make_password(self.cleaned_data['senha'])

        if commit:
            usuario.save()
        return usuario


class LoginForm(forms.Form):
    login = forms.CharField(label="Usuário", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    senha = forms.CharField(label="Senha", widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['profissional','cliente', 'data', 'hora_inicio', 'hora_fim', 'descricao']
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
   


