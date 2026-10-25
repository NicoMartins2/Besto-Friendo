# BestoFriendo

[English](#english) | [Português](#português)

## English

A Python Discord bot with slash commands (`/`), independent per-server configuration, and support for multiple LLM APIs. Main file: **bot.py**.

### Getting started

1. Create an application and its bot in the [Discord Developer Portal](https://discord.com/developers/applications). Under **Bot**, enable **Message Content Intent**. Never share your token.
2. In OAuth2/URL Generator or Installation, include the **bot** and **applications.commands** scopes. Invite the bot with **View Channels**, **Send Messages**, **Read Message History**, **Attach Files**, and, if using threads, **Send Messages in Threads**. Administrator permission is not required. Your user must be allowed to use application commands.
3. Copy `.env.example` to `.env` if you have not configured it yet. An initially empty `.env` is included with this project; do not overwrite an existing configured file. Set `DISCORD_TOKEN` and the chosen provider's API key **only in the local file**.
4. Open a terminal in this folder and run `python bot.py`. Press Ctrl+C to stop. The host computer must remain powered on and connected.
5. In your server, configure the bot, for example: `/config api:openai modelo:gpt-4o-mini agente:You are a programming tutor. Answer in English.` Then use `/ask pergunta:Explain Python functions`.

**Command option names remain in Portuguese** (`pergunta`, `modelo`, `agente`, `tom`, and `confirmar`); use them exactly as shown. This English README does not change the bot's interface language.

The interpreter used during development already had the main dependencies installed. On another machine, use Python 3.11+ and a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python bot.py
```

If your Python installation does not include `pip`, install a complete Python distribution, or use `uv venv` and `uv pip install --python .venv/Scripts/python.exe -r requirements.txt` if uv is available. Dependencies are not required just to edit the files.

### Commands

| Command | Purpose |
|---|---|
| `/ask pergunta:` | Sends the question and agent instructions to the API; replies publicly in the channel. |
| `/model` | Privately shows the current provider and model. |
| `/config` | Shows the configuration in a private file, without credentials. |
| `/config api: modelo: agente:` | Changes the API, model, and agent instructions for this server. Requires **Manage Server**. Omitted fields are preserved; when changing the API, also specify the model. |
| `/tone` | Shows the current tone. |
| `/tone tom:humorous and concise` | Changes the server's tone; requires **Manage Server**. |
| `/resume confirmar:True` | Summarizes all accessible text history in the current channel/thread before the command. Requires **Manage Server**, permission to read history, and explicit consent. |
| `/help` | Shows help and privacy information. |

The bot introduces itself when joining a server, in the system channel or the first channel where it can send messages. It posts another introduction after saving `/config`. If the bot was offline when added, run `/config` with parameters after starting it to publish the introduction. Saving the configuration **does not guarantee that the key or model is valid**: the first request establishes the connection.

### Providers

- `openai`: `OPENAI_API_KEY`.
- `anthropic`: `ANTHROPIC_API_KEY` (native Messages API).
- `gemini`: `GEMINI_API_KEY` (OpenAI-compatible endpoint).
- `groq`: `GROQ_API_KEY`.
- `openrouter`: `OPENROUTER_API_KEY`.
- `ollama`: local Ollama at `http://localhost:11434/v1`; override the address with `OLLAMA_BASE_URL`. Use a model you have already downloaded in Ollama.
- `custom`: `CUSTOM_BASE_URL` and `CUSTOM_API_KEY` for an OpenAI Chat Completions-compatible endpoint. The URL must include the API prefix, usually `/v1`, not `/chat/completions`.

Model IDs must match those available to your account. The OpenAI default is `gpt-4o-mini`, a configurable example, not a guarantee of availability. Models intended exclusively for audio, images, the Responses API, or parameters incompatible with Chat Completions may not work.

Credentials belong to the **host** and are shared by servers using the same provider. There is no API-key entry through Discord or per-server key vault. Install the bot only in trusted servers and set spending limits in your provider dashboards.

### History and privacy

- `/ask` handles an independent question: it does not automatically send the entire channel or maintain conversational memory between questions.
- `/resume` paginates through all accessible history without a fixed recent-message limit, processes chunks, and combines summaries. The result is a synthesis, not a transcript or a guarantee that every detail is preserved.
- It includes text from human and bot messages, display names, author IDs, and timestamps. It excludes attachment/image/embed contents, deleted messages, messages sent after the command, other channels, and child threads.
- Notify participants before transmitting history. Answers and summaries are posted in the same channel; the start confirmation is private.
- Large histories may require many API calls. The bot allows one concurrent summary per server, limits concurrent API calls, and applies question and summary cooldowns. **There is no spending cap or resume-after-restart capability**. Stopping the process cancels ongoing work but does not undo already billed calls.
- Configuration is stored in `data/config.sqlite3`; messages and summaries are processed in memory, not saved to disk by the bot. Discord and API providers may retain content according to their policies.
- Tokens are stored as plain text in `.env` on the host; protect the file and do not commit it to Git. Error messages do not expose raw API responses. Generated replies do not trigger mentions.

### Tests and troubleshooting

```powershell
python -m unittest discover -v
python bot.py --check
```

Local tests use simulated HTTP transports and Discord interactions. They do not establish real authentication, model availability, or Discord connectivity. `--check` verifies imports without connecting to APIs.

If commands do not appear, check the `applications.commands` scope, permissions, and synchronization. The optional `DISCORD_GUILD_ID` registers commands only in the specified test server; leaving it empty registers them globally, which may take time to propagate. Restart after changing `.env`. If duplicates appear when switching between test and global synchronization, remove the old commands through the appropriate dashboard/API.

If history is empty, check **Message Content Intent**, channel access, and **Read Message History**. The key must match the chosen API, have available quota, and allow the requested model.

### Files

- `bot.py`: Discord commands, introductions, permissions, and execution.
- `llm.py`: API clients, retries, and hierarchical summarization.
- `storage.py`: per-server configuration in SQLite.
- `test_*.py`: automated local tests.
- `.env.example` / `.env`: environment variables.
- `requirements.txt`: dependencies.

---

## Português

Bot Discord em Python com comandos de barra (`/`), configuração independente por servidor e múltiplas APIs de LLMs. Arquivo principal: **bot.py**.

## Iniciar

1. No [Discord Developer Portal](https://discord.com/developers/applications), crie uma aplicação e seu bot. Na seção **Bot**, habilite **Message Content Intent**. Nunca compartilhe o token.
2. Em OAuth2/URL Generator ou Installation, inclua os escopos **bot** e **applications.commands**. Convide o bot com **View Channels**, **Send Messages**, **Read Message History**, **Attach Files** e, se usar threads, **Send Messages in Threads**. Não é necessário conceder Administrator. Seu usuário deve ter permissão de usar comandos de aplicativos.
3. Copie `.env.example` para `.env` (um `.env` vazio já acompanha este projeto) e preencha `DISCORD_TOKEN` e a chave da API escolhida **somente no arquivo local**.
4. No terminal aberto nesta pasta, execute `python bot.py`. Para interromper: Ctrl+C. O computador precisa permanecer ligado e conectado.
5. No servidor, configure, por exemplo: `/config api:openai modelo:gpt-4o-mini agente:Você é um tutor de programação.` Depois use `/ask pergunta:Explique funções em Python`.

O interpretador usado na criação já tinha as dependências principais instaladas. Para outra máquina, use Python 3.11+ e um ambiente virtual:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python bot.py
```

Se o Python não tiver `pip`, instale uma distribuição completa do Python ou use `uv venv` e `uv pip install --python .venv/Scripts/python.exe -r requirements.txt`, caso tenha uv. Não precisa instalar dependências para simplesmente editar os arquivos.

## Comandos

| Comando | Função |
|---|---|
| `/ask pergunta:` | Envia a pergunta e as instruções do agente à API; responde publicamente no canal. |
| `/model` | Mostra provedor e modelo atual, privadamente. |
| `/config` | Mostra a configuração em arquivo privado, sem credenciais. |
| `/config api: modelo: agente:` | Modifica API, modelo e instruções do agente neste servidor. Requer **Gerenciar servidor**. Campos omitidos são preservados; ao trocar API, informe também modelo. |
| `/tone` | Mostra o tom atual. |
| `/tone tom:bem-humorado e objetivo` | Altera o tom para o servidor; requer **Gerenciar servidor**. |
| `/resume confirmar:True` | Resume todo o histórico textual acessível do canal/thread atual, anterior ao comando. Requer **Gerenciar servidor**, leitura de histórico e consentimento explícito. |
| `/help` | Mostra ajuda e informações de privacidade. |

O bot se apresenta ao entrar em um servidor, no canal de sistema ou primeiro canal onde puder falar. Publica outra apresentação após salvar `/config`. Se não estava online ao ser adicionado, use `/config` com parâmetros após iniciar para publicar a apresentação. O salvamento da configuração **não garante que a chave/modelo sejam válidos**: a primeira chamada efetua a conexão.

## Provedores

- `openai`: `OPENAI_API_KEY`.
- `anthropic`: `ANTHROPIC_API_KEY` (API nativa de mensagens).
- `gemini`: `GEMINI_API_KEY` (endpoint compatível com OpenAI).
- `groq`: `GROQ_API_KEY`.
- `openrouter`: `OPENROUTER_API_KEY`.
- `ollama`: Ollama local em `http://localhost:11434/v1`; `OLLAMA_BASE_URL` pode alterar o endereço. Use um modelo que você já baixou no Ollama.
- `custom`: `CUSTOM_BASE_URL` e `CUSTOM_API_KEY`, para um endpoint compatível com OpenAI Chat Completions. A URL deve incluir o prefixo da API, normalmente `/v1`, não `/chat/completions`.

IDs de modelos precisam corresponder aos disponíveis na sua conta. O padrão OpenAI é `gpt-4o-mini`, um exemplo configurável, não uma garantia de disponibilidade. Modelos exclusivamente de áudio, imagem, Responses API ou com parâmetros incompatíveis com Chat Completions podem não funcionar.

As credenciais são do **host**, compartilhadas entre servidores que escolhem o mesmo provedor. Não há entrada de chaves pelo Discord nem cofre de chaves por servidor. Instale somente em servidores confiáveis e defina limites de gasto no painel dos provedores.

## Histórico e privacidade

- `/ask` é uma pergunta independente: não envia automaticamente todo o canal nem mantém memória conversacional entre perguntas.
- `/resume` pagina todo o histórico acessível, sem limite fixo de últimas mensagens, processa blocos e combina resumos. O resultado é uma síntese, não uma transcrição nem uma garantia de preservar todos os detalhes.
- Inclui texto de mensagens de pessoas e bots, nomes de exibição, IDs de autores e horários. Não inclui conteúdo de anexos/imagens/embeds, mensagens apagadas, mensagens posteriores ao comando, outros canais ou threads filhas.
- Avise os participantes antes de transmitir o histórico. Respostas e resumos são publicados no mesmo canal; a confirmação de início é privada.
- Históricos grandes podem custar muitas chamadas. Há um resumo simultâneo por servidor, limite de concorrência de chamadas, cooldown de perguntas e de resumo. **Não existe teto de gastos nem retomada após reinício**. Interromper o processo cancela o trabalho em andamento, mas não desfaz chamadas já cobradas.
- Dados de configuração ficam em `data/config.sqlite3`; mensagens e resumos são processados em memória, não armazenados pelo bot em disco. O Discord e os provedores podem guardar conteúdo conforme suas políticas.
- Tokens ficam em `.env`, em texto simples no computador; proteja o arquivo e não o envie ao Git. Mensagens de erro não expõem respostas cruas das APIs. Respostas geradas não disparam menções.

## Testes e diagnóstico

```powershell
python -m unittest discover -v
python bot.py --check
```

Testes locais usam transportes HTTP e interações Discord simulados. Não comprovam autenticação real, disponibilidade de modelos nem conexão ao Discord. `--check` verifica imports sem conectar às APIs.

Se comandos não aparecerem, confira o escopo `applications.commands`, permissões e sincronização. `DISCORD_GUILD_ID` opcional registra comandos apenas no servidor de testes indicado; vazio registra globalmente e a propagação pode demorar. Reinicie após alterar `.env`. Não mude entre sincronização de teste e global sem remover comandos antigos pelo painel/API se aparecerem duplicados.

Se o histórico vier vazio, confira **Message Content Intent**, acesso ao canal e **Read Message History**. A chave deve corresponder à API escolhida, ter cota e permitir o modelo solicitado.

## Arquivos

- `bot.py`: comandos Discord, apresentações, permissões e execução.
- `llm.py`: APIs, retentativas e resumo hierárquico.
- `storage.py`: configuração por servidor em SQLite.
- `test_*.py`: testes automatizados locais.
- `.env.example` / `.env`: variáveis de ambiente.
- `requirements.txt`: dependências.
