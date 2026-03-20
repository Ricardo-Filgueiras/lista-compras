# Requisitos do Sistema - Projeto Lista de Compras

Este documento descreve as dependências de sistema (não-Python) necessárias para o funcionamento pleno de todas as funcionalidades do projeto.

## Geração de PDF (WeasyPrint)

A funcionalidade de geração de PDFs utiliza a biblioteca `WeasyPrint`, que possui dependências de sistema específicas para renderização de fontes e layouts (GTK3).

### Windows

O erro `cannot load library 'libgobject-2.0-0'` ocorre porque o WeasyPrint não consegue localizar as DLLs do GTK no Windows.

#### Passos para Instalação:

1. **Baixar o GTK3 Runtime:**
   - Acesse o repositório oficial do instalador para Windows: [GTK-for-Windows-Runtime-Environment-Installer](https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases).
   - Baixe a versão estável mais recente (ex: `gtk3-runtime-3.24.xx-20xx-xx-xx-ts-win64.exe`).

2. **Instalar:**
   - Execute o instalador.
   - **IMPORTANTE:** Durante a instalação, marque a opção **"Add to PATH"** (Adicionar ao PATH do sistema).

3. **Reiniciar o Ambiente:**
   - Reinicie seu Terminal, VS Code ou IDE após a instalação para que as novas variáveis de ambiente sejam carregadas.

### Linux (Ubuntu/Debian)

No Linux, instale as bibliotecas via `apt`:

```bash
sudo apt-get update
sudo apt-get install build-essential python3-dev python3-pip python3-setuptools python3-wheel python3-cffi libcairo2 libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 libffi-dev shared-mime-info
```

### macOS

No macOS, utilize o `Homebrew`:

```bash
brew install cairo pango gdk-pixbuf libffi
```

---

## QRCode (Pillow)

Para a geração de QRCodes, o sistema utiliza a biblioteca `Pillow`. Geralmente, as dependências são instaladas automaticamente via `pip`, mas em alguns sistemas Linux pode ser necessário instalar bibliotecas de desenvolvimento de imagem:

```bash
sudo apt-get install libjpeg-dev zlib1g-dev
```
