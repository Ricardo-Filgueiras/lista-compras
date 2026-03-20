04 - Motor PDF e Logística de Impressão (Picking List)

1. Objetivo da Logística de Impressão

O objetivo desta fase é transpor a eficiência digital para o mundo físico. Utilizaremos o motor de renderização já configurado para gerar documentos que auxiliem o funcionário na separação dos itens (Picking List) e forneçam ao cliente um comprovante físico com o QR Code de retorno.

2. Reutilização de Componentes Existentes

O projeto já possui as dependências necessárias instaladas. Reutilizaremos:

WeasyPrint: Para converter os templates HTML específicos de "Staff" em PDF.

Lib qrcode (Python): Para gerar os códigos de acesso rápido nos documentos impressos.

Base64: Para injetar as imagens dos QR Codes diretamente no HTML sem salvar ficheiros.

3. Implementação da Picking List (Folha de Separação)

3.1 Template HTML de Separação (staff/pdf/picking_list.html)

Este template deve ser otimizado para leitura rápida e conter campos de conferência manual.

{% load static %}
<!DOCTYPE html>
<html>
<head>
    <style>
        @page { size: A4; margin: 1cm; }
        body { font-family: 'Courier', monospace; font-size: 10pt; }
        .item-row { border-bottom: 1px solid #000; padding: 5px 0; }
        .checkbox { border: 1px solid #000; width: 15px; height: 15px; display: inline-block; }
        .header { text-align: center; border-bottom: 3px double #000; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>LISTA DE SEPARAÇÃO #{{ lista.id }}</h1>
        <p>Escola: {{ lista.escola }} | Cliente: {{ lista.usuario.get_full_name }}</p>
    </div>

    {% for item in itens %}
    <div class="item-row">
        <span class="checkbox"></span> 
        <strong>[{{ item.quantidade }}x]</strong> {{ item.produto.nome }}
        <br><small>Categoria: {{ item.produto.categoria }} | Local: Corredor {{ item.produto.categoria|slice:":1" }}</small>
    </div>
    {% endfor %}

    <div style="margin-top: 30px; text-align: center;">
        <img src="data:image/png;base64,{{ qr_base64 }}" width="80">
        <p>Escaneie para finalizar no sistema</p>
    </div>
</body>
</html>


3.2 View de Geração do PDF Administrativo

A lógica é idêntica à do cliente, mas com contexto focado na operação interna.

@staff_member_required
def gerar_picking_pdf(request, uuid):
    lista = get_object_or_404(ListaEscolar, uuid=uuid)
    itens = lista.itens.all().order_by('produto__categoria') # Ordenar para facilitar o percurso na loja
    
    # Reutilização da lógica de QR Code em memória
    qr_base64 = gerar_base64_qr(request.build_absolute_uri(lista.get_absolute_url()))

    context = {
        'lista': lista,
        'itens': itens,
        'qr_base64': qr_base64,
    }
    
    html_string = render_to_string('staff/pdf/picking_list.html', context)
    pdf_file = HTML(string=html_string).write_pdf()
    
    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Picking_{lista.id}.pdf"'
    return response


4. Impressão de Etiquetas de QR Code para Templates

Para os Templates Públicos, o Admin precisa imprimir etiquetas para colar nos murais da loja.

4.1 Layout de Etiqueta (80mm ou A4 Múltiplo)

Conteúdo: Nome da Escola + Série + QR Code Grande + Instrução "Aponte a Câmara".

Lógica: Uma View que gera uma página A4 com 12 a 24 QR Codes de templates diferentes para corte e colagem rápida.

5. Fluxo Operacional (O Ciclo Completo)

O lojista visualiza um novo pedido no Dashboard.

Clica em "Imprimir Picking List".

Com o papel em mãos, faz a separação física (marcando os checkboxes).

Após a separação, lê o QR Code no rodapé do papel com o seu telemóvel para abrir a lista no sistema e marcar como "Pronto para Levantamento".

6. Próximos Passos

Testar a renderização de tabelas longas (quebra de página) no WeasyPrint.

Configurar a ordenação dos itens por categoria no PDF para minimizar o movimento do funcionário dentro da papelaria.

Implementar o botão de impressão rápida diretamente na linha da tabela do Dashboard Staff.