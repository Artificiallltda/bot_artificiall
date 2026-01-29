# Bot de Automação de Downloads (Freepik e Envato)

Este projeto é uma aplicação Python que automatiza o processo de download de arquivos do Freepik e Envato Elements, faz o upload para o Google Drive e compartilha o link resultante através de um bot do Telegram.

## 1. Pré-requisitos

Para rodar esta aplicação, você precisará de:

1.  **Python 3.8+** instalado na sua Máquina Virtual (VM).
2.  **Gerenciador de pacotes `pip`**.
3.  **Dependências do Playwright:** O Playwright usa navegadores reais. Você precisa instalar as dependências do Chromium na sua VM.
    ```bash
    # Para sistemas baseados em Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y libnss3 libfontconfig libgtk-3-0 libgbm-dev
    ```
4.  **Conta de Serviço do Google Drive:** Um arquivo JSON de credenciais para permitir que a aplicação acesse seu Google Drive.

## 2. Configuração do Google Drive API

O bot usa uma **Conta de Serviço** para interagir com o Google Drive.

1.  Vá para o [Google Cloud Console] e crie um novo projeto.
2.  Ative a **Google Drive API** para este projeto.
3.  Crie uma **Conta de Serviço** e baixe o arquivo JSON de credenciais.
4.  **Renomeie** o arquivo baixado para `credentials.json` e coloque-o na pasta raiz do projeto (`automation_bot/`).
5.  **Compartilhe a pasta de destino:** No seu Google Drive, crie ou escolha a pasta onde os arquivos serão enviados. Compartilhe esta pasta com o **e-mail da Conta de Serviço** (o e-mail está dentro do arquivo `credentials.json`).
6.  Obtenha o **ID da Pasta** da URL do Drive (ex: `https://drive.google.com/drive/folders/PASTE_ID_AQUI`). Este ID será usado no arquivo `.env`.

## 3. Configuração do Bot do Telegram

1.  Crie um novo bot usando o **BotFather** no Telegram.
2.  Obtenha o **Token de Acesso** do seu bot. Este token será usado no arquivo `.env`.

## 4. Instalação do Projeto

1.  Clone ou baixe este repositório para sua VM.
2.  Navegue até a pasta do projeto:
    ```bash
    cd automation_bot
    ```
3.  Instale as dependências do Python:
    ```bash
    pip install -r requirements.txt
    ```
4.  Instale os navegadores necessários para o Playwright:
    ```bash
    playwright install chromium
    ```

## 5. Configuração das Variáveis de Ambiente

Crie um arquivo chamado `.env` na pasta raiz do projeto (`automation_bot/`) e preencha com suas credenciais e IDs:

```dotenv
# Token do BotFather
TELEGRAM_TOKEN="SEU_TOKEN_DO_TELEGRAM"

# Credenciais do Freepik
FREEPIK_EMAIL="seu_email@freepik.com"
FREEPIK_PASSWORD="sua_senha_freepik"

# Credenciais do Envato Elements
ENVATO_EMAIL="seu_email@envato.com"
ENVATO_PASSWORD="sua_senha_envato"

# ID da pasta de destino no Google Drive
DRIVE_FOLDER_ID="ID_DA_PASTA_DO_GOOGLE_DRIVE"
```

## 6. Execução da Aplicação

Para iniciar o bot, execute o arquivo principal:

```bash
python main.py
```

**Recomendação:** Para manter o bot rodando 24/7 na sua VM, use um gerenciador de processos como `screen`, `tmux` ou `systemd`.

**Exemplo com `screen`:**

1.  Instale o `screen`: `sudo apt install screen`
2.  Crie uma nova sessão: `screen -S bot_session`
3.  Execute o bot: `python main.py`
4.  Desanexe a sessão (o bot continua rodando): Pressione `Ctrl+A` seguido de `D`.
5.  Para reanexar: `screen -r bot_session`

---

## Estrutura do Projeto

```
automation_bot/
├── main.py             # Ponto de entrada e orquestração
├── config.py           # Carrega variáveis de ambiente
├── requirements.txt    # Dependências do Python
├── .env                # Variáveis de ambiente (suas credenciais)
├── credentials.json    # Credenciais da Conta de Serviço do Google Drive
├── README.md           # Este arquivo
└── modules/
    ├── bot.py          # Lógica do Bot do Telegram
    ├── downloader.py   # Automação Web (Playwright) para Freepik/Envato
    └── drive_service.py# Integração com Google Drive API
```
