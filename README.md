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

```bash
pip install -r requirements.txt
```

### 1.2 Configuração local (modo simples: 1 e-mail para tudo)

```bash
export EMAIL_ADDRESS="seuemail@gmail.com"
export EMAIL_APP_PASSWORD="senha-de-app-16-digitos"

export OPENCLAW_API_URL="https://seu-endpoint/v1/chat/completions"
export OPENCLAW_API_KEY="sua_chave"

export CONTINUOUS_MODE="true"
export SEND_TIMES="06:00,24:00"
```

> Para Gmail/Outlook/Hotmail/Live/Yahoo/iCloud, `IMAP_HOST` e `SMTP_HOST` são detectados automaticamente.
> Se seu provedor não estiver nessa lista, defina também:
> `IMAP_HOST="imap.seu-provedor.com"` e `SMTP_HOST="smtp.seu-provedor.com"`.

### 1.3 Executar local

Rodar uma vez:

```bash
python email_agent_openclaw.py
```

Rodar em horário agendado (24/7, enquanto o PC estiver ligado):

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
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ativar:

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
- resumir os itens críticos,
- listar pendências por prioridade,
- indicar o que pode esperar.
