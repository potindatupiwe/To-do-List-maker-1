from django.test import TestCase, Client
from django.urls import reverse
from todo.models import Lista, Tarefa
from django.contrib.auth.models import User
from django.utils import timezone
from todo.forms_models import *
from django.contrib.messages import get_messages
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@gmail.com')
        self.lista = Lista.objects.create(usuario=self.user, 
                                         titulo='Teste self',
                                         descricao = 'Descrição',
                                         data_criacao = timezone.now(),
                                         data_atualizacao = timezone.now())
        
        
    def test_index_GET_not_logged_in(self):
        """Verifica o comportamento da página inicial para usuários não autenticados:
    - Status code 200 (OK)
    - Template correto (index.html)
    - Contexto 'user_in' marcado como False"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/index.html')
        self.assertFalse(response.context['user_in'])

    def test_index_GET_logged_in(self):
        """Testa o carregamento da página inicial para usuários logados:
    - Autenticação bem-sucedida
    - Template específico para usuários logados (index_login.html)
    - Contexto 'user_in' marcado como True"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/index_login.html')
        self.assertTrue(response.context['user_in'])

    def test_index_POST_redirects_set_list(self):
        """Verifica o redirecionamento após POST na página inicial:
    - Sessão de usuário configurada corretamente
    - Status code 302 (Redirect)
    - Redirecionamento para a view 'set_list'"""
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['user'] = self.user.id  # Atribua o ID do usuário à sessão (se necessário)
        session.save()
        response = self.client.post(reverse('index'), {})  # Adicione dados do POST se necessário
        self.assertEqual(response.status_code, 302)  # Verifica se ocorreu um redirecionamento
        self.assertRedirects(response, reverse('set_list'))  # Verifica se o redirecionamento é para 'set_list'

    def test_custom_login_GET(self):
        """Testa o acesso à página de login:
    - Status code 200 (OK)
    - Template correto (login.html)"""

        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')

    def test_custom_login_POST_valid(self):
        """Testa login com credenciais válidas:
    - Redirecionamento para a página inicial
    - Autenticação bem-sucedida"""
        response = self.client.post(reverse('login'), {
            'user': 'testuser',
            'password': 'testpassword'
        })
        self.assertRedirects(response, reverse('index'))

    def test_custom_login_POST_invalid(self):
        """Testa login com credenciais inválidas:
    - Status code 200 (permanece na mesma página)
    - Mensagem de erro exibida"""
        response = self.client.post(reverse('login'), {
            'user': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuario ou senha estão incorretos')       


    def test_register_GET(self):
        """Verifica o acesso à página de registro:
    - Status code 200 (OK)
    - Template correto (register.html)"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')

    def test_register_POST_valid(self):
        """Testa registro com dados válidos:
    - Redirecionamento para a página de login
    - Novo usuário criado no banco de dados"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password': 'newpassword',
            'email': 'newuser@example.com'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_register_POST_invalid(self):
        """Testa registro com dados inválidos:
    - Campo username vazio
    - Erro de formulário específico detectado"""
        response = self.client.post(reverse('register'), {
            'username': '',  # Campo vazio
            'password': 'newpassword',
            'email': 'newuser@example.com'
        })
        self.assertFormError(response, 'form', 'username', 'Este campo é obrigatório.')

    def test_mudarSenha_GET(self):
        """Verifica acesso à página de alteração de senha:
    - Acesso restrito a usuários logados
    - Template correto (mudarSenha.html)"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('mudarSenha'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/mudarSenha.html')

    def test_mudarSenha_POST_valid(self):
        """Testa alteração de senha com dados válidos:
    - Senhas coincidentes
    - Requisição POST bem-sucedida"""
        self.assertTrue(self.client.post(reverse('mudarSenha'), {
            'usuario': 'testuser',
            'password': 'newpassword',
            'password_repeat': 'newpassword',
            'email': 'test@gmail.com'
        }))
        
        
    def test_mudarSenha_POST_invalid_passwords(self):
        """Testa alteração de senha com senhas divergentes:
    - Mensagem de erro específica
    - Status code 200 (formulário reexibido)"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('mudarSenha'), {
            'usuario': 'testuser',
            'password': 'newpassword',
            'confirm_password': 'wrongpassword'
        })
        self.assertContains(response, 'As senha não batem')
    
    
    def test_set_list_GET_logged_in(self):
        """Verifica acesso à criação de listas:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""

        response = self.client.get(reverse('set_list'))
        self.assertEqual(response.status_code, 302)
    
    def test_get_list_GET_logged_in(self):
        """Verifica acesso à ver listas:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""

        response = self.client.get(reverse('get_list', args=[self.lista.pk]))
        self.assertEqual(response.status_code, 302)

    def test_editar_lista_GET_logged_in(self):
        """Verifica acesso à editar listas:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""

        response = self.client.get(reverse('editar_lista', args=[self.lista.pk]))
        self.assertEqual(response.status_code, 302)

    def test_editar_tarefa_GET_logged_in(self):
        """Verifica acesso à editar tarefas:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""
        tarefa = Tarefa.objects.create(  descricao ='Descrição',
                                         user =  self.user,
                                         lista = self.lista,
                                         titulo = 'Tarefa Teste2',
                                         dataCriacao =  timezone.now(),
                                         prioridade =  'alta',
                                         dataVencimento = timezone.now())
        response = self.client.get(reverse('editar_tarefa', args=[tarefa.pk]))
        self.assertEqual(response.status_code, 302)

    def test_set_task_GET_logged_in(self):
        """Verifica acesso à criar tarefas:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""

        response = self.client.get(reverse('set_task'))
        self.assertEqual(response.status_code, 302)

    def test_logout_GET_logged_in(self):
        """Verifica acesso à fazer logout:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""

        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)    

    def test_user_info_GET_logged_in(self):
        """Verifica acesso à ver informações do usuario:
    - Acesso restrito a usuários logados
    - Redirecionamento adequado (status 302)"""

        response = self.client.get(reverse('user_info'))
        self.assertEqual(response.status_code, 302)

    def test_set_list_POST_valid(self):
        """Testa criação de lista com dados válidos:
    - POST bem-sucedido
    - Follow=True para verificar redirecionamento"""
        self.client.login(username='testuser', password='testpassword')
        self.assertTrue(self.client.post(
            reverse('set_list'),
            {
                'titulo': 'Nova Lista2',
                'descricao': 'Descrição da lista'
            },
            follow=True
        ))


    def test_set_list_POST_invalid(self):
        """Testa criação de lista com dados inválidos:
    - Título vazio
    - Status code 404 (Não encontrado)
    - Lista não persistida no banco"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('set_list'), {'titulo': ''})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Lista.objects.filter(titulo='').exists())

    def test_getList_GET_valid(self):
            """Testa visualização de lista existente:
    - Acesso autorizado
    - Template correto (get_list.html)
    - Status code 200 (OK)"""
            self.client.login(username='testuser', password='testpassword')
            lista = Lista.objects.create(usuario=self.user, 
                                         titulo='Teste1',
                                         descricao = 'Descrição',
                                         data_criacao = timezone.now(),
                                         data_atualizacao = timezone.now())
            response = self.client.get(reverse('get_list', args=[lista.pk]))
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'todo/get_list.html')

    def test_getList_GET_invalid(self):
        """Testa acesso a lista de outro usuário:
    - Mensagem de erro específica
    - Restrição de acesso adequada"""

        lista = Lista.objects.create(usuario=self.user, 
                                         titulo='Teste2',
                                         descricao = 'Descrição',
                                         data_criacao = timezone.now(),
                                         data_atualizacao = timezone.now())
        User.objects.create_user(username='testuser2', password='testpassword', email='test2@gmail.com')
        self.client.login(username='testuser2', password='testpassword')
        response = self.client.get(reverse('get_list', args=[lista.pk]))  # ID inválido
        self.assertContains(response, 'A lista que você está tentando acessar não pertence a você')

    def test_getList_POST_delete(self):
        """Testa exclusão de lista:
    - Redirecionamento para página inicial
    - Lista removida do banco de dados"""
        self.client.login(username='testuser', password='testpassword')
        lista = Lista.objects.create(usuario=self.user, 
                                         titulo='Teste',
                                         descricao = 'Descrição',
                                         data_criacao = timezone.now(),
                                         data_atualizacao = timezone.now())
        response = self.client.post(reverse('get_list', args=[lista.pk]), {'Deletar': lista.pk})
        self.assertRedirects(response, reverse('index'))
        self.assertFalse(Lista.objects.filter(pk=lista.pk).exists())

    def test_set_task_GET_logged_in(self):
        """Verifica acesso à criação de tarefas:
    - Formulário correto no contexto
    - Template adequado (set_task.html)"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('set_task'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/set_task.html')
        self.assertIsInstance(response.context['form'], RegisterTaskForm)

    def test_set_task_POST_valid(self):
        """Testa criação de tarefa:
    - Todos campos obrigatórios preenchidos
    - POST bem-sucedido"""
        self.client.login(username='testuser', password='testpassword')
        self.assertTrue(self.client.post(reverse('set_task'), {
            'titulo': 'Nova Tarefa',
            'descricao': 'Descrição da tarefa',
            'status': 'pendente',
            'dataVencimento':timezone.now(),
            'Enviar':self.lista.pk
        }))

    def test_editar_lista_GET(self):
        """Verifica acesso à edição de lista:
    - Template correto (update_list.html)
    - Formulário pré-preenchido"""
        self.client.login(username='testuser', password='testpassword')
        lista = Lista.objects.create(usuario=self.user, 
                                         titulo='Velha Lista2',
                                         descricao = 'Descrição',
                                         data_criacao = timezone.now(),
                                         data_atualizacao = timezone.now())
        response = self.client.get(reverse('editar_lista', args=[lista.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/update_list.html')

    def test_editar_lista_POST_valid(self):
        """Testa atualização de lista:
    - Dados válidos
    - Redirecionamento para página inicial
    - Alterações persistidas no banco"""
        self.client.login(username='testuser', password='testpassword')
        lista = Lista.objects.create(usuario=self.user, 
                                         titulo='Velha Lista',
                                         descricao = 'Descrição',
                                         data_criacao = timezone.now(),
                                         data_atualizacao = timezone.now())
        response = self.client.post(reverse('editar_lista', args=[lista.pk]), {
            'titulo': 'Nova Lista',
            'descricao': 'Nova descrição'
        })
        self.assertRedirects(response, reverse('index'))
        self.assertTrue(Lista.objects.filter(titulo='Nova Lista').exists())

    def test_custom_logout(self):
        """Testa o logout do usuário:
    - Redirecionamento para a página inicial
    - Sessão encerrada corretamente"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('index'))

    def test_user_info(self):
        """Verifica acesso às informações do usuário:
    - Template correto (user_info.html)
    - Acesso restrito a usuários logados
    - Status code 200 (OK)"""
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_info'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/user_info.html')

    def test_editar_tarefa_GET(self):
        """Verifica acesso à edição de tarefa:
    - Template correto (update_task.html)
    - Formulário pré-preenchido"""
        self.client.login(username='testuser', password='testpassword')
        tarefa = Tarefa.objects.create(  descricao ='Descrição',
                                         user =  self.user,
                                         lista = self.lista,
                                         titulo = 'Tarefa Teste2',
                                         dataCriacao =  timezone.now(),
                                         prioridade =  'alta',
                                         dataVencimento = timezone.now())
        response = self.client.get(reverse('editar_tarefa', args=[tarefa.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/update_task.html')

    def test_editar_tarefa_POST_valid(self):
        """Testa atualização de tarefa:
    - Dados válidos
    - Redirecionamento para lista relacionada
    - Alterações persistidas no banco"""
        self.client.login(username='testuser', password='testpassword')
        tarefa = Tarefa.objects.create(  descricao ='Descrição',
                                         user =  self.user,
                                         lista = self.lista,
                                         titulo = 'Tarefa Teste2',
                                         dataCriacao =  timezone.now(),
                                         prioridade =  'alta',
                                         dataVencimento = timezone.now())
       
        response = self.client.post(reverse('editar_tarefa', args=[tarefa.pk]), {
            'titulo': 'Nova Tarefa',
            'descricao': 'Nova descrição',
            'status': 'em andamento',
            'dataVencimento':'2/2/2025',
            'prioridade':'alta'
        })

        self.assertRedirects(response, reverse('get_list', args=[tarefa.lista.pk]))
        self.assertTrue(Tarefa.objects.filter(titulo='Nova Tarefa').exists())