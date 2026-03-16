# Módulo de Compras (Shopping)

## 1. Descrição Geral

O módulo de "Compras" é uma aplicação Django projetada para ajudar os usuários a gerenciar suas listas de compras. Ele permite a criação de múltiplas listas, a adição de itens com detalhes como quantidade e preço, o acompanhamento de itens já comprados e o gerenciamento de um orçamento de compras mensal. Além disso, o módulo possui uma funcionalidade de compartilhamento, permitindo que vários usuários colaborem na mesma lista.

A arquitetura do módulo garante privacidade e segurança ao utilizar UUIDs dinâmicos em vez de IDs sequenciais nas URLs para controle e busca de entidades, prevenindo assim vulnerabilidades de acesso indevido (IDOR) e implementando rigoroso controle de acesso (Ownership base).

## 2. Funcionalidades

### Gerenciamento de Listas
- **Criar Lista:** Usuários podem criar novas listas de compras fornecendo um nome. A lista ganha um identificador UUID para fácil referência segura nas URLs.
- **Visualizar Listas:** A página inicial do módulo exibe todas as listas que o usuário criou de forma independente ou que foram compartilhadas com ele.
- **Detalhar Lista:** Ao selecionar uma lista, o usuário visualiza todos os itens contidos nela, separados entre "Pendentes" e "Comprados". A visão detalhada também mostra um resumo financeiro.
- **Excluir Lista:** O proprietário de uma lista pode excluí-la de maneira permanente. Essa exclusão remove atrilhados itens e acessos de compartilhamento.

### Gerenciamento de Itens
- **Adicionar Item:** Dentro de uma lista, é viável registrar novos itens especificando nome, quantidade, unidade (ex: kg, L, un) e preço estimado ou oficial.
- **Editar Item:** Os detalhes de um item, como valores e descrições, podem ser atualizados se o usuário for o dono ou um convidado com permissão de edição.
- **Excluir Item:** Itens podem ser permanentemente removidos de uma lista, refletindo-se assim no custo geral.
- **Marcar como Comprado (Toggle):** Usuários podem alterar ativamente o status de um item para "comprado" ou desfazer a ação, e o sistema HTMX aciona o recarregamento na tela (`HX-Refresh`). Isso o move para a seção de itens concluídos e atualiza em tempo real o cálculo de totais.

### Compartilhamento
- **Compartilhar Lista com Permissões:** O proprietário pode vincular a lista a outro usuário do sistema ao localizar com precisão um username existente. O remetente pode selecionar ativamente se o destinatário terá privilégios extras (campo checkbox de edição).
- **Listas Compartilhadas e Acesso Integrado:** As listas compartilhadas aparecem de maneira contínua na tela principal junto aos itens particulares, restritos pela premissa `can_edit`.

### Orçamento
- **Definir Orçamento:** Existe uma rotina acionada por interface para estipular o limite oficial do orçamento. **É importante notar que o orçamento é único para cada lista de compras.**
- **Acompanhamento Financeiro (Cálculos por DB Sum e F):** A aplicação quantifica interações pelo banco de dados:
    - **Total Pendente:** Soma da equação `(quantidade * preço)` de produtos pendentes no mercado da referida lista.
    - **Total Comprado:** Extrato acumulativo do custo garantido em itens fechados ("carrinho") da lista.
    - **Saldo Projetado:** Indicador financeiro que espelha `Orçamento da Lista - (Total Global)`.

## 3. Estrutura de Dados (Modelos Django)

- **`ShoppingList`**:
    - `uuid`: `UUIDField` - campo indexado para urls e controle de instâncias visuais.
    - `name`: Nome textual da lista.
    - `user`: Controle de propriedade base ForeignKey relacionada à `auth.User`.
    - Atributos nativos de `created_at` e `updated_at`.
- **`ShoppingItem`**:
    - `uuid`: Identificador alfanumérico primário via UUID4 gerado sem intervenção.
    - `shopping_list`: Chave pai e vinculativa da coleção.
    - `name`: Nome descritivo da mercadoria.
    - `quantity_value`: Expresso em métricas decimais (`DecimalField`) para acomodar peso, líquidos, e singulares.
    - `unit`: Denotação da massa/grandeza com a default `un`.
    - `price`: O valor unitário expresso na loja.
    - `is_purchased`: Variável finalizadora - checagem se consta na sacola ou carrinho base `BooleanField`.
    - `@property total_price`: Facilidade Pythonic na obtenção final com multiplicação instanciada nativa.
- **`ShoppingShare`**:
    - `shopping_list`: O contexto local da parceria.
    - `shared_with` e `shared_by`: Par de chaves que constroem a ligação remetente / parceiro (`auth.User`).
    - `can_edit`: Expressão Booleana fundamental para conceder (ou barrar) criação, exclusão de itens por parte do parceiro em `views`.
    - Relacionamento exclusivo bloqueado por base da dupla (`shopping_list`, `shared_with`).
- **`MonthlyShoppingBudget`**:
    - `user`: Identificador do consumidor que instanciou o teto financeiro.
    - `period`: Formatação do bloco sazonal (`DateField` contendo primeiro do mês ativo local).
    - `amount`: Valor estipulado a ser verificado contra as predições.
    - Relacionamento restrito e acoplado de (`user`, `period`).

## 4. Guia para Recriação por um Agente

Para recriar este módulo num cenário base ou de clone:

1.  **Crie a App:** Inicie um módulo via script padrão `django-admin startapp shopping` anexando posteriormente a lista ao `INSTALLED_APPS`.
2.  **Defina os Modelos em Models.py:** Construa as arquiteturas base de Class `ShoppingList`, `ShoppingItem`, `ShoppingShare`, `MonthlyShoppingBudget`. Acople a geração de UUID nos construtores padrões de Lista e Item. Implemente as Restrições Múltiplas `unique_together` adequadas em metadados. Realize as Migrations.
3.  **Crie os Formulários:** Expresse e extraia Models via `forms.ModelForm` em `forms.py`. Construa form de Share através de um tradicional `forms.Form`. Assegure suporte para Inputs decimais fracionados.
4.  **Implemente as Views Seguras em Views.py:**
    - Isole e tranque a visualização de acessibilidade via login e Q Query combinados: `Q(user=request.user) | Q(shares__shared_with=request.user)`.
    - Assegure validação contra `uuid` nas rotas do painel visual. Crie a proteção secundária ao extrair um objeto buscando também pela condição restritiva `can_edit=True` ao manipular propriedades de `Create, Update, Delete` em Item.
    - Incorpore o recurso de `aggregate` de QuerySets conjugando `Sum` e `F`.
    - Inclua validações lógicas e notificações de Message ao recarregar a visualização padrão.
5.  **Configure as URLs sem IDs Sequenciais:** Mapeie os destinos baseados puramente no uso do termo UUID: `path('<uuid:uuid>/', views.list_detail, name='list_detail')`.
6.  **Integrações de Templates:** Combine lógicas do framework front-end incorporado mesclando blocos. Caso adicione dinâmicas parciais instale chamadas de JS Vanilla para checagem ou base de lib HTMX no atributo Response `HX-Refresh`.

## 5. Pontos de Melhoria e UX/UI

### Melhorias de Funcionalidade
1.  **Soma de Quantidades Inteligente:** Se adicionar pela inserção padrão uma variante com idêntico "nome", empilhar a conta quantitativa ao invés de alocar nova subseção independente.
2.  **Categorias de Itens Modeladas:** O módulo lucraria atrevidamente se implementasse instâncias dinâmicas como `Category`, com visualização colorida das matrizes "Laticínios", "Vegetais". Ideal para fatiamento logístico.
3.  **Templating Sazonal Pró-Ativo:** Um recurso em que o fechador das compras gerasse estâncias espelhos (como Listas Mensais fixas e idênticas que contornam a inserção chata) das mais procuradas.
4.  **Adoção de Navegação Retrospectiva dos Meses:** Evoluir amplamente o `MonthlyShoppingBudget` adicionando ponteiros gráficos facilitando o retrospecto do consumo e evolução histórica anterior.

### Melhorias de UX/UI
1.  **Plena Migração para Interatividade HTMX:** Substituir de modo agressivo operações convencionais em Adicionar Itens de forma invisível. Evitando recarregar as páginas nas telas de preenchimento, algo notavelmente estressor nestas listas grandes.
2.  **Interface de Budgeting Expandido e Barra Gráfica:** Melhorar ativamente referências e contrastes orçamentais instalando preenchimento com barras liminares (vermelho para excesso e verde/azul para controle).
3.  **Adição Instantânea Multicamadas:** Estabilizar inputs "sticky" (adesivos na parte inferior de mobile) que com simples acionamento da tecla Submeter aglomerem subitens à lista de modo imperceptível à transição.
4.  **Arranjo Móvel (`Drag-And-Drop`):** Incorporação de elementos Javascript do tipo sortableJS para organizar priorização sequencial ao passear num corredor virtual/real.
