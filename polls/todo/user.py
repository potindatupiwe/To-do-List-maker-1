from .models import *
from django.utils import timezone
import datetime
from django.contrib.auth import logout
from django.contrib import messages

def auto_logout_after_one_hour(view_func):
    def wrapper(request,*args, **kwargs):
        if request.user.is_authenticated:
            if timeout(request.user):
                logout(request)
                messages.info(request,'Seu login expirou')
        return view_func(request,*args, **kwargs)
    return wrapper

def timeout(user: User):
    return user.last_login+datetime.timedelta(minutes=60)<=timezone.now()

    
def custom_logout_timeout(request):
        try:
            user=User.objects.get(pk = request.user.pk)
        except:
            return False
        else:
            if timeout(user):
                return False
            else:
                return True


