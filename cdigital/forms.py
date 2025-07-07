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
        fields = ['nome', 'email', 'senha', 'senha2', 'is_admin']
        widgets = {
            'senha': forms.PasswordInput(attrs={'placeholder': 'Digite a senha'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        instance = super().save(commit=False)
        senha = self.cleaned_data.get('senha')

        if senha:
            instance.senha = make_password(senha)

        if commit:
            instance.save()

        return instance



class AgendaForm(forms.Form):
    cliente = forms.ModelChoiceField(queryset=Clientes.objects.all(), label='Cliente')
    data = forms.DateField(label='Data')
    hora_inicio = forms.TimeField(label='Hora de Início')
    hora_fim = forms.TimeField(label='Hora de Fim')
    descricao = forms.CharField(widget=forms.Textarea, required=False, label='Descrição')

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
   


