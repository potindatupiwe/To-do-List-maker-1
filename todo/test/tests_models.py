from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Lista, Tarefa
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
class ListaModelTest(TestCase):
    """Testes para o modelo Lista"""
    
    def setUp(self):
        """Configura dados de teste comuns para todos os testes de Lista"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.lista_data = {
            'usuario': self.user,
            'descricao': 'Descrição teste',
            'titulo': 'Lista Teste',
            'data_criacao': timezone.now(),
            'data_atualizacao': timezone.now()
        }

    # --- Testes de Campos ---
    def test_campo_titulo_max_length(self):
        """Verifica o comprimento máximo permitido para o campo título"""
        lista = Lista(**self.lista_data)
        max_length = lista._meta.get_field('titulo').max_length
        self.assertEqual(max_length, 100)

    def test_campo_descricao_max_length(self):
        """Verifica o comprimento máximo permitido para o campo descrição"""
        lista = Lista(**self.lista_data)
        max_length = lista._meta.get_field('descricao').max_length
        self.assertEqual(max_length, 300)

    # --- Teste de Representação String ---
    def test_representacao_string_sucesso(self):
        """Verifica a representação em string do modelo"""
        lista = Lista.objects.create(**self.lista_data)
        self.assertEqual(str(lista), self.lista_data['titulo'])

    # --- Testes de Relacionamentos ---
    def test_relacionamento_usuario_cascade(self):
        """Testa o comportamento de cascata ao excluir o usuário relacionado"""
        lista = Lista.objects.create(**self.lista_data)
        self.user.delete()
        self.assertFalse(Lista.objects.filter(pk=lista.pk).exists())

    # --- Testes de Validação ---
    def test_validacao_titulo_duplicado_mesmo_usuario(self):
        """Impede a criação de listas com títulos duplicados para o mesmo usuário"""
        Lista.objects.create(**self.lista_data)
        with self.assertRaises(ValidationError):
            lista = Lista(**self.lista_data)
            lista.full_clean()

    def test_data_atualizacao(self):
        """Garante que o campo data_atualizacao só aceite valores datetime válidos"""
        lista = Lista(**self.lista_data)
        lista.data_atualizacao = 'Valor inválido'
        with self.assertRaises(ValidationError):
            lista.full_clean()

    def test_data_criacao(self):
        """Garante que o campo data_criacao só aceite valores datetime válidos"""
        lista = Lista(**self.lista_data)
        lista.data_criacao = 'Valor inválido'
        with self.assertRaises(ValidationError):
            lista.full_clean()

class TarefaModelTest(TestCase):
    """Testes para o modelo Tarefa"""
    
    def setUp(self):
        """Configura dados de teste comuns para todos os testes de Tarefa"""
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.lista = Lista.objects.create(
            usuario=self.user,
            titulo='Lista Teste',
            descricao='Descrição',
            data_criacao=timezone.now(),
            data_atualizacao=timezone.now()
        )
        self.tarefa_data = {
            'user': self.user,
            'lista': self.lista,
            'titulo': 'Tarefa Teste',
            'dataCriacao': timezone.now(),
            'prioridade': 'alta',
            'descricao': 'Descrição',
            'dataVencimento': timezone.now()
        }

    # --- Testes de Campos ---
    def test_campo_descricao_pode_ser_nulo(self):
        """Verifica se o campo descrição é obrigatório"""
        tarefa = Tarefa(
            user=self.user,
            lista=self.lista,
            titulo='Tarefa Teste2',
            dataCriacao=timezone.now(),
            prioridade='alta',
            dataVencimento=timezone.now())
        with self.assertRaises(ValidationError):
            tarefa.full_clean()

    def test_campo_dataConclusao_pode_ser_nulo(self):
        """Garante que dataConclusao pode permanecer nulo"""
        tarefa = Tarefa.objects.create(**self.tarefa_data)
        self.assertIsNone(tarefa.dataConclusao)

    # --- Teste de Representação String ---
    def test_representacao_string_combinacao(self):
        """Verifica o formato da representação em string da tarefa"""
        tarefa = Tarefa.objects.create(**self.tarefa_data)
        expected_str = f"{self.tarefa_data['titulo']}{self.user.username}"
        self.assertEqual(str(tarefa), expected_str)

    # --- Testes de Relacionamentos ---
    def test_relacionamento_lista_cascade(self):
        """Testa o comportamento de cascata ao excluir a lista relacionada"""
        tarefa = Tarefa.objects.create(**self.tarefa_data)
        self.lista.delete()
        self.assertFalse(Tarefa.objects.filter(pk=tarefa.pk).exists())

    # --- Testes de Métodos do Modelo ---
    def test_save_chama_full_clean(self):
        """Garante que o método save() chama a validação completa"""
        with self.assertRaises(TypeError):
            tarefa = Tarefa(user=self.user, lista=self.lista)
            tarefa.save()

    def test_delete_atualiza_relacionamentos(self):
        """Verifica a exclusão correta de uma tarefa"""
        tarefa = Tarefa.objects.create(**self.tarefa_data)
        tarefa_pk = tarefa.pk
        tarefa.delete()
        self.assertFalse(Tarefa.objects.filter(pk=tarefa_pk).exists())

    # --- Testes de Constraints ---
    def test_constraint_unica_tarefa_usuario(self):
        """Impede tarefas duplicadas para o mesmo usuário"""
        Tarefa.objects.create(**self.tarefa_data)
        with self.assertRaises(ValidationError):
            tarefa = Tarefa(**self.tarefa_data)
            tarefa.full_clean()

    def test_constraint_unica_lista_usuario(self):
        """Impede listas duplicadas para o mesmo usuário"""
        Lista.objects.create(
            usuario=self.user,
            titulo='Lista Duplicada',
            descricao='Descrição',
            data_criacao=timezone.now(),
            data_atualizacao=timezone.now()
        )
        with self.assertRaises(ValidationError):
            lista = Lista(
                usuario=self.user,
                titulo='Lista Duplicada',
                descricao='Outra descrição',
                data_criacao=timezone.now(),
                data_atualizacao=timezone.now()
            )
            lista.full_clean()

    def test_data_vencimento(self):
        """Garante que dataVencimento só aceite valores datetime válidos"""
        tarefa = Tarefa(**self.tarefa_data)
        tarefa.dataVencimento = 'Valor inválido'
        with self.assertRaises(TypeError):
            tarefa.full_clean()

    def test_data_vencimento_menor_que_hoje(self):
        """ Verifica se a dataVencimento é menor que a data atual """
        tarefa = {
            'user': self.user,
            'lista': self.lista,
            'titulo': 'Tarefa Teste',
            'dataCriacao': timezone.now(),
            'prioridade': 'alta',
            'descricao': 'Descrição',
            'dataVencimento': timezone.now()-datetime.timedelta(days=1)
        }
        tarefa_data = Tarefa(**tarefa)
        with self.assertRaises(ValidationError):
            tarefa_data.full_clean()

class ModelsUserTest(TestCase):
    """Testes adicionais para o modelo User"""
    
    def setUp(self):
        """Configura usuário de teste"""
        self.user = User.objects.create_user(
            username='italo3', 
            password='123',
            email='email.example@gmail.com'
        )
    
    def test_username_igual(self):
        """Impede a criação de usuários com username duplicado"""
        novo_user = User(
            username='italo3', 
            password='123',
            email='email.example@gmail.com'
        )
        with self.assertRaises(ValidationError):
            novo_user.full_clean()

    def test_on_CASCADE(self):
        """Verifica o comportamento de cascata ao excluir usuário"""
        Lista.objects.create(
            usuario=self.user,
            titulo='titulo',
            descricao='descrição',
            data_atualizacao=timezone.now(),
            data_criacao=timezone.now()
        )
        self.user.delete()
        self.assertEqual(Lista.objects.count(), 0)