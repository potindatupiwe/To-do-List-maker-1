from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login',views.custom_login, name='login'),
    path('register', views.register, name='register'),
    path('mudarSenha', views.mudarSenha, name='mudarSenha'),
    
    
    # Urls protegidas
    path('logout',views.custom_logout, name='logout'),
    path('user_inf',views.user_info,name='user_info'),
    path('set_list',views.set_list, name='set_list'),
    path('get_list/<int:pk>', views.getList, name='get_list'),
    path('set_task',views.set_task, name='set_task'),
    path('editar_lista/<int:pk>', views.editar_lista, name='editar_lista'),
    path('editar_tarefa/<int:pk>', views.editar_tarefa, name='editar_tarefa')
]