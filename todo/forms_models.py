from django import forms 
from todo.models import *
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils import timezone

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password', 'email']
        widgets = {
            'password':forms.PasswordInput(attrs={'placeholder':'Digite a sua senha','class':'form-control'}),
            'username':forms.TextInput(attrs={'placeholder':'Digite o seu usuario', 'class':'form-control'}),
            'email':forms.EmailInput(attrs={'placeholder':'Digite o seu email', 'class':'form-control'}),
        }
    def saveh(self, username, password, email):
        user = User(username = username, password = password, email = email)
        user.set_password(password)
        user.save()


class RegisterListForm(forms.ModelForm):
    class Meta:
        model = Lista
        fields = ['titulo','descricao']
        widgets = {
            'descricao':forms.Textarea(attrs={'placeholder':'Digite uma descrição','class':'form-control'}),
            'titulo':forms.TextInput(attrs={'placeholder':'Digite um titulo','class':'form-control'})
        }
    def save(self,request,commit=True):
        lista = super().save(commit=False)
        lista.usuario = get_object_or_404(User, pk=request.user.pk)
        lista.data_criacao = timezone.now()
        lista.data_atualizacao = timezone.now()
        if commit:
            lista.save()

class RegisterTaskForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'prioridade','dataVencimento']
        widgets = {
            'titulo':forms.TextInput(attrs={'class':'form-control'}),
            'descricao':forms.Textarea(attrs={'class':'form-control'}),
            'prioridade':forms.Select(attrs={'class':'form-control'}),
            'dataVencimento':forms.DateInput(format='%d/%m/%Y',attrs={'class':'form-control',
                                                                      'type':'date'})
           
        }
    def save(self,request,commit=True):
            task = super().save(commit=False)
            lista = get_object_or_404(Lista, pk=request.GET.get('Enviar'))
            task.lista = lista
            task.dataCriacao = timezone.now()
            task.user = task.lista.usuario
            if commit:
                task.save()

class UpdateTaskForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['titulo', 'descricao', 'prioridade','dataVencimento', 'status']
        widgets = {
            'titulo':forms.TextInput(attrs={'class':'form-control'}),
            'descricao':forms.Textarea(attrs={'class':'form-control'}),
            'prioridade':forms.Select(attrs={'class':'form-control'}),
            'dataVencimento':forms.DateInput(format='%d/%m/%Y',attrs={'class':'form-control','type':'date'}),
            'status':forms.Select(attrs={'class':'form-select'})
        }

class UpdateListForm(forms.ModelForm):
    class Meta:
        model = Lista
        fields = ['titulo', 'descricao']
        widgets = {
            'descricao':forms.Textarea(attrs={'placeholder':'Digite uma descrição','class':'form-control'}),
            'titulo':forms.TextInput(attrs={'placeholder':'Digite um titulo','class':'form-control'})
        }
    

