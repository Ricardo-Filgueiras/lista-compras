import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    name = models.CharField('Nome do Artigo', max_length=200)
    price = models.DecimalField('Preço Unitário', max_digits=10, decimal_places=2)
    category = models.CharField('Categoria', max_length=100, db_index=True)
    stock = models.IntegerField('Estoque', default=0)
    barcode = models.CharField('Código de Barras', max_length=50, blank=True, null=True)
    image_url = models.URLField('URL da Imagem', blank=True, null=True)

    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['name']

    def __str__(self):
        return self.name

class ShoppingList(models.Model):
    STATUS_CHOICES = [
        ('aberta', '🛒 Em Edição (Cliente)'),
        ('fechada', '🔒 Pedido Concluído'),
        ('separacao', '📦 Em Separação'),
        ('pronto', '✅ Pronto para Levantamento'),
        ('entregue', '🏁 Entregue/Finalizado'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    name = models.CharField('Nome da Lista', max_length=200) # Nome amigável
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_lists')
    
    # Campos para Listas Escolares
    student_name = models.CharField('Nome do Estudante', max_length=100, blank=True)
    school = models.CharField('Escola', max_length=200, db_index=True, blank=True)
    grade = models.CharField('Série/Ano', max_length=50, blank=True)
    
    status = models.CharField('Status', max_length=20, choices=STATUS_CHOICES, default='aberta')
    is_template = models.BooleanField('É um Modelo da Loja?', default=False)
    is_locked = models.BooleanField('Concluída (Travada)', default=False)
    
    budget = models.DecimalField('Orçamento', max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lista de Compras'
        verbose_name_plural = 'Listas de Compras'
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_pix_total(self):
        return self.get_total() * Decimal('0.90')

class ShoppingItem(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Fallback/Manual entry fields (Mantendo compatibilidade ou para itens fora do catálogo)
    name = models.CharField('Produto (Manual)', max_length=200, blank=True)
    price = models.DecimalField('Preço unitário', max_digits=10, decimal_places=2, default=0)
    category = models.CharField('Categoria', max_length=100, blank=True, default='Geral')
    
    quantity = models.PositiveIntegerField('Quantidade', default=1)
    is_purchased = models.BooleanField('Comprado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'

    def __str__(self):
        return f"{self.get_item_name()} ({self.shopping_list.name})"

    def get_item_name(self):
        return self.product.name if self.product else self.name

    def get_item_price(self):
        return self.product.price if self.product else self.price

    def get_subtotal(self):
        return self.get_item_price() * self.quantity

class ShoppingShare(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_lists')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_by_me')
    invite_uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    can_edit = models.BooleanField('Pode editar', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Compartilhamento'
        verbose_name_plural = 'Compartilhamentos'
        unique_together = [('shopping_list', 'shared_with')]

    def __str__(self):
        return f'{self.shopping_list.name} → {self.shared_with.username}'

class MonthlyShoppingBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='monthly_budgets')
    period = models.DateField('Período (mês ref.)')
    amount = models.DecimalField('Valor do Orçamento', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Orçamento Mensal'
        verbose_name_plural = 'Orçamentos Mensais'
        unique_together = [('user', 'period')]

    def __str__(self):
        return f'{self.user.username} - {self.period.strftime("%m/%Y")} - R${self.amount}'
