import uuid
from django.db import models
from django.contrib.auth.models import User


class ShoppingList(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    name = models.CharField('Nome', max_length=200)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shopping_lists')
    budget = models.DecimalField('Orçamento', max_digits=10, decimal_places=2, null=True, blank=True)
    is_locked = models.BooleanField('Concluída (Travada)', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Lista de Compras'
        verbose_name_plural = 'Listas de Compras'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ShoppingItem(models.Model):
    UNIT_CHOICES = [
        ('un', 'Unidade'),
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('L', 'Litro'),
        ('ml', 'Mililitro'),
        ('cx', 'Caixa'),
        ('pct', 'Pacote'),
        ('dz', 'Dúzia'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='items')
    name = models.CharField('Produto', max_length=200)
    quantity_value = models.DecimalField('Quantidade', max_digits=10, decimal_places=3, default=1)
    unit = models.CharField('Unidade', max_length=10, choices=UNIT_CHOICES, default='un')
    price = models.DecimalField('Preço unitário', max_digits=10, decimal_places=2, default=0)
    category = models.CharField('Categoria', max_length=100, blank=True, default='Geral')
    is_purchased = models.BooleanField('Comprado', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Itens'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.shopping_list.name})'

    @property
    def total_price(self):
        return self.quantity_value * self.price


class ShoppingShare(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE, related_name='shares')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_lists')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_by_me')
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
