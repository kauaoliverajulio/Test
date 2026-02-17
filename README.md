# Agente de e-mail (sem OpenClaw obrigatório)

Você pediu sem OpenClaw — então o projeto agora roda em dois modos:

- `SUMMARY_MODE=local` (**padrão**): resumo local, sem API externa.
- `SUMMARY_MODE=llm`: usa qualquer API compatível com chat completions (`LLM_API_URL` + `LLM_API_KEY`).

## 1) Configuração mínima (1 e-mail para tudo)

```env
EMAIL_ADDRESS=seuemail@gmail.com
EMAIL_APP_PASSWORD=senha-de-app-16-digitos

SUMMARY_MODE=local

CONTINUOUS_MODE=true
SEND_TIMES=06:00,24:00
```

> Para Gmail/Outlook/Hotmail/Live/Yahoo/iCloud, IMAP/SMTP host são detectados automaticamente.

## 2) Se quiser usar LLM (opcional)

```env
SUMMARY_MODE=llm
LLM_API_URL=https://seu-endpoint/v1/chat/completions
LLM_API_KEY=sua_chave
LLM_MODEL=gpt-4o-mini
```

## 3) Dependências

```bash
pip install -r requirements.txt
```

## 4) Rodar local

Uma vez:

```bash
python email_agent_openclaw.py
```

Agendado 24/7 (enquanto máquina ligada):

```bash
CONTINUOUS_MODE=true SEND_TIMES="06:00,24:00" python email_agent_openclaw.py
```

## 5) Rodar na nuvem (Railway/Render)

Use as mesmas variáveis `.env` acima no painel de variáveis do serviço.

Variáveis obrigatórias para modo sem OpenClaw:

```env
EMAIL_ADDRESS=seuemail@gmail.com
EMAIL_APP_PASSWORD=senha-de-app-16-digitos
SUMMARY_MODE=local
CONTINUOUS_MODE=true
SEND_TIMES=06:00,24:00
```

## 6) Conta com 2FA

Se tiver 2 fatores, use **senha de app** em `EMAIL_APP_PASSWORD`.
Senha normal da conta geralmente falha em IMAP/SMTP.
