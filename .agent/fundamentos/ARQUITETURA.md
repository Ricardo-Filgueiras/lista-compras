# Arquitetura do Webapp Papelaria Criativa

## Estrutura de Pastas e Componentes

```
lista-compras/
├── .agent/
│   ├── fundamentos/        # Definições de Negócio e UX
│   └── implementacao/     # Detalhes Técnicos e Código
├── src/
│   ├── core/               # Configurações globais
│   └── shopping/           # Módulo principal
│       ├── static/shopping/css/style.css # Design System (Slate Palette)
│       └── templates/shopping/
│           ├── client/     # UI do Cliente (Pai/Mãe)
│           └── staff/      # UI da Papelaria (Admin/Lojista)
│               ├── dashboard.html    # Pipeline de Pedidos
│               └── pdf/              # Templates de Impressão (Picking List)
```

## Novas Rotas e Fluxos

### Fluxo do Cliente
- `/` → Home
- `/compras/` → Dashboard Cliente
- `/compras/<uuid>/` → Detalhes/Edição
- `/compras/<uuid>/usar-template/` → Clonagem de lista

### Fluxo Administrativo (Staff)
- `/dashboard/admin/` → Pipeline de pedidos (Agrupados por status)
- `/dashboard/admin/catalogo/` → Gestão de produtos e templates
- `/dashboard/admin/importar-csv/` → Atualização massiva de estoque/preços
- `/dashboard/admin/pdf/<uuid>/` → Geração de Picking List para separação

## Modelos de Dados (Django Models)

- `Product`: Catálogo mestre de artigos da papelaria.
- `ShoppingList`: Entidade central (Pedido ou Template). Possui `status` e `is_template`.
- `ShoppingItem`: Relação entre lista e produto com quantidade.
- `ShoppingShare`: Controle de acessos colaborativos.
