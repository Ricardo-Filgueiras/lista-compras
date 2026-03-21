# 03 - Automação CSV e Gestão de Catálogo (Templates)

## 1. Importação em Massa (CSV)

O arquivo `.csv` deve seguir o cabeçalho:
`name,price,category,stock,barcode,image_url`

```python
import csv
import io
from django.contrib import messages
from .models import Product

@staff_member_required
def import_products_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Pular header

        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            Product.objects.update_or_create(
                name=row[0],
                defaults={
                    'price': row[1],
                    'category': row[2],
                    'stock': row[3],
                    'barcode': row[4],
                    'image_url': row[5],
                }
            )
        messages.success(request, 'Catálogo atualizado com sucesso!')
        return redirect('admin_catalogo')
```

## 2. Mecanismo de Clonagem (Copy-on-Write)

Implementação da rota `/usar-template/[UUID]/` para criação de cópias exclusivas.

```python
@login_required
def clone_template(request, uuid):
    template = get_object_or_404(ShoppingList, uuid=uuid, is_template=True)
    
    # Nova lista baseada no template
    nova_lista = ShoppingList.objects.create(
        user=request.user,
        school=template.school,
        grade=template.grade,
        status='aberta'
    )
    
    # Clonagem profunda dos itens
    for item in template.items.all():
        ShoppingItem.objects.create(
            shopping_list=nova_lista,
            product=item.product,
            quantity=item.quantity
        )
    
    messages.success(request, f'Template "{template.school}" clonado com sucesso!')
    return redirect('client_dashboard')
```

## 3. Gestão de Templates Públicos
- **Check-box "Tornar Template Público":** Define `is_template=True` e `is_locked=True`.
- **Geração de QR Code:** Vinculado à URL `/v/<short_id>/` (encurtada).
- **Interface de Impressão:** Grid de templates ativos com botões para impressão de etiquetas (80mm).