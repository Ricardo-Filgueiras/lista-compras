# Arquitetura do Webapp Lista de Compras

## Estrutura de Pastas

```
lista-compras/
├── .agent/
│   ├── COMPRAS.md          # Especificação do módulo
│   └── ARQUITETURA.md      # Este arquivo
├── .venv/                  # Ambiente virtual Python
├── dotenv_files/
│   └── .env                # Variáveis de ambiente
├── src/
│   ├── manage.py
│   ├── requirements.txt
│   ├── core/               # Configurações do projeto Django
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── asgi.py
│   │   └── wsgi.py
│   └── shopping/           # App principal de compras
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── forms.py
│       ├── models.py
│       ├── urls.py
│       ├── views.py
│       ├── migrations/
│       │   └── __init__.py
│       └── templates/
│           └── shopping/
│               ├── base.html
│               ├── login.html
│               ├── register.html
│               ├── list_index.html
│               ├── list_detail.html
│               ├── item_form.html
│               └── partials/
│                   └── item_row.html
└── pyproject.toml
```

## Modelos (Models)

- `ShoppingList` — lista de compras de um usuário (uuid, name, user, budget, created_at, updated_at)
- `ShoppingItem` — itens da lista (uuid, shopping_list, name, quantity_value, unit, price, is_purchased)
- `ShoppingShare` — compartilhamento entre usuários (shopping_list, shared_with, shared_by, can_edit)
- `MonthlyShoppingBudget` — orçamento mensal por usuário (user, period, amount)

## Fluxo de URL

```
/               → login (redirect para /compras/ se autenticado)
/registrar/     → cadastro de usuário
/logout/        → encerrar sessão
/compras/       → lista de todas as listas do usuário
/compras/<uuid>/         → detalhe de uma lista
/compras/<uuid>/editar/  → editar lista
/compras/<uuid>/excluir/ → excluir lista
/compras/<uuid>/item/adicionar/         → adicionar item
/compras/<uuid>/item/<uuid>/editar/     → editar item
/compras/<uuid>/item/<uuid>/excluir/    → excluir item
/compras/<uuid>/item/<uuid>/toggle/     → marcar/desmarcar item
/compras/<uuid>/compartilhar/           → compartilhar lista
/compras/<uuid>/budget/                 → definir orçamento da lista
```

## Stack Técnica

- **Backend:** Django 6.x
- **Banco de dados (dev):** SQLite3 (default para desenvolvimento local)
- **Banco de dados (prod):** PostgreSQL (via env vars)
- **Frontend:** HTML5 + CSS3 (vanilla) + HTMX para interações parciais
- **Autenticação:** Django Auth nativo (login/logout/register)
- **Segurança:** UUIDs nas URLs (anti-IDOR) + ownership check nas views
