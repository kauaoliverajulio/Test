# Agente de e-mail com OpenClaw

Este agente:
1. Lê e-mails via IMAP.
2. Resume os mais importantes com OpenClaw.
3. Envia o resumo por SMTP.
4. Pode rodar em horário fixo (`06:00` e `24:00`) 24/7.

## 1) Rodar LOCAL (no seu computador)

### 1.1 Requisitos
- Python 3.10+
- `pip`

Instalar dependência:
Este projeto cria um agente simples em Python para:
1. Ler e-mails de uma caixa IMAP.
2. Enviar os conteúdos para a OpenClaw.
3. Retornar um resumo dos e-mails mais importantes com priorização.
4. Enviar esse resumo automaticamente para o seu e-mail.

## Requisitos

- Python 3.10+
- Credenciais IMAP válidas
- Endpoint/API key da OpenClaw

Instale dependências:

```bash
pip install -r requirements.txt
```

### 1.2 Configuração local (modo simples: 1 e-mail para tudo)

```bash
export EMAIL_ADDRESS="seuemail@gmail.com"
export EMAIL_APP_PASSWORD="senha-de-app-16-digitos"

export OPENCLAW_API_URL="https://seu-endpoint/v1/chat/completions"
export OPENCLAW_API_KEY="sua_chave"

## Configuração

Defina as variáveis de ambiente:

```bash
export IMAP_HOST="imap.seu-provedor.com"
export IMAP_USER="voce@empresa.com"
export IMAP_PASSWORD="sua_senha"
export IMAP_MAILBOX="INBOX"
export IMAP_LIMIT="20"
export IMAP_SEARCH_CRITERIA="UNSEEN"

export OPENCLAW_API_URL="https://api.openclaw.seu-endpoint/v1/chat/completions"
export OPENCLAW_API_KEY="sua_chave"
export OPENCLAW_MODEL="openclaw-chat"

export SMTP_HOST="smtp.seu-provedor.com"
export SMTP_PORT="587"
export SMTP_USER="voce@empresa.com"
export SMTP_PASSWORD="sua_senha_smtp"
export SMTP_TO="voce@empresa.com"
export SMTP_FROM="agente@empresa.com"
export SMTP_USE_TLS="true"

# Modo agendado (24/7)
export CONTINUOUS_MODE="true"
export SEND_TIMES="06:00,24:00"
```

> Para Gmail/Outlook/Hotmail/Live/Yahoo/iCloud, `IMAP_HOST` e `SMTP_HOST` são detectados automaticamente.
> Se seu provedor não estiver nessa lista, defina também:
> `IMAP_HOST="imap.seu-provedor.com"` e `SMTP_HOST="smtp.seu-provedor.com"`.

### 1.3 Executar local

Rodar uma vez:

### Configuração simplificada (1 e-mail para tudo)

Se você quer facilitar, use somente estas variáveis para autenticação:

```bash
export EMAIL_ADDRESS="seuemail@gmail.com"
export EMAIL_APP_PASSWORD="senha-de-app-16-digitos"
```

Com isso, o código usa automaticamente:
- `IMAP_USER = EMAIL_ADDRESS`
- `IMAP_PASSWORD = EMAIL_APP_PASSWORD`
- `SMTP_USER = EMAIL_ADDRESS`
- `SMTP_PASSWORD = EMAIL_APP_PASSWORD`
- `SMTP_TO` e `SMTP_FROM` como o mesmo e-mail, se não forem definidos.

> Você ainda precisa definir `IMAP_HOST`, `SMTP_HOST`, `OPENCLAW_API_URL` e `OPENCLAW_API_KEY`.

## Execução

### Rodar uma vez

```bash
python email_agent_openclaw.py
```

Rodar em horário agendado (24/7, enquanto o PC estiver ligado):
### Rodar em modo agendado (todos os dias às 06:00 e 24:00)

```bash
CONTINUOUS_MODE=true SEND_TIMES="06:00,24:00" python email_agent_openclaw.py
```

---

## 2) Rodar NA NUVEM (sem depender do PC ligado)

## 2.1 Railway (recomendado para começar)

### Passo a passo
1. Suba este projeto no GitHub.
2. Railway → **New Project** → **Deploy from GitHub repo**.
3. Selecione o repositório.
4. Abra o serviço criado → aba **Variables**.
5. Adicione as variáveis abaixo.
6. Deploy.

### Variáveis mínimas (Railway)

```env
EMAIL_ADDRESS=seuemail@gmail.com
EMAIL_APP_PASSWORD=senha-de-app-16-digitos

OPENCLAW_API_URL=https://seu-endpoint/v1/chat/completions
OPENCLAW_API_KEY=sua_chave

CONTINUOUS_MODE=true
SEND_TIMES=06:00,24:00
```

### Variáveis opcionais (Railway)

```env
IMAP_MAILBOX=INBOX
IMAP_LIMIT=15
IMAP_SEARCH_CRITERIA=UNSEEN
OPENCLAW_MODEL=openclaw-chat
SMTP_PORT=587
> `24:00` é tratado como `00:00` (meia-noite do próximo dia).

No modo agendado, o agente fica ligado 24/7 e só executa nos horários definidos em `SEND_TIMES`.

## Rodar na nuvem (sem depender do seu PC)

A forma mais simples é subir este projeto como um serviço containerizado em uma plataforma como **Railway**, **Render** ou **Fly.io**.

### 1) Deploy com Docker (base)

Este repositório já inclui `Dockerfile` e `requirements.txt`.

Build local:

```bash
docker build -t openclaw-email-agent .
```

Run local com variáveis:

```bash
docker run --rm \
  -e IMAP_HOST="..." \
  -e IMAP_USER="..." \
  -e IMAP_PASSWORD="..." \
  -e OPENCLAW_API_URL="..." \
  -e OPENCLAW_API_KEY="..." \
  -e SMTP_HOST="..." \
  -e SMTP_USER="..." \
  -e SMTP_PASSWORD="..." \
  -e CONTINUOUS_MODE="true" \
  -e SEND_TIMES="06:00,24:00" \
  openclaw-email-agent
```

### 2) Railway (mais fácil)

1. Suba este repositório no GitHub.
2. No Railway, clique em **New Project > Deploy from GitHub repo**.
3. Selecione o repositório.
4. Abra o serviço criado e vá em **Variables**.
5. Cadastre **exatamente** as variáveis abaixo.
6. Faça o deploy.

#### Variáveis obrigatórias no Railway

| Variável | Exemplo | Obrigatória? | Observação |
|---|---|---|---|
| `IMAP_HOST` | `imap.gmail.com` | Sim | Host IMAP do provedor |
| `IMAP_USER` | `voce@empresa.com` | Sim* | Usuário IMAP (ou use `EMAIL_ADDRESS`) |
| `IMAP_PASSWORD` | `senha-ou-app-password` | Sim* | Senha IMAP (ou use `EMAIL_APP_PASSWORD`) |
| `OPENCLAW_API_URL` | `https://seu-endpoint/v1/chat/completions` | Sim | Endpoint da OpenClaw |
| `OPENCLAW_API_KEY` | `sk-...` | Sim | Chave da OpenClaw |
| `SMTP_HOST` | `smtp.gmail.com` | Sim | Host SMTP para envio (pode ser Gmail pessoal) |
| `SMTP_USER` | `seuemail@gmail.com` | Sim* | Usuário SMTP (ou use `EMAIL_ADDRESS`) |
| `SMTP_PASSWORD` | `app-password-do-gmail` | Sim* | Senha SMTP (ou use `EMAIL_APP_PASSWORD`) |
| `CONTINUOUS_MODE` | `true` | Sim | Mantém o processo em modo agendado |
| `SEND_TIMES` | `06:00,24:00` | Sim | Horários de envio diário |



\* Você pode preencher direto (`IMAP_USER`/`IMAP_PASSWORD`/`SMTP_USER`/`SMTP_PASSWORD`) **ou** usar o atalho `EMAIL_ADDRESS` + `EMAIL_APP_PASSWORD`.

#### Variáveis opcionais no Railway

| Variável | Padrão | Quando usar |
|---|---|---|
| `IMAP_MAILBOX` | `INBOX` | Se quiser outra pasta de e-mail |
| `IMAP_LIMIT` | `15` | Quantidade máxima de e-mails analisados por execução |
| `IMAP_SEARCH_CRITERIA` | `UNSEEN` | Trocar filtro (ex.: `ALL`) |
| `OPENCLAW_MODEL` | `openclaw-chat` | Se você tiver outro nome de modelo |
| `SMTP_PORT` | `587` | Ajustar porta SMTP |
| `SMTP_TO` | `SMTP_USER` | Destinatário do resumo |
| `SMTP_FROM` | `SMTP_USER` | Remetente exibido |
| `SMTP_USE_TLS` | `true` | Se seu SMTP não usar TLS, ajustar para `false` |
| `EMAIL_ADDRESS` | vazio | Atalho para usar o mesmo e-mail em IMAP e SMTP |
| `EMAIL_APP_PASSWORD` | vazio | Atalho para usar a mesma senha de app em IMAP e SMTP |


#### Posso usar o mesmo e-mail da caixa de entrada?

Sim. Você pode usar o **mesmo e-mail** para ler e para enviar os resumos.

Exemplo (mesma conta):

- `IMAP_USER=seuemail@gmail.com`
- `SMTP_USER=seuemail@gmail.com`
- `SMTP_TO=seuemail@gmail.com`

Se quiser receber em outro endereço, altere apenas `SMTP_TO`.

#### Exemplo para e-mail pessoal (Gmail)

Se você vai enviar para seu e-mail pessoal, use assim no Railway:

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seuemail@gmail.com
SMTP_PASSWORD=senha-de-app-16-digitos
SMTP_TO=seuemail@gmail.com
SMTP_FROM=seuemail@gmail.com
SMTP_USE_TLS=true
```

### Quando precisa informar host manual no Railway?

Só se o domínio do seu e-mail não for suportado automaticamente.
Nesse caso, adicione também:

```env
IMAP_HOST=imap.seu-provedor.com
SMTP_HOST=smtp.seu-provedor.com
```

---

## 2.2 Render (alternativa)

1. **New** → **Background Worker** (ou Web Service).
2. Conecte o repositório.
3. Runtime: Docker (usa o `Dockerfile`).
4. Cadastre as mesmas variáveis do Railway.
5. Deploy em plano que mantenha serviço ligado.

---

## 2.3 VPS/EC2/DigitalOcean (com systemd)

No servidor Linux:

```bash
pip install -r requirements.txt
```
> No Gmail pessoal, ative verificação em 2 etapas e gere uma **Senha de app** em
> Conta Google → Segurança → Senhas de app.

#### Checklist rápido (Railway)

- `CONTINUOUS_MODE=true`
- `SEND_TIMES=06:00,24:00`
- `IMAP_SEARCH_CRITERIA=UNSEEN`
- Todas as credenciais preenchidas sem espaços extras

### 3) Render

1. **New > Web Service** (ou Background Worker).
2. Conecte o repositório.
3. Runtime: Docker (ele usa o `Dockerfile`).
4. Configure as variáveis de ambiente.
5. Deploy com plano que mantenha o serviço sempre ligado.

## Rodar 24/7 como serviço (VM Linux + systemd)

Se preferir VPS/EC2/DigitalOcean:

Crie `/etc/systemd/system/openclaw-email-agent.service`:

```ini
[Unit]
Description=OpenClaw Email Agent
After=network.target

[Service]
Type=simple
User=seu_usuario
WorkingDirectory=/caminho/do/projeto
Environment=CONTINUOUS_MODE=true
Environment=SEND_TIMES=06:00,24:00
EnvironmentFile=/caminho/do/projeto/.env
ExecStart=/usr/bin/python3 /caminho/do/projeto/email_agent_openclaw.py
WorkingDirectory=/workspace/Test
Environment=CONTINUOUS_MODE=true
Environment=SEND_TIMES=06:00,24:00
EnvironmentFile=/workspace/Test/.env
ExecStart=/usr/bin/python3 /workspace/Test/email_agent_openclaw.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar:
Depois:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-email-agent
sudo systemctl status openclaw-email-agent
```

---

## 3) Exemplo `.env` (serve local/nuvem)

```env
EMAIL_ADDRESS=seuemail@gmail.com
EMAIL_APP_PASSWORD=senha-de-app-16-digitos

OPENCLAW_API_URL=https://seu-endpoint/v1/chat/completions
OPENCLAW_API_KEY=sua_chave

CONTINUOUS_MODE=true
SEND_TIMES=06:00,24:00

# opcionais
IMAP_SEARCH_CRITERIA=UNSEEN
SMTP_TO=seuemail@gmail.com
SMTP_FROM=seuemail@gmail.com
SMTP_USE_TLS=true
```

## 4) Observações importantes

- `24:00` é tratado como `00:00` do próximo dia.
- Para Gmail pessoal, use **Senha de app** (não a senha normal da conta).
- Se quiser receber o resumo em outro e-mail, altere apenas `SMTP_TO`.

## 5) Formato do resumo gerado

A OpenClaw recebe instruções para:
## Como o resumo é gerado

O agente monta um prompt com remetente, assunto e conteúdo dos e-mails encontrados e pede para a OpenClaw:

- resumir os itens críticos,
- listar pendências por prioridade,
- indicar o que pode esperar.
