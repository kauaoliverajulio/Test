#!/usr/bin/env python3
"""Agente para ler e-mails via IMAP e gerar resumo dos mais importantes."""

from __future__ import annotations

import email
import imaplib
import json
import logging
import os
import re
import smtplib
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import EmailMessage
from html import unescape
from typing import List, Tuple

import requests


PROVIDER_HOSTS = {
    "gmail.com": ("imap.gmail.com", "smtp.gmail.com", 587),
    "outlook.com": ("outlook.office365.com", "smtp.office365.com", 587),
    "hotmail.com": ("outlook.office365.com", "smtp.office365.com", 587),
    "live.com": ("outlook.office365.com", "smtp.office365.com", 587),
    "yahoo.com": ("imap.mail.yahoo.com", "smtp.mail.yahoo.com", 587),
    "icloud.com": ("imap.mail.me.com", "smtp.mail.me.com", 587),
}

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("email-agent")


@dataclass
class MailMessage:
    sender: str
    subject: str
    body: str


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _decode_text(value: str | bytes | None) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value

    decoded_parts = decode_header(value)
    chunks: List[str] = []
    for chunk, encoding in decoded_parts:
        if isinstance(chunk, bytes):
            chunks.append(chunk.decode(encoding or "utf-8", errors="ignore"))
        else:
            chunks.append(chunk)
    return "".join(chunks)


def _extract_text(msg: email.message.Message) -> str:
    text_body = ""
    html_body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            disposition = str(part.get("Content-Disposition"))
            if "attachment" in disposition:
                continue

            payload = part.get_payload(decode=True) or b""
            decoded = payload.decode(errors="ignore")
            if content_type == "text/plain" and not text_body:
                text_body = decoded
            elif content_type == "text/html" and not html_body:
                html_body = decoded
    else:
        payload = msg.get_payload(decode=True) or b""
        decoded = payload.decode(errors="ignore")
        if msg.get_content_type() == "text/html":
            html_body = decoded
        else:
            text_body = decoded

    if text_body:
        return text_body

    # fallback simples para HTML
    cleaned = re.sub(r"<[^>]+>", " ", html_body)
    return unescape(cleaned)


def _parse_send_times() -> List[Tuple[int, int]]:
    raw_times = os.getenv("SEND_TIMES", "06:00,24:00")
    parsed: List[Tuple[int, int]] = []

    for item in raw_times.split(","):
        value = item.strip()
        if not value:
            continue
        if value == "24:00":
            value = "00:00"

        try:
            hour_str, minute_str = value.split(":")
            hour = int(hour_str)
            minute = int(minute_str)
        except ValueError as exc:
            raise ValueError(f"Formato inválido em SEND_TIMES: '{item}'. Use HH:MM.") from exc

        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError(f"Horário inválido em SEND_TIMES: '{item}'.")

        parsed.append((hour, minute))

    unique_sorted = sorted(set(parsed))
    if not unique_sorted:
        raise ValueError("SEND_TIMES precisa ter pelo menos um horário.")

    return unique_sorted


def _next_run_time(schedule: List[Tuple[int, int]], now: datetime) -> datetime:
    candidates: List[datetime] = []
    for hour, minute in schedule:
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        candidates.append(candidate)
    return min(candidates)


def _get_email_identity() -> tuple[str, str, str, str, str, str]:
    single_email = os.getenv("EMAIL_ADDRESS")
    single_password = os.getenv("EMAIL_APP_PASSWORD")

    imap_user = os.getenv("IMAP_USER") or single_email
    imap_password = os.getenv("IMAP_PASSWORD") or single_password
    smtp_user = os.getenv("SMTP_USER") or single_email
    smtp_password = os.getenv("SMTP_PASSWORD") or single_password

    if not imap_user or not imap_password or not smtp_user or not smtp_password:
        raise RuntimeError(
            "Configure IMAP_USER/IMAP_PASSWORD e SMTP_USER/SMTP_PASSWORD "
            "ou use EMAIL_ADDRESS + EMAIL_APP_PASSWORD."
        )

    smtp_to = os.getenv("SMTP_TO", smtp_user)
    smtp_from = os.getenv("SMTP_FROM", smtp_user)
    return imap_user, imap_password, smtp_user, smtp_password, smtp_to, smtp_from


def _get_hosts(email_address: str | None) -> tuple[str, str, int]:
    imap_host = os.getenv("IMAP_HOST")
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    if imap_host and smtp_host:
        return imap_host, smtp_host, smtp_port

    if email_address and "@" in email_address:
        domain = email_address.split("@", 1)[1].lower()
        defaults = PROVIDER_HOSTS.get(domain)
        if defaults:
            default_imap, default_smtp, default_port = defaults
            return imap_host or default_imap, smtp_host or default_smtp, int(os.getenv("SMTP_PORT", str(default_port)))

    raise RuntimeError(
        "Defina IMAP_HOST e SMTP_HOST ou use EMAIL_ADDRESS de provedor suportado "
        "(gmail/outlook/hotmail/live/yahoo/icloud)."
    )


def fetch_recent_emails() -> List[MailMessage]:
    user, password, _, _, _, _ = _get_email_identity()
    host, _, _ = _get_hosts(user)
    mailbox = os.getenv("IMAP_MAILBOX", "INBOX")
    limit = int(os.getenv("IMAP_LIMIT", "15"))
    search_criteria = os.getenv("IMAP_SEARCH_CRITERIA", "UNSEEN")

    with imaplib.IMAP4_SSL(host) as conn:
        conn.login(user, password)
        conn.select(mailbox)
        status, data = conn.search(None, search_criteria)
        if status != "OK":
            raise RuntimeError("Falha ao consultar mensagens no IMAP.")

        ids = data[0].split()[-limit:]
        messages: List[MailMessage] = []
        for msg_id in ids:
            _, msg_data = conn.fetch(msg_id, "(RFC822)")
            if not msg_data or not msg_data[0]:
                continue

            raw_email = msg_data[0][1]
            parsed = email.message_from_bytes(raw_email)
            sender = _decode_text(parsed.get("From"))
            subject = _decode_text(parsed.get("Subject"))
            body = _extract_text(parsed)
            body = re.sub(r"\s+", " ", body).strip()

            messages.append(MailMessage(sender=sender, subject=subject, body=body[:3000]))

        return messages


def _local_summary(messages: List[MailMessage]) -> str:
    top = messages[:5]
    lines = [
        "Resumo automático (modo local):",
        "",
        "- resumir os itens críticos:",
    ]
    for msg in top:
        lines.append(f"  • {msg.subject} (de: {msg.sender})")

    lines.extend(
        [
            "",
            "- listar pendências por prioridade:",
            "  • Alta: revisar assuntos com 'urgente', 'prazo', 'vencimento'.",
            "  • Média: responder dúvidas e acompanhamentos.",
            "  • Baixa: newsletters e comunicados gerais.",
            "",
            "- indicar o que pode esperar:",
            "  • Mensagens informativas sem pedido de ação imediata.",
        ]
    )
    return "\n".join(lines)


def _llm_summary(messages: List[MailMessage]) -> str:
    api_url = os.environ["LLM_API_URL"]
    api_key = os.environ["LLM_API_KEY"]
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    prompt_lines = [
        "Você é um assistente que identifica os e-mails mais importantes para ação imediata.",
        "Retorne em português no seguinte formato:",
        "- resumir os itens críticos,",
        "- listar pendências por prioridade,",
        "- indicar o que pode esperar.",
        "",
        "E-mails:",
    ]
    for idx, msg in enumerate(messages, start=1):
        prompt_lines.extend([f"[{idx}] De: {msg.sender}", f"Assunto: {msg.subject}", f"Conteúdo: {msg.body}", ""])

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Você resume e prioriza e-mails com foco em ação."},
            {"role": "user", "content": "\n".join(prompt_lines)},
        ],
        "temperature": 0.2,
    }
    response = requests.post(
        api_url,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise RuntimeError(f"Resposta inesperada do LLM: {data}") from exc


def summarize_important_emails(messages: List[MailMessage]) -> str:
    summary_mode = os.getenv("SUMMARY_MODE", "local").lower()
    if summary_mode == "local":
        return _local_summary(messages)
    if summary_mode == "llm":
        return _llm_summary(messages)
    raise RuntimeError("SUMMARY_MODE inválido. Use 'local' ou 'llm'.")


def send_summary_email(summary: str, total_messages: int) -> None:
    _, _, smtp_user, smtp_password, smtp_to, smtp_from = _get_email_identity()
    _, smtp_host, smtp_port = _get_hosts(smtp_user)
    use_tls = os.getenv("SMTP_USE_TLS", "true").lower() == "true"

    msg = EmailMessage()
    msg["Subject"] = f"Resumo dos e-mails importantes ({total_messages} analisados)"
    msg["From"] = smtp_from
    msg["To"] = smtp_to
    msg.set_content(
        "Resumo automático gerado pelo agente.\n\n"
        f"Total de e-mails analisados: {total_messages}\n\n"
        f"{summary}"
    )

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        if use_tls:
            server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)


def run_once() -> None:
    messages = fetch_recent_emails()
    if not messages:
        logger.info("Nenhum e-mail novo encontrado.")
        return

    summary = summarize_important_emails(messages)
    logger.info("Resumo gerado com sucesso.")
    logger.debug(summary)
    send_summary_email(summary, total_messages=len(messages))
    logger.info("Resumo enviado por e-mail com sucesso.")


def run_forever() -> None:
    schedule = _parse_send_times()
    schedule_text = ", ".join(f"{h:02d}:{m:02d}" for h, m in schedule)
    logger.info("Modo agendado ativo. Horários: %s", schedule_text)

    while True:
        now = datetime.now()
        next_run = _next_run_time(schedule, now)
        sleep_seconds = max(1, int((next_run - now).total_seconds()))
        logger.info("Próxima execução em %s", next_run.strftime("%Y-%m-%d %H:%M:%S"))
        time.sleep(sleep_seconds)

        try:
            run_once()
        except Exception as exc:
            logger.exception("Erro na execução agendada: %s", exc)


def main() -> None:
    continuous_mode = os.getenv("CONTINUOUS_MODE", "false").lower() == "true"
    if continuous_mode:
        run_forever()
        return
    run_once()


if __name__ == "__main__":
    main()
