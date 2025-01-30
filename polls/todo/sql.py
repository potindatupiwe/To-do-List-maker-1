from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages

def delete(request, obj):
    """ Essa função deleta um objeto e mostra uma mensagem dizendo que o objeto foi deletado corretamente """
    object = get_object_or_404(obj, pk=request.POST.get('Deletar'))
    object.delete()
    messages.info(request, 'O objeto foi deletado com sucesso')

def error(form, url,request, rurl = 'index'):
    """ Essa função recebe um formulario, uma url, uma HttpRequest, uma url e redirecionamento,
     e mostra a mensagem de erro caso tenha algum erro, ou redireciona para a url informada"""
    try:
        form.save(request)
    except ValidationError:
        messages.error(request,f'O titulo dado já está em uso')
    except ValueError:
        messages.error(request,f'{form.errors}')
    else:
        form.save(request)
        return redirect(rurl)
    user = get_object_or_404(User, pk=request.user.pk)
    context={
        'error':True,
        'form':form,
        'usuario':user.username
        }
    return render(request,f'todo/{url}.html',context)
