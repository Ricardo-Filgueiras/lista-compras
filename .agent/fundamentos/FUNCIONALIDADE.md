# Funcionalidades Detalhadas - Papelaria Criativa

## 1. Experiência do Cliente (B2C)
- **Gestão Dinâmica de Itens:** Atualização instantânea de quantidades e preços via HTMX.
- **Checkout e Desconto PIX:** Ao concluir o pedido, o cliente visualiza o valor total e o desconto de 10% para PIX.
- **Clonagem de Templates:** Facilidade para pais criarem suas listas a partir de modelos escolares via QR Code.
- **Edição Colaborativa:** Link exclusivo para compartilhar com membros da família.

## 2. Painel do Lojista (Staff Dashboard)
- **Pipeline de Pedidos:** Visualização em colunas (estilo Trello) dos pedidos: `Fechado`, `Em Separação`, `Pronto`.
- **Gestão de Catálogo Massiva:** Importação de planilhas CSV para atualização rápida de preços e estoques escolares.
- **Gestão de Templates Públicos:** Criação de listas modelo vinculadas a escolas e séries.

## 3. Logística e Operação Física (Phygital)
- **Geração de Picking List (PDF):** Documento otimizado para o funcionário coletar os itens no estoque, incluindo checkboxes e QR Code de retorno.
- **QR Code de Retorno:** Ao ler o QR Code do papel de separação, o lojista é levado à view que atualiza o status do pedido instantaneamente.
- **Impressão de Etiquetas de Templates:** Geração de folhas A4 com QR Codes para colagem em vitrines ou corredores da loja.

## 4. Segurança e Permissões
- **Staff-Only:** Áreas administrativas protegidas por decoradores `@staff_member_required`.
- **Trava de Edição:** Listas com status `fechada` ou superior são bloqueadas para edição pelo cliente, garantindo integridade logística.
