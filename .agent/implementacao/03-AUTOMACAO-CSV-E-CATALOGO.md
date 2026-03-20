03 - Automação CSV e Gestão de Catálogo (Templates)

1. Objetivo da Automação

Eliminar a necessidade de cadastro manual unitário de produtos. O lojista deve ser capaz de exportar uma planilha de seu sistema de estoque atual (ERP local) e importá-la para o WebApp, garantindo preços e estoques atualizados para o período de volta às aulas.

2. Ingestão de Dados via CSV

2.1 Formato do Arquivo Requerido

O arquivo .csv deve seguir obrigatoriamente este cabeçalho (headers):
nome,preco,categoria,estoque,codigo_barras,imagem_url

2.2 Implementação da View de Importação (views.py)

Esta funcionalidade deve processar o arquivo em memória, validar os dados e atualizar produtos existentes ou criar novos.

import csv
import io
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from .models import Produto

@staff_member_required
def importar_produtos_csv(request):
    if request.method == 'POST':
        csv_file = request.FILES.get('file')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'O arquivo deve ser um CSV.')
            return redirect('admin_catalogo')

        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        next(io_string) # Pular o cabeçalho

        count = 0
        for row in csv.reader(io_string, delimiter=',', quotechar='"'):
            obj, created = Produto.objects.update_or_create(
                nome=row[0],
                defaults={
                    'preco': row[1],
                    'categoria': row[2],
                    'estoque': row[3],
                    'codigo_barras': row[4],
                    'imagem_url': row[5],
                }
            )
            count += 1
        
        messages.success(request, f'{count} produtos processados com sucesso!')
        return redirect('admin_catalogo')
    
    return render(request, 'staff/importar_csv.html')


3. Gestão de Templates (Listas Modelo)

Um "Template" é uma ListaEscolar onde is_template=True e o campo usuario pode ser nulo ou vinculado ao admin.

3.1 Fluxo de Criação de Template

Admin cria uma nova lista no painel.

Adiciona os itens padrão (ex: Lista 1º Ano Colégio Santo Agostinho).

Marca o checkbox "Tornar Template Público".

O sistema gera automaticamente o QR Code apontando para a URL de clonagem: /usar-template/[UUID]/.

3.2 Lógica de Clonagem (Copy on Write)

Quando um cliente escaneia o QR Code, o sistema não edita o template, mas cria uma cópia para o cliente.

@login_required
def clonar_template(request, uuid):
    template = get_object_or_404(ListaEscolar, uuid=uuid, is_template=True)
    
    # Criar a nova lista para o usuário logado
    nova_lista = ListaEscolar.objects.create(
        usuario=request.user,
        escola=template.escola,
        serie=template.serie,
        status='aberta'
    )
    
    # Clonar os itens do template para a nova lista
    for item in template.itens.all():
        ItemLista.objects.create(
            lista=nova_lista,
            produto=item.produto,
            quantidade=item.quantidade
        )
    
    messages.success(request, f'Lista da {template.escola} copiada com sucesso!')
    return redirect('client_dashboard')


4. Interface do Catálogo (Staff)

O catálogo no painel administrativo deve permitir:

Busca Rápida: Filtro por nome ou código de barras.

Edição em Lote: Selecionar múltiplos produtos e aplicar desconto (ex: -10%).

Visualização de Templates: Uma área dedicada para ver todos os QR Codes ativos e prontos para impressão em etiquetas.