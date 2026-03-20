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

## 6. Compartilhamento via QR Code Dinâmico
- **Geração On-the-Fly (Server-side):** Utilização da biblioteca qrcode em Python para gerar a imagem do código instantaneamente no backend. A imagem é servida diretamente via HttpResponse como um stream de dados (MIME type image/png), eliminando a necessidade de salvar arquivos físicos ou ocupar espaço no storage do WebApp.
- **URLs de Template Encurtadas:** Integração com identificadores únicos (UUIDs) para criar QR Codes com baixa densidade de pixels, garantindo uma leitura rápida e precisa mesmo quando impressos em materiais pequenos como etiquetas ou cartões de visita.
- **Modal de Partilha Integrado:** Interface minimalista que exibe o QR Code gerado dinamicamente ao clicar no ícone de partilha, permitindo que o lojista ou o cliente apresente o código diretamente na tela do telemóvel para clonagem imediata.
- **Ponto de Venda Físico (Phygital):** Facilita a transição do mundo físico para o digital, permitindo que a papelaria imprima cartazes de "Listas Escolares 2026" para colagem em vitrines ou escolas, direcionando o pai diretamente para o fluxo de /usar-template/ sem digitação de URLs.
- **Validação de Acesso:** O endpoint de geração do QR Code verifica em tempo real se o template solicitado é público e válido, garantindo que códigos antigos ou de listas privadas não sejam renderizados por questões de segurança.

## 7. Exportação de PDF com WeasyPrint
- **Geração de PDF On-the-Fly:** Utilização da biblioteca WeasyPrint para converter templates HTML em documentos PDF profissionais diretamente no servidor, sem salvar arquivos físicos.
- **Integração com QR Code Dinâmico:** Incorporação automática do QR Code gerado em Base64 no PDF, permitindo acesso direto à versão digital da lista.
- **Template Específico para Impressão:** Design otimizado para papel A4 com estilos CSS inline, mantendo a identidade visual Slate Palette da Papelaria Criativa.
- **Download Direto:** Resposta HTTP com Content-Type application/pdf e Content-Disposition attachment, permitindo download imediato sem armazenamento no servidor.
- **Cálculos Automáticos:** Inclusão de subtotais e totais com desconto PIX no documento impresso, garantindo precisão para o setor de separação física da loja.
