from django import forms 
from todo.models import *
from django.contrib.auth.models import User


class UpdateSenhaForm(forms.Form):
    usuario = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), max_length=200, required=True)
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), max_length=200, required=True)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}), max_length=200, required=True)

    def ipass(self):
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')
        return password == password_repeat
        
    
    def user_exist(self) -> bool:
        usuario = self.cleaned_data.get('usuario')
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(username = usuario,email=email)
        except:
            return False
        else:
            return True

class UserLoginForm(forms.Form):
    user = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}),max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}), max_length=200, required=True)