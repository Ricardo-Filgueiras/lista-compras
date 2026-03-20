02 - Dashboard Administrativo (Interface do Lojista)

1. Objetivo da Interface

A interface administrativa (Staff) deve ser otimizada para Desktop e Tablet, focando em densidade de informação e velocidade de operação. O lojista deve conseguir identificar rapidamente quais pedidos precisam de atenção e alterar seus estados com o mínimo de cliques.

2. Estrutura de Pastas e Organização

Para manter a separação de responsabilidades e evitar confusão entre a UI do cliente e do lojista:

templates/
  ├── base.html              # Layout base comum
  ├── client/                # Templates exclusivos do pai/mãe
  └── staff/                 # Templates exclusivos da papelaria
       ├── dashboard.html    # Visão geral de pedidos
       ├── detail.html       # Visualização detalhada de um pedido
       └── components/       # Fragmentos HTMX (linhas da tabela, badges)


3. Definição das Views (views.py)

As views administrativas devem ser protegidas pelo decorator @staff_member_required.

from django.shortcuts import render, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from .models import ListaEscolar

@staff_member_required
def admin_dashboard(request):
    """Lista todos os pedidos agrupados por status."""
    # Buscamos as listas que não são templates, ordenadas pelas mais recentes
    listas = ListaEscolar.objects.filter(is_template=False).order_by('-atualizado_em')
    
    context = {
        'listas_pendentes': listas.filter(status='fechada'),
        'listas_separacao': listas.filter(status='separacao'),
        'listas_prontas': listas.filter(status='pronto'),
    }
    return render(request, 'staff/dashboard.html', context)

@staff_member_required
def update_status_htmx(request, uuid):
    """Atualiza o status via HTMX e retorna apenas o componente do badge."""
    lista = get_object_or_404(ListaEscolar, uuid=uuid)
    novo_status = request.POST.get('status')
    
    if novo_status in dict(ListaEscolar.STATUS_CHOICES):
        lista.status = novo_status
        lista.save()
        
    # Retorna um template parcial para atualizar apenas a linha na tabela
    return render(request, 'staff/components/lista_row.html', {'lista': lista})


4. Design do Dashboard (Frontend)

O dashboard deve utilizar a Slate Palette (Cinzas azulados) para transmitir seriedade e reduzir o cansaço visual.

4.1 Layout das Colunas (Trello Style)

Uma abordagem eficiente é dividir o dashboard em colunas de status, permitindo uma visão clara do pipeline de trabalho:

Coluna 1: Novos Pedidos (🔒 Fechada)

Foco: Verificação de pagamento.

Coluna 2: Em Separação (📦)

Foco: Operação física no estoque.

Coluna 3: Aguardando Retirada (✅)

Foco: Atendimento ao balcão.

4.2 Integração com HTMX

Para evitar o carregamento total da página ao mudar um pedido de "Separação" para "Pronto", utilizaremos atributos HTMX nos botões de ação:

<!-- Exemplo de botão de ação dentro da linha da tabela -->
<button 
    hx-post="{% url 'update_status_htmx' lista.uuid %}" 
    hx-vals='{"status": "separacao"}'
    hx-target="#lista-row-{{ lista.uuid }}"
    hx-swap="outerHTML"
    class="bg-blue-600 text-white px-3 py-1 rounded text-sm">
    Iniciar Separação
</button>


5. Funcionalidades de Filtro e Busca

O painel deve incluir uma barra de ferramentas superior com:

Busca por Nome: Localizar pedidos de um aluno ou pai específico.

Filtro por Escola: Agrupar pedidos para otimizar a separação de itens comuns.

Toggle de Templates: Atalho para o lojista gerenciar as "Listas Modelo" da loja separadamente.