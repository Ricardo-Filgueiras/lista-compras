# 02 - Dashboard Administrativo (Interface do Lojista)

## 1. Organização de Templates
```
templates/
  ├── base.html              # Layout base comum (Slate Palette)
  └── staff/                 # Exclusivo da papelaria
       ├── dashboard.html    # Pipeline de pedidos (Trello Style)
       ├── detail.html       # Picking List Digital
       └── components/       
            └── shoppinglist_row.html # Fragmento HTMX
```

## 2. Views Administrativas (views.py)

```python
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import ShoppingList

@staff_member_required
def admin_dashboard(request):
    """Pipeline de pedidos agrupados por status."""
    listas = ShoppingList.objects.filter(is_template=False).order_by('-created_at')
    
    context = {
        'listas_fechadas': listas.filter(status='fechada'),
        'listas_separacao': listas.filter(status='separacao'),
        'listas_prontas': listas.filter(status='pronto'),
    }
    return render(request, 'staff/dashboard.html', context)

@staff_member_required
def update_status_htmx(request, uuid):
    """Atualização de status via HTMX (Trigger: click)."""
    lista = get_object_or_404(ShoppingList, uuid=uuid)
    novo_status = request.POST.get('status')
    
    if novo_status in dict(ShoppingList.STATUS_CHOICES):
        lista.status = novo_status
        lista.save()
        
    return render(request, 'staff/components/shoppinglist_row.html', {'lista': lista})
```

## 3. UX do Dashboard (Staff)

### 3.1 Pipeline Visual
- **Colunas Dinâmicas:** Implementação de 3 colunas principais (Fechada, Separação, Pronta).
- **Cartões de Lista:** Devem exibir `student_name`, `school` e o total de itens.

### 3.2 Interações HTMX
```html
<button 
    hx-post="{% url 'update_status_htmx' lista.uuid %}" 
    hx-vals='{"status": "separacao"}'
    hx-target="#lista-row-{{ lista.uuid }}"
    hx-swap="outerHTML"
    class="btn-primary">
    Iniciar Separação
</button>
```

## 4. Filtros Avançados
- **Busca Global:** Filtro em tempo real (via `hx-get` e `hx-trigger="keyup changed delay:500ms"`) por nome de aluno ou escola.
- **Toggle de Templates:** Filtro para visualização apenas de `is_template=True`.