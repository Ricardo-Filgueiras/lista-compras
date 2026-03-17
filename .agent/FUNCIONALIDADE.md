# Funcionalidades Detalhadas - Papelaria Criativa

O WebApp foi projetado para oferecer uma experiência de "Aplicativo Nativo" no navegador, utilizando **HTMX** para interações fluidas.

## 1. Gestão Dinâmica de Itens
- **Controle de Quantidade (+/-):** Alteração instantânea da quantidade no card do produto com atualização do preço total e do resumo do pedido (via evento `update-totals`).
- **Remoção Instantânea:** Botão de lixeira com confirmação para excluir itens sem recarregar a página.
- **Destaque de Categoria:** Itens rotulados por categoria (ex: PAPÉIS, ESCRITA, CADERNOS).

## 2. Fluxos de Compartilhamento
- **Edição Colaborativa (`/entrar/`):** Link exclusivo para compartilhar com membros da família. Permite que múltiplos usuários editem a mesma lista de compras.
- **Link de Template (`/usar-template/`):** Mecanismo de clonagem que permite a um cliente criar sua própria lista baseada em um modelo da papelaria. Inclui página de confirmação para evitar cópias acidentais.

## 3. Checkout e Totais
- **Sticky Footer (Resumo do Pedido):** Barra fixa na parte inferior da tela que acompanha o scroll, exibindo sempre o Valor Total.
- **Cálculo de Desconto PIX:** Exibição automática do valor com 10% de desconto para pagamentos via PIX.
- **Fechamento de Pedido:** Botão "CONCLUIR PEDIDO" que trava a edição da lista, garantindo a integridade dos dados para o setor de separação física da loja.

## 4. Gerenciamento do Painel (Dashboard)
- **Grid de Listas:** Visualização elegante de todas as listas do usuário.
- **Exclusão de Listas:** Ícone de lixeira diretamente no card da página inicial com confirmação visual.
- **Diferenciação Visual:** Listas compartilhadas possuem bordas e ícones distintos das listas próprias.

## 5. Experiência do Usuário (UX)
- **Modais Minimalistas:** Formulários de criação de lista integrados ao painel.
- **Home Landing Page:** Página de entrada com foco em conversão e boas-vindas.
- **Logo Dinâmica:** Navegação inteligente que retorna o usuário ao painel se logado, ou à home se deslogado.
