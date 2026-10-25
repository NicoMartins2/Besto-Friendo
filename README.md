# BestoFriendo

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
