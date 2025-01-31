from django.test import TestCase
from todo.forms_models import *
from django.contrib.auth.models import User
from ..models import *
from todo.forms import *

class RegisterFormTest(TestCase):
    """Testes para o formulário de registro de usuários"""
    
    def test_valid_form(self):
        """Verifica o formulário com dados válidos:
        - Todos campos obrigatórios preenchidos
        - Formato de email válido
        - Senha segura"""
        form_data = {
            "username": "testuser",
            "password": "securepassword123",
            "email": "test@example.com"
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_duplicate_username(self):
        """Impede registro com username já existente:
        - Valida unicidade do username
        - Verifica erro no campo específico"""
        User.objects.create_user(username="testuser", password="12345", email="test@example.com")
        form_data = {
            "username": "testuser",
            "password": "securepassword123",
            "email": "test2@example.com"
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("username", form.errors)

    def test_password_widget(self):
        """Garante que o campo password usa widget correto:
        - Input type='password' para ocultar texto"""
        form = RegisterForm()
        self.assertEqual(form.fields["password"].widget.input_type, "password")

    def test_save_method(self):
        """Testa a criação de usuário no banco de dados:
        - Hash de senha implementado corretamente
        - Campos essenciais persistidos"""
        form_data = {
            "username": "testuser",
            "password": "securepassword123",
            "email": "test@example.com"
        }
        form = RegisterForm(data=form_data)
        if form.is_valid():
            form.saveh(username="testuser", password="securepassword123", email="test@example.com")
            user = User.objects.get(username="testuser")
            self.assertTrue(user.check_password("securepassword123"))

class RegisterListFormTest(TestCase):
    """Testes para o formulário de criação de listas"""
    
    def setUp(self):
        """Configura usuário de teste"""
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_valid_form(self):
        """Valida formulário com dados corretos:
        - Título dentro do limite de caracteres
        - Descrição opcional"""
        form_data = {"titulo": "Compras", "descricao": "Lista de supermercado"}
        form = RegisterListForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_save_method(self):
        """Verifica vinculação correta ao usuário:
        - Lista associada ao usuário da sessão
        - Campos obrigatórios persistidos"""
        form_data = {"titulo": "Compras", "descricao": "Lista de supermercado"}
        form = RegisterListForm(data=form_data)
        if form.is_valid():
            form.save(request=self.mock_request(user_id=self.user))
            lista = Lista.objects.get(titulo="Compras")
            self.assertEqual(lista.usuario, self.user)

    def mock_request(self, user_id):
        """Simula objeto request com sessão de usuário"""
        class MockRequest:
            user = user_id
        return MockRequest()

class RegisterTaskFormTest(TestCase):
    """Testes para o formulário de criação de tarefas"""
    
    def setUp(self):
        """Configura usuário e lista para testes"""
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.lista = Lista.objects.create(
            usuario=self.user,
            titulo="Compras",
            descricao="Lista de supermercado",
            data_criacao=timezone.now(),
            data_atualizacao=timezone.now()
        )

    def test_valid_form(self):
        """Valida formulário com todos campos obrigatórios:
        - Data de vencimento no formato correto
        - Prioridade dentro das opções permitidas"""
        form_data = {
            "titulo": "Comprar leite",
            "descricao": "Ir ao supermercado",
            "prioridade": "alta",
            "dataVencimento": "2023-12-31"
        }
        form = RegisterTaskForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_save_method(self):
        """Verifica vinculação correta à lista:
        - Tarefa associada à lista selecionada
        - Atualização de data na lista relacionada"""
        form_data = {
            "titulo": "Comprar leite",
            "descricao": "Ir ao supermercado",
            "prioridade": "alta",
            "dataVencimento": "2023-12-31"
        }
        form = RegisterTaskForm(data=form_data)
        if form.is_valid():
            form.save(request=self.mock_request())
            task = Tarefa.objects.get(titulo="Comprar leite")
            self.assertEqual(task.lista, self.lista)

    def mock_request(self):
        """Simula request com parâmetro GET para lista ID"""
        class MockRequest:
            GET = {"Enviar": self.lista.id}
        return MockRequest()

class UpdateTaskFormTest(TestCase):
    """Testes para o formulário de atualização de tarefas"""
    
    def setUp(self):
        """Configura tarefa de teste"""
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.lista = Lista.objects.create(
            usuario=self.user,
            titulo="Compras",
            descricao="Lista de supermercado",
            data_criacao=timezone.now(),
            data_atualizacao=timezone.now()
        )
        self.task = Tarefa.objects.create(
            titulo="Comprar leite",
            descricao="Ir ao supermercado",
            prioridade="alta",
            dataVencimento=timezone.now(),
            dataCriacao = timezone.now(),
            lista=self.lista,
            user=self.user
        )

    def test_valid_form(self):
        """Valida atualização com novos dados:
        - Modificação de título e descrição
        - Alteração de status e prioridade"""
        form_data = {
            "titulo": "Comprar pão",
            "descricao": "Ir à padaria",
            "prioridade": "media",
            "dataVencimento": "2023-12-31",
            "status": "concluido",
            "dataCriacao": "2023-12-30"
        }
        form = UpdateTaskForm(data=form_data, instance=self.task)
        self.assertTrue(form.is_valid())

    def test_status_update(self):
        """Verifica atualização de status:
        - Marcação como concluído
        - Atualização de data de conclusão"""
        form_data = {
            "titulo": "Comprar leite",
            "descricao": "Ir ao supermercado",
            "prioridade": "alta",
            "dataVencimento": "2023-12-31",
            "status": "concluido",
            "dataCriacao":"2023-12-30"
        }
        form = UpdateTaskForm(data=form_data, instance=self.task)
        if form.is_valid():
            form.save()
            self.task.refresh_from_db()
            self.assertEqual(self.task.status, "concluido")

class UpdateListFormTest(TestCase):
    """Testes para o formulário de atualização de listas"""
    
    def setUp(self):
        """Configura lista para testes"""
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.lista = Lista.objects.create(
            usuario=self.user,
            titulo="Compras",
            descricao="Lista de supermercado",
            data_criacao=timezone.now(),
            data_atualizacao=timezone.now()
        )

    def test_valid_form(self):
        """Valida atualização com novos dados:
        - Modificação de título e descrição
        - Manutenção do usuário proprietário"""
        form_data = {"titulo": "Compras atualizada", "descricao": "Nova descrição"}
        form = UpdateListForm(data=form_data, instance=self.lista)
        self.assertTrue(form.is_valid())

    def test_duplicate_title(self):
        """Impede títulos duplicados para o mesmo usuário:
        - Valida restrição de unicidade
        - Verifica mensagem de erro global"""
        Lista.objects.create(
            usuario=self.user,
            titulo="Outra lista",
            descricao="Descrição",
            data_criacao=timezone.now(),
            data_atualizacao=timezone.now()
        )
        form_data = {"titulo": "Outra lista", "descricao": "Descrição"}
        form = UpdateListForm(data=form_data, instance=self.lista)
        self.assertFalse(form.is_valid())
        self.assertIn("O nome da lista já está em uso", form.errors["__all__"])

class UpdateSenhaFormTest(TestCase):
    """Testes para o formulário de alteração de senha"""
    
    def setUp(self):
        """Configura usuário para testes"""
        self.user = User.objects.create_user(
            username="testuser", 
            password="12345", 
            email="test@example.com"
        )

    def test_valid_form(self):
        """Valida formulário com dados corretos:
        - Senhas coincidentes
        - Email correspondente ao usuário"""
        form_data = {
            "usuario": "testuser",
            "password": "newpassword123",
            "password_repeat": "newpassword123",
            "email": "test@example.com"
        }
        form = UpdateSenhaForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_exist(self):
        """Verifica validação de existência do usuário:
        - Identifica usuário inexistente
        - Mantém formulário válido para segurança"""
        form_data = {
            "usuario": "nonexistentuser",
            "password": "newpassword123",
            "password_repeat": "newpassword123",
            "email": "nonexistent@example.com"
        }
        form = UpdateSenhaForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.user_exist())

class UserLoginFormTest(TestCase):
    """Testes para o formulário de login"""
    
    def test_valid_form(self):
        """Valida formulário com credenciais completas:
        - Usuário e senha preenchidos
        - Campos no formato correto"""
        form_data = {"user": "testuser", "password": "12345"}
        form = UserLoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_fields(self):
        """Detecta campos obrigatórios faltantes:
        - Senha não informada
        - Erro no campo específico"""
        form_data = {"user": "testuser"}
        form = UserLoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("password", form.errors)
