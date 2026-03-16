4. Arquitetura do Projeto (Sugestão Técnica)

Para suportar as funcionalidades descritas, recomenda-se a seguinte estrutura:

4.1 Frontend e Estado Global

Framework: React.js com Next.js (App Router) para otimização de SEO e carregamento veloz.

Gerenciamento de Estado: Zustand. É ideal para este projeto por ser leve e permitir a sincronização fácil com o localStorage, garantindo a persistência do carrinho.

Estilização: Tailwind CSS para garantir a fidelidade ao Design System com baixo custo de performance.

4.2 Camada de Dados e API

Backend: Node.js (NestJS ou Express) para processar as regras de negócio complexas (como cálculos de impostos e cupons).

Banco de Dados: PostgreSQL para dados relacionais (Produtos, Categorias) e Redis para cache de buscas preditivas e sessões temporárias.

Estratégia de Busca: Implementação de busca via Fuse.js (no cliente) para catálogos médios ou ElasticSearch para grandes inventários, suportando a busca preditiva.

4.3 Integrações de Checkout

Gateway de Pagamento: Stripe ou Adyen para suportar Cartão de Crédito e Webhooks de confirmação.

Sistema de PIX: Integração direta com APIs bancárias para geração dinâmica de QR Codes e aplicação imediata do desconto de 10%.