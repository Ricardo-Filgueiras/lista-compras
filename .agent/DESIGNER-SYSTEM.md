Design System: Papelaria Criativa

Este documento estabelece as bases visuais e funcionais para o WebApp de checkout da Papelaria Criativa. O foco do design é a rapidez, clareza e micro-interações fluidas.

1. Princípios de Design

Minimalismo Funcional: O branco e tons de cinza claro dominam para dar destaque aos produtos coloridos da papelaria.

Densidade Otimizada: Itens dispostos em cards horizontais para facilitar a leitura rápida em dispositivos móveis.

Feedback Instantâneo: Toda ação do usuário (troca de item, alteração de quantidade) é acompanhada de uma resposta visual imediata.

2. Tipografia

A família de fontes principal é a Inter (ou similar sans-serif), focada em legibilidade.

Títulos de Seção: Semibold, 20px, Slate-900.

Nomes de Produtos: Bold, 14px, Slate-800.

Marca/Categoria: Black, 10px, UpperCase, Tracking-widest (espaçamento entre letras).

Preços: Black, 16px (no card) a 24px (no total).

3. Componentes Principais

Cards de Produto: Bordas arredondadas (16px), sombras suaves (shadow-sm) e placeholders circulares coloridos para representar os SKUs.

Modais: Design "Bottom Sheet" para mobile (desliza de baixo para cima) e centralizado para desktop. Cantos superiores com 32px de raio.

Botões de Ação: CTAs grandes com altura de 56px a 64px, cantos arredondados de 16px.

Troca Inteligente: Elementos em azul (Blue-600) para destacar sugestões do sistema, diferenciando-os do fluxo padrão de compra.

4. Paleta de Cores (Customizável)

Este tópico define as variáveis de cor utilizadas no Tailwind CSS. Você pode ajustar os códigos hexadecimais conforme a identidade da sua marca.

Variável

Uso

Código Hex (Sugerido)

Primary

Botões principais, ícone da marca

#F97316 (Orange-500)

Secondary

Destaque de Troca Inteligente

#2563EB (Blue-600)

Success

Desconto PIX, preços menores

#16A34A (Green-600)

Danger

Lixeira, alertas, erro

#EF4444 (Red-500)

Neutral-Bg

Fundo da aplicação

#F8FAFC (Slate-50)

Neutral-Card

Cards e headers

#FFFFFF (White)

Text-Main

Títulos e textos fortes

#0F172A (Slate-900)

Text-Muted

Descrições e preços riscados

#94A3B8 (Slate-400)

5. Micro-interações e Estados

Hover: Leve elevação de sombra em cards e botões.

Active: Efeito de escala scale-95 para simular o clique físico de botões.

Animações: slide-in-from-bottom para modais e fade-in para novos elementos no carrinho.

Empty State: Ilustração ou ícone minimalista acompanhado de texto de suporte quando não há itens.

6. Iconografia

Utiliza a biblioteca Lucide React com espessura de traço padrão.

Ícones de 18px para navegação.

Ícones de 14px para controles internos (mais/menos).

Ícones de 24px para destaque em modais (Zap, Gift).