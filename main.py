import os
import hmac
import hashlib
import smtplib
import logging
from email.mime.text import MIMEText
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_ID = os.environ.get("GROUP_ID")
SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))


def gerar_link_convite():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/createChatInviteLink"
    payload = {
        "chat_id": GROUP_ID,
        "member_limit": 1,
        "creates_join_request": False
    }
    r = requests.post(url, json=payload)
    data = r.json()
    if data.get("ok"):
        return data["result"]["invite_link"]
    logging.error(f"Erro ao gerar link: {data}")
    return None


def enviar_email(destinatario, nome, link):
    assunto = "Seu acesso ao grupo foi liberado!"
    corpo = f"""Olá, {nome}!

Seu pagamento foi confirmado. Clique no link abaixo para entrar no grupo exclusivo:

{link}

⚠️ Este link é único e de uso pessoal. Não compartilhe.

Boas-vindas!
"""
    msg = MIMEText(corpo, "plain", "utf-8")
    msg["Subject"] = assunto
    msg["From"] = SMTP_EMAIL
    msg["To"] = destinatario

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.sendmail(SMTP_EMAIL, destinatario, msg.as_string())
        logging.info(f"E-mail enviado para {destinatario}")
        return True
    except Exception as e:
        logging.error(f"Erro ao enviar e-mail: {e}")
        return False


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "sem dados"}), 400

    logging.info(f"Webhook recebido: {data}")

    # Extrai dados do comprador
    customer = data.get("customer", {})
    nome = customer.get("name", "Cliente")
    email = customer.get("email")
    telefone = customer.get("phone_number")
    pago = data.get("paid", False)

    if not pago:
        return jsonify({"status": "pagamento nao confirmado"}), 200

    if not email:
        logging.warning("E-mail do comprador não encontrado no webhook")
        return jsonify({"error": "email nao encontrado"}), 400

    # Gera link único de convite
    link = gerar_link_convite()
    if not link:
        return jsonify({"error": "falha ao gerar link"}), 500

    # Envia por e-mail
    enviado = enviar_email(email, nome, link)

    return jsonify({
        "status": "ok",
        "email_enviado": enviado,
        "telefone": telefone
    }), 200


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "online"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
