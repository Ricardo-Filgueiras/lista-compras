import io
import base64
import qrcode
from django.template.loader import render_to_string
from django.http import HttpResponse
from weasyprint import HTML
from .models import ListaEscolar

def gerar_pdf_lista(request, uuid):
    # 1. Buscar dados da lista
    lista = ListaEscolar.objects.get(uuid=uuid)
    itens = lista.itens_selecionados.all()

    # 2. Gerar QR Code em memória (Base64)
    url_lista = request.build_absolute_uri(lista.get_absolute_url())
    qr = qrcode.make(url_lista)
    buffer_qr = io.BytesIO()
    qr.save(buffer_qr, format="PNG")
    qr_base64 = base64.b64encode(buffer_qr.getvalue()).decode()

    # 3. Preparar contexto e renderizar HTML para String
    context = {
        'lista': lista,
        'itens': itens,
        'qr_code_base64': qr_base64,
        'subtotal': lista.get_subtotal(),
        'total_pix': lista.get_total_com_desconto(),
    }
    html_content = render_to_string('templates/lista_pdf.html', context)

    # 4. Converter HTML para PDF com WeasyPrint
    pdf_file = HTML(string=html_content, base_url=request.build_absolute_uri()).write_pdf()

    # 5. Retornar resposta de Download
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Lista_{lista.id}.pdf"'

    return response