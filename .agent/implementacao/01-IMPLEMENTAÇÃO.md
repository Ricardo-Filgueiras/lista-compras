01 - Arquitetura de Dados e Estrutura de Permissões

1. Objetivo do Painel Administrativo (Lojista)

O objetivo central do Painel Administrativo é transformar a "intenção de compra" do cliente em uma "operação logística" eficiente. Ele permite que o lojista:

Gerencie o Ciclo de Vida do Pedido: Monitore listas desde a criação até a entrega final.

Controle o Fluxo de Separação (Picking): Organize a retirada física dos produtos no estoque.

Alimente o Catálogo de Forma Massiva: Utilize ferramentas de automação (CSV) para manter preços e estoques atualizados sem esforço manual unitário.

Crie Inteligência de Vendas: Identifique quais escolas e séries estão gerando mais demanda.

2. Requisitos Técnicos Detalhados

2.1 Autenticação e Níveis de Acesso

Utilizaremos o sistema nativo do Django (django.contrib.auth), baseando a separação de permissões no atributo is_staff.

Superusuário (Dono): Único com acesso ao /admin/ nativo do Django para criar contas de funcionários.

Staff (Funcionário/Lojista): Acesso ao Painel Gerencial personalizado (/dashboard/admin/). Não pode criar sua própria conta; deve ser cadastrado pelo Superusuário.

Usuário Comum (Cliente): Acesso apenas ao seu próprio painel de listas.

2.2 Tecnologias Envolvidas

Backend: Django 4.2+ (Python 3.10+).

Banco de Dados: PostgreSQL (Recomendado para produção) ou SQLite (Desenvolvimento).

Frontend Interativo: HTMX (para atualizações de status sem reload de página).

Estilização: Tailwind CSS (Slate Palette).

3. Modelagem de Dados (ERD)

Abaixo, a estrutura de classes que deve ser implementada no arquivo models.py.

3.1 Model: Produto

Armazena o catálogo mestre da papelaria.

class Produto(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome do Artigo")
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    categoria = models.CharField(max_length=100, db_index=True) # Ex: Cadernos, Escrita
    estoque = models.IntegerField(default=0)
    codigo_barras = models.CharField(max_length=50, blank=True, null=True)
    imagem_url = models.URLField(blank=True, null=True) # URL para foto do produto

    def __str__(self):
        return self.nome


3.2 Model: ListaEscolar

O coração do sistema. Funciona como um "Carrinho de Compras Permanente" que evolui para um "Pedido".

import uuid

class ListaEscolar(models.Model):
    STATUS_CHOICES = [
        ('aberta', '🛒 Em Edição (Cliente)'),
        ('fechada', '🔒 Pedido Concluído'),
        ('separacao', '📦 Em Separação'),
        ('pronto', '✅ Pronto para Levantamento'),
        ('entregue', '🏁 Entregue/Finalizado'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="minhas_listas")
    nome_estudante = models.CharField(max_length=100)
    escola = models.CharField(max_length=200, db_index=True)
    serie = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    is_template = models.BooleanField(default=False, verbose_name="É um Modelo da Loja?")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.itens.all())


3.3 Model: ItemLista

Tabela de ligação que permite quantidades específicas de cada produto em uma lista.

class ItemLista(models.Model):
    lista = models.ForeignKey(ListaEscolar, related_name='itens', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.produto.preco * self.quantidade


4. Lógica de Roteamento (Gatekeeper)

Para garantir que o Admin e o Cliente caiam nos lugares certos após o login, implementaremos uma View de redirecionamento no views.py:

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_by_role(request):
    """Encaminha o usuário baseando-se no seu nível de permissão."""
    if request.user.is_staff:
        return redirect('admin_dashboard') # Rota a ser criada no arquivo 02
    return redirect('client_dashboard') # Rota do painel do pai/mãe
