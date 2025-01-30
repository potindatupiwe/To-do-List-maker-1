from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib import messages

def delete(request, obj):
    object = get_object_or_404(obj, pk=request.POST.get('Deletar'))
    object.delete()

def error(form, url,request, rurl = 'index'):
    try:
        form.save(request)
    except ValidationError:
        messages.error(request,f'O titulo dado já está em uso')
    except ValueError:
        messages.error(request,f'{form.errors}')
    else:
        form.save(request)
        return redirect(rurl)
    user = get_object_or_404(User, pk=request.session.get('user'))
    context={
        'error':True,
        'form':form,
        'usuario':user.username
        }
    return render(request,f'todo/{url}.html',context)
