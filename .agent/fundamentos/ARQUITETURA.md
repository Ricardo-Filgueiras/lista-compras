# Arquitetura do Webapp Papelaria Criativa

## Estrutura de Pastas e Componentes

```
lista-compras/
├── .agent/
│   ├── OBJETIVO-PROJETO.md  # Objetivo de Negócio
│   ├── FUNCIONALIDADE.md   # Funcionalidades e UX
│   └── ARQUITETURA.md      # Este arquivo
├── src/
│   ├── core/               # Configurações globais
│   └── shopping/           # Módulo principal de compras
│       ├── static/shopping/css/style.css # Design System (Slate Palette)
│       └── templates/shopping/
│           ├── home.html           # Landing Page
│           ├── list_index.html     # Dashboard (Painel de Listas)
│           ├── list_detail.html    # Detalhes da Lista (Carrinho)
│           ├── list_clone_confirm.html # Confirmação de Template
│           └── partials/
│               ├── item_row.html      # Card Compacto do Item (HTMX)
│               └── footer_summary.html # Sticky Footer Dinâmico (HTMX)
```

## Novas Rotas e Fluxos

- `/` → Home (Landing Page)
- `/compras/` → Index (Dashboard para usuários logados)
- `/compras/<uuid>/` → Detalhes da lista
- `/compras/<uuid>/entrar/` → Link para edição colaborativa (Auto-Join)
- `/compras/<uuid>/usar-template/` → Link para clonar lista (Template)
- `/compras/<uuid>/totais/` → View HTMX para atualização do resumo do footer

## Fluxos Dinâmicos com HTMX

O projeto utiliza HTMX para atualizações parciais de interface sem recarregamento:
- **`update-totals` (Evento):** Disparado quando um item é alterado ou excluído. O footer escuta esse evento (`hx-trigger="update-totals from:body"`) e faz um `GET` para `/totais/` para atualizar os valores.
- **`hx-headers`:** Utilizado para passar o `X-CSRFToken` em requisições `POST`, `PUT` ou `DELETE`.

## Modelos de Dados (Django Models)

- `ShoppingList`: Adicionado campo `is_locked` para controle de checkout.
- `ShoppingItem`: Campo `category` para rotulação visual.
- `ShoppingShare`: Relacionamento de compartilhamento entre usuários.
