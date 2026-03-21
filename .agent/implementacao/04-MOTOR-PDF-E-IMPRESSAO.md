# 04 - Motor PDF e Logística de Impressão (Picking List)

## 1. Geração de QR Code Dinâmico (Memory Stream)

```python
import qrcode
import base64
from io import BytesIO

def generate_base64_qr(url):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    
    return base64.b64encode(buffer.getvalue()).decode('utf-8')
```

## 2. Picking List (Folha de Separação)

### 2.1 Template de Impressão (Picking)
Otimizado para P&B, com foco em conferência manual.

```html
<style>
    @page { size: A4; margin: 1cm; }
    .item-row { border-bottom: 1px solid #000; padding: 4px 0; }
    .pix-price { font-weight: bold; color: #16A34A; }
</style>

<div class="header">
    <h1>SEPARAÇÃO: {{ shopping_list.school }} - {{ shopping_list.grade }}</h1>
    <p>Cliente: {{ shopping_list.student_name }} | UUID: {{ shopping_list.uuid|slice:":8" }}</p>
</div>

{% for item in items %}
<div class="item-row">
    [ ] {{ item.quantity }}x {{ item.product.name }} 
    <small>({{ item.product.category }})</small>
</div>
{% endfor %}

<div class="footer">
    <p>Total: R$ {{ total }}</p>
    <p class="pix-price">Total PIX (10% off): R$ {{ pix_total }}</p>
    <img src="data:image/png;base64,{{ qr_base64 }}" width="100">
</div>
```

## 3. View de Geração de PDF (WeasyPrint)

```python
from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse

@staff_member_required
def generate_picking_pdf(request, uuid):
    lista = get_object_or_404(ShoppingList, uuid=uuid)
    items = lista.items.all().order_by('product__category')
    
    qr_base64 = generate_base64_qr(request.build_absolute_uri(lista.get_absolute_url()))
    
    context = {
        'shopping_list': lista,
        'items': items,
        'total': lista.get_total(),
        'pix_total': lista.get_pix_total(),
        'qr_base64': qr_base64,
    }
    
    html_string = render_to_string('staff/pdf/picking_list.html', context)
    pdf_file = HTML(string=html_string).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Picking_{lista.uuid|slice:":8"}.pdf"'
    return response
```

## 4. Logística Phygital
- **QR Code Reverso:** Injetado no rodapé de todos os documentos impressos para que o lojista, ao terminar a separação, aponte a câmera e mude o status para "Pronto para Levantamento" instantaneamente no sistema.
- **Cache de QR Codes:** Utilização de `lru_cache` para URLs de templates estáticos para reduzir processamento de CPU.