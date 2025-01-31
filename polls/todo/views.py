from django.shortcuts import render, redirect, get_object_or_404
from todo.models import *
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import *
from .forms_models import *
from .user import auto_logout_after_one_hour
from .sql import delete, error
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
#Os usuario não podem acessar as funções set_list, set_task, aditar_tarefa, editar_tarefa e user_info, se naõ estiver logado

#Os usuario não podem acessar lista/tarefas que não foram eles que criaram

# Depois de uma hora o usuario é deslogado automaticamente

@auto_logout_after_one_hour
def index(request):
    """ 
    Renderiza o index do site, renderizando o index_login se tiver usuario logado, caso contrario 
    renderiza o index
    """
    if request.method == 'GET':
        
        if request.user.is_authenticated:
            user = get_object_or_404(User, pk=request.user.pk)
            listas = Lista.objects.filter(usuario = user).values()
            context = {
                'listas':listas,
                'user_in':True,
                'usuario':user.username
            }
            
            return render(request,'todo/index_login.html', context)
        
        return render(request, 'todo/index.html',{'user_in':False})
    else:
        return redirect('set_list')

@auto_logout_after_one_hour
def custom_login(request):
    """ 
    Faz o login do usuario
    """
    if request.method == 'GET':
        form = UserLoginForm()
        return render(request, 'user/login.html',{'form':form})
    else:
        form = UserLoginForm(request.POST)
        if form.is_valid():
            usuario = form.cleaned_data.get('user')
            senha = form.cleaned_data.get('password')
            user = authenticate(request,username=usuario, password=senha)
            if user is not None:
                login(request,user)
                return redirect('index')
            else:
                messages.error(request, 'Usuario ou senha estão incorretos')
                return render(request, 'user/login.html',{'form':form})

@auto_logout_after_one_hour
def register(request):
    """ Faz o cadastro do usuario """
    if request.method == 'GET':

        form = RegisterForm()
        return render(request, 'user/register.html',{'form':form})
    else:
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.saveh(request.POST.get('username'),request.POST.get('password'),request.POST.get('email'))
            return redirect('login')
        else:
            messages.error(request,f'{form.errors}')
            return render(request, 'user/register.html',{'form':form})
        
@auto_logout_after_one_hour
def mudarSenha(request):
    """ Altera a senha do usuario """
    if request.method == 'GET':
        form = UpdateSenhaForm()

        return render(request, 'user/mudarSenha.html',{'form':form})
    else:
        form = UpdateSenhaForm(request.POST)
        if form.is_valid() and form.ipass() and form.user_exist():
            usuario = form.cleaned_data.get('usuario')
            user = get_object_or_404(User, username = usuario)
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            return redirect('login')
        elif not form.ipass():
            messages.error(request,'As senha não batem')
            return render(request, 'user/mudarSenha.html',{'form':form})
        else:
            messages.error(request, 'Usuario não existe')
            return render(request, 'user/mudarSenha.html',{'form':form})
        
@auto_logout_after_one_hour
@login_required
def set_list(request):
    """ Renderiza o formulario para adicionar uma lista """
    form = RegisterListForm()
    if request.method == "GET":
        return render(request,'todo/set_list.html',{'form':form,'usuario':request.user})
    else:
        form = RegisterListForm(request.POST)
        return error(form, 'set_list',request)
    
@auto_logout_after_one_hour
@login_required
def getList(request, pk):
        """ Mostra uma lista com mais detalhes """
        if not 'Deletar' in request.POST or request.method == 'GET':

            lista = get_object_or_404(Lista,pk=pk)
            if lista.usuario.pk == request.user.pk:
                tarefas = Tarefa.objects.filter(lista = lista)
                context={
                    'lista':lista,
                    'tarefas':tarefas,
                    'usuario':lista.usuario
                }
                return render(request,'todo/get_list.html',context)
            else:
                
                messages.error(request,'A lista que você está tentando acessar não pertence a você')
                return render(request, 'todo/get_list.html',{'usuario':request.user})
        else:
            delete(request, Lista)
            return redirect('index')
        
@auto_logout_after_one_hour
@login_required
def set_task(request):
    """ Renderiza o formulario para adiconar uma tarefa """
    if request.method == 'GET':

            form = RegisterTaskForm()
            try:    
                user = get_object_or_404(User, pk=request.user.pk)
            except:
                return redirect('login')
            else:
                return render(request,'todo/set_task.html',{'form':form,'usuario':user.username})
    else:
        
        if not 'Deletar' in request.POST:
            lista = get_object_or_404(Lista, pk=request.GET.get('Enviar'))
            if lista.usuario.pk == request.user.pk:
                form = RegisterTaskForm(request.POST)
                Lista.objects.filter(pk=request.GET.get('Enviar')).update(data_atualizacao = timezone.now())
                return error(form, 'set_task',request, f'get_list/{lista.pk}')
            else:
               user = get_object_or_404(User, pk=request.user.pk)
               form = RegisterTaskForm()
               messages.error(request,' A tarefa que você tentou acessar não pertence a você')
               context={
                   'form':form,
                   'usuario':user.username
               }
               return render(request, 'todo/set_task.html',context)
        else:   

                tarefa = get_object_or_404(Tarefa,pk=request.POST.get('Deletar'))
                delete(request,Tarefa)
                return redirect('get_list', pk=tarefa.lista.pk)
   
@auto_logout_after_one_hour       
@login_required
def editar_lista(request,pk):
    """ Renderiza o formulario para editar uma lista """
    lista = get_object_or_404(Lista,pk=pk)
    if request.method == "GET":
        if lista.usuario.pk == request.user.pk:
            form = UpdateListForm(instance=lista)
            context = {
                'form':form,
                'nome':lista.titulo,
                'usuario':request.user
            }
            return render(request,'todo/update_list.html',context)
        else:
            form = UpdateListForm()
            messages.error(request,' A tarefa que você tentou acessar não pertence a você')
            context={
                'form':form,
                'usuario':request.user,
            }
            return render(request, 'todo/update_list.html',context)

    else:
        form = UpdateListForm(request.POST, instance=lista)
        if form.is_valid():
            form.save()
            Lista.objects.filter(pk=pk).update(data_atualizacao = timezone.now())
            return redirect('index')
        else:
            return error(form,'update_list',request, 'editar_lista')
       
@auto_logout_after_one_hour            
@login_required
def editar_tarefa(request, pk):
    """ Renderiza o formulario para editar uma tarefa"""
    tarefa = get_object_or_404(Tarefa,pk=pk)
    if request.method == "GET":
        form = UpdateTaskForm(instance=tarefa)
        return render(request,'todo/update_task.html',{'form':form,'usuario':tarefa.user})
    else:
        
        form = UpdateTaskForm(request.POST, instance=tarefa)
        if tarefa.user.pk == request.user.pk:
            if form.is_valid():
                form.save()
                Lista.objects.filter(pk=tarefa.lista.pk).update(data_atualizacao = timezone.now())
                if form.cleaned_data.get('status') == 'concluido':
                    Tarefa.objects.filter(pk=pk).update(concluido=True, dataConclusao = timezone.now())
                else:
                    Tarefa.objects.filter(pk=pk).update(concluido=False, dataConclusao = None)

                return redirect('get_list', pk=tarefa.lista.pk)
            else:
               return error(form,'update_task',request)
        else:
            messages.error(request,' A tarefa que você tentou acessar não pertence a você')
            context={
                'form':form,
                'usuario':request.user,
                

            }
            return render(request, 'todo/update_task.html',context)
        
@auto_logout_after_one_hour  
@login_required
def custom_logout(request):
    """ Faz o logout do usuario """
    logout(request)
    return redirect('index')

@auto_logout_after_one_hour
@login_required
def user_info(request):
    """ Mostra as informações de username e email do usuario logado """
    user = get_object_or_404(User, pk=request.user.pk)
    return render(request,'user/user_info.html',{'user':user})
