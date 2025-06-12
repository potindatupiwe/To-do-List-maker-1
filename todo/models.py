from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
import datetime
#VALIDATORS(só pode salvar a tarefa se não existir outra tarefa com o mesmo titulo feita pelo mesmo usuario, a mesma coisa pras listas)

class Lista(models.Model):
    # Referência ao usuário dono da lista.
    usuario = models.ForeignKey(User, models.CASCADE, related_name='lista')
    # Descrição detalhada da lista.
    descricao = models.CharField(max_length=300, null=False)
    # Título da lista, usado como identificador principal.
    titulo = models.CharField(max_length=100, null=False)
    # Data de criação da lista.
    data_criacao = models.DateTimeField('date published', null=False)
    # Data da última atualização da lista.
    data_atualizacao = models.DateTimeField('date update', null=False)

    def __str__(self):
        """
        Retorna uma representação em string do objeto Lista, utilizando o título.
        """
        return self.titulo
    
    def clean(self):
        """
        Validação personalizada para garantir que não existam listas com o mesmo título para o mesmo usuário.
        Levanta um ValidationError se a condição for violada.
        """
        super().clean()
        try:
             Lista.objects.exclude(pk=self.pk).get(titulo=self.titulo, usuario=self.usuario)
        except:
            pass
        else:
            raise ValidationError('O nome da lista já está em uso')

    def save(self, *args, **kwargs):
        """
        Salva o objeto Lista no banco de dados após realizar as validações definidas em clean.
        """
        self.full_clean()
        super().save(*args, **kwargs)

    
class Tarefa(models.Model):
    # Opções para o status da tarefa.
    STATUS = (
        ('concluido','concluido'), ('em andamento','em andamento'), ('pendente','pendente')
        )
    # Opções para a prioridade da tarefa.
    PRIORIDADE = (('alta','alta'), ('media','media'), ('baixa','baixa'))
    # Título da tarefa, usado como identificador principal.
    titulo = models.CharField(max_length=100, null=False)
    # Descrição detalhada da tarefa (opcional).
    descricao = models.CharField(max_length=300, null=True)
     # Data de criação da tarefa.
    dataCriacao = models.DateField('date published', null=False)
    # Data de conclusão da tarefa (opcional),só é colocada quando o usuario coloca o status para concluido.
    dataConclusao = models.DateField('date con', null=True, blank=True)
    # Indica se a tarefa está concluída.
    concluido = models.BooleanField(default=False, null=False)
    # Status atual da tarefa.
    status = models.CharField(max_length=20, choices=STATUS, null=True, default='pendente')
    # Nível de prioridade da tarefa.
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE, null=True)
    # Data de vencimento da tarefa (opcional).
    dataVencimento = models.DateField('date final', null=True)
    # Referência à lista associada à tarefa.
    lista = models.ForeignKey(Lista, on_delete=models.CASCADE, null=False)
    # Referência ao usuário dono da tarefa.
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    def __str__(self):
        """
        Retorna uma representação em string do objeto Tarefa, combinando o título da tarefa com o título da lista associada.
        """
        return self.titulo+self.user.username
    
    def clean(self):
        """
        Validação personalizada para garantir que não existam tarefas com o mesmo título para o mesmo usuário.
        Levanta um ValidationError se a condição for violada.
        """
        super().clean()
        try:
            Tarefa.objects.exclude(pk=self.pk).get(titulo=self.titulo, user=self.user)
        except:
            pass
        else:
            raise ValidationError('O nome da tarefa já está em uso')
        
        if self.dataVencimento<datetime.date.today():
            raise ValidationError('Informe uma data de vencimento válida')
        
    def save(self, *args, **kwargs):
        """
        Salva o objeto Tarefa no banco de dados após realizar as validações definidas em clean.
        """
        self.full_clean()
        super().save(*args, **kwargs)


# Comandos SQL para testes CRUD na base de dados:

# Inserção de usuários na tabela User:
# A senha é criptografada
# INSERT INTO auth_user (username, password, email) VALUES ('usuario1', 'senha1', 'email1@example.com');
# INSERT INTO auth_user (username, password, email) VALUES ('usuario2', 'senha2', 'email2@example.com');

# Inserção de listas na tabela Lista:
# INSERT INTO todo_lista (usuario_id, descricao, titulo, data_criacao, data_atualizacao) 
# VALUES (1, 'Lista de compras', 'Compras', '2023-01-01 10:00:00', '2023-01-01 10:00:00');
# INSERT INTO todo_lista (usuario_id, descricao, titulo, data_criacao, data_atualizacao) 
# VALUES (2, 'Lista de tarefas', 'Trabalho', '2023-01-02 11:00:00', '2023-01-02 11:00:00');

# Inserção de tarefas na tabela Tarefa:
# INSERT INTO todo_tarefa (titulo, descricao, dataCriacao, dataConclusao, concluido, status, prioridade, dataVencimento, lista_id, user_id) 
# VALUES ('Comprar leite', 'Ir ao supermercado para comprar leite', '2023-01-01', NULL, FALSE, 'pendente', 'media', '2023-01-02', 1, 1);
# INSERT INTO todo_tarefa (titulo, descricao, dataCriacao, dataConclusao, concluido, status, prioridade, dataVencimento, lista_id, user_id) 
# VALUES ('Enviar relatório', 'Finalizar e enviar o relatório mensal', '2023-01-02', '2023-01-03', TRUE, 'concluido', 'alta', '2023-01-02', 2, 2);

# Consulta para listar todas as listas de um usuário:
# SELECT * FROM todo_lista WHERE usuario_id = 1;

# Consulta para listar todas as tarefas de uma lista específica:
# SELECT * FROM todo_tarefa WHERE lista_id = 1;

# Atualização do status de uma tarefa:
# UPDATE todo_tarefa SET status = 'concluido', concluido = TRUE WHERE id = 1;

# Exclusão de uma tarefa:
# DELETE FROM todo_tarefa WHERE id = 1;

