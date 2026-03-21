# Design System: Papelaria Criativa (Slate Palette)

Este sistema visual foca na **neutralidade, minimalismo e densidade otimizada**.

## 🎨 Cores (Slate-based)
- **Background:** `#F8FAFC` (Slate-50) para um fundo limpo e moderno.
- **Card Base:** `#FFFFFF` (Branco Puro).
- **Brand Primary:** `#F97316` (Orange-500) para ações criativas e de papelaria.
- **Smart Swap/Edit:** `#2563EB` (Blue-600) para destaques de colaboração.
- **Checkout/Success:** `#16A34A` (Green-600) para finalização e preços no PIX.
- **Danger:** `#EF4444` (Red-500) para lixeira e exclusão.

## 🔡 Tipografia
- **Família:** `Inter` (Sans-serif moderna).
- **Hierarquia:**
  - Títulos: `Bold` (800), `Slate-900`.
  - Nomes de Produtos: `Bold` (700), `Slate-800`.
  - Categorias: `Black` (800), `UpperCase`, `Slate-400`.
  - Preços: `Bold` (800), `Slate-900`.

## 📦 Componentes Visuais
- **Cards de Lista (Cliente):** Bordas arredondadas (`20px`), sombras suaves e ícones grandes.
- **Pipeline de Status (Staff):** Colunas verticais (`flex-1`) com scroll independente e badges coloridos para status.
- **Item Rows:** Layout horizontal compacto (`grid`), reduzindo o scroll vertical.
- **Sticky Footer:** Barra fixa inferior com `backdrop-filter: blur(20px)` e sombra superior suave.

## 🛠 Staff UI (Painel Admin)
- **Densidade:** Maior que na UI do cliente, permitindo ver múltiplos pedidos por tela.
- **Badges de Status:**
  - `Fechado`: Slate-600 (Neutro/Aguardando).
  - `Em Separação`: Blue-600 (Ação em curso).
  - `Pronto`: Green-600 (Sucesso/Retirada).
- **Feedback HTMX:** Transições de opacidade ao mover cartões entre colunas.

## 📱 Responsividade (Mobile First)
- Em telas menores (`< 600px`), o sistema empilha informações para manter o conforto do clique:
  - O seletor de quantidade e o preço total ficam lado a lado na base do card.
  - A barra de navegação ganha preenchimento lateral reduzido (`1rem`).
  - Botões de ação (`+`/`-`) são redimensionados para `28px/32px` para toque preciso.

## ⚡ Micro-interações
- **Feedback Visual:** Efeito `scale-95` no clique de botões.
- **Estados:** `hover` com elevação de sombra e `active` para feedback táctil simulado.
- **HTMX Transitions:** Atualizações parciais de dados acompanhadas de mudanças de estado (ex: botão "Copiado!").
