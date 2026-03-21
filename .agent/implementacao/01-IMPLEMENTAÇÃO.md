# 01 - Arquitetura de Dados e Estrutura de Permissões

## 1. Modelagem de Dados (models.py)

Abaixo, a estrutura técnica detalhada para implementação, seguindo as definições da `ARQUITETURA.md`.

### 1.1 Model: Product (Catálogo Mestre)
```python
class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nome do Artigo")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço Unitário")
    category = models.CharField(max_length=100, db_index=True) # Ex: Cadernos, Escrita
    stock = models.IntegerField(default=0)
    barcode = models.CharField(max_length=50, blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
```

### 1.2 Model: ShoppingList (Pedido/Template)
```python
class ShoppingList(models.Model):
    STATUS_CHOICES = [
        ('aberta', '🛒 Em Edição (Cliente)'),
        ('fechada', '🔒 Pedido Concluído'),
        ('separacao', '📦 Em Separação'),
        ('pronto', '✅ Pronto para Levantamento'),
        ('entregue', '🏁 Entregue/Finalizado'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shopping_lists")
    student_name = models.CharField(max_length=100, blank=True)
    school = models.CharField(max_length=200, db_index=True, blank=True)
    grade = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberta')
    is_template = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False) # Trava de edição (Checkout)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self):
        return sum(item.get_subtotal() for item in self.items.all())

    def get_pix_total(self):
        return self.get_total() * Decimal('0.90') # 10% Desconto PIX
```

### 1.3 Model: ShoppingItem
```python
class ShoppingItem(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def get_subtotal(self):
        return self.product.price * self.quantity
```

### 1.4 Model: ShoppingShare (Colaboração)
```python
class ShoppingShare(models.Model):
    shopping_list = models.ForeignKey(ShoppingList, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE)
    invite_uuid = models.UUIDField(default=uuid.uuid4, editable=False) # Para links /entrar/
```

## 2. Roteamento Técnico (Gatekeeper)

```python
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

@login_required
def redirect_by_role(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    return redirect('client_dashboard')
```

## 3. URLs Encurtadas e Identificadores
- Utilização de `UUID` truncado ou `ShortUUID` para URLs de templates, facilitando a geração de QR Codes de baixa densidade.
- Endpoint de validação: `/v/<short_id>/` redireciona para `/compras/<uuid>/usar-template/`.
