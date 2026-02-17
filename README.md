# Agente de e-mail com OpenClaw

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

## Execução

### Rodar uma vez

```bash
python email_agent_openclaw.py
```

### Rodar em modo agendado (todos os dias às 06:00 e 24:00)

```bash
CONTINUOUS_MODE=true SEND_TIMES="06:00,24:00" python email_agent_openclaw.py
```

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
4. Em **Variables**, adicione todas as variáveis de ambiente do bloco de configuração.
5. Garanta que `CONTINUOUS_MODE=true` e `SEND_TIMES=06:00,24:00`.
6. Deploy.

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

Depois:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-email-agent
sudo systemctl status openclaw-email-agent
```

## Como o resumo é gerado

O agente monta um prompt com remetente, assunto e conteúdo dos e-mails encontrados e pede para a OpenClaw:

- resumir os itens críticos,
- listar pendências por prioridade,
- indicar o que pode esperar.
