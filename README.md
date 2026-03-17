# 🎨 Papelaria Criativa - WebApp de Listas de Compras

O **Papelaria Criativa** é uma aplicação web moderna desenvolvida em **Django** para otimizar o processo de compra de materiais escolares e de escritório. O objetivo é reduzir o tempo de espera na loja física através de um sistema colaborativo de pré-montagem de listas.

---

## 🚀 Funcionalidades Principais

- **🏠 Landing Page Moderna:** Interface de boas-vindas focada na proposta de valor da papelaria.
- **📋 Painel de Listas (Dashboard):** Gerenciamento centralizado de listas próprias e compartilhadas.
- **📑 Sistema de Templates:** Criação de cópias privadas de listas prontas (ex: lista de material 1º ano).
- **👥 Edição Colaborativa:** Link direto para convidar parceiros (esposa, sócios) para editar a mesma lista em tempo real.
- **📲 Interface WebApp Responsiva:** Design otimizado para celulares, focado na densidade de informações e facilidade de uso.
- **🛒 Carrinho Inteligente (HTMX):** 
  - Ajuste de quantidade (+/-) sem recarregar a página.
  - Exclusão instantânea de itens.
  - Barra de resumo (Sticky Footer) sempre visível com cálculo de **Desconto PIX (10% OFF)**.
- **🔒 Checkout & Travamento:** Ao finalizar a lista, ela é trancada para separação logística pela papelaria.

---

## 🛠️ Stack Técnica

- **Backend:** Django 6.x (Python)
- **Frontend:** HTML5, CSS3 (Custom Design System), HTMX (para interações dinâmicas sem refresh)
- **Gerenciador de Pacotes:** `uv` (extremamente rápido e moderno)
- **Banco de Dados:** SQLite (Desenvolvimento) / PostgreSQL (Produção)

---

## ⚙️ Como Executar o Projeto

1. **Instale o `uv`** (se ainda não tiver):
   ```powershell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Clone o repositório:**
   ```bash
   git clone https://github.com/seu-usuario/lista-compras.git
   cd lista-compras
   ```

3. **Instale as dependências e crie o ambiente virtual:**
   ```bash
   uv sync
   ```

4. **Execute as migrações:**
   ```bash
   uv run python src/manage.py migrate
   ```

5. **Inicie o servidor:**
   ```bash
   uv run python src/manage.py runserver
   ```

Acesse em: `http://127.0.0.1:8000`

---

## 📂 Estrutura do Projeto

- `src/shopping/`: App principal de gestão de listas e itens.
- `src/core/`: Configurações globais do Django.
- `src/shopping/static/shopping/css/style.css`: Design System completo (Slate-50 Palette).
- `src/shopping/templates/shopping/partials/`: Componentes reutilizáveis (item rows, summary footer).
- `.agent/`: Documentação técnica e de arquitetura do projeto.

---

## 📜 Licença

Este projeto está sob a licença [MIT](LICENSE).
