# Telegram Acesso Bot — InfinityPay

## Variáveis de ambiente (configurar no Render)

| Variável | Descrição |
|---|---|
| BOT_TOKEN | Token do seu bot (@BotFather) |
| GROUP_ID | ID do grupo (número negativo, ex: -1001234567890) |
| SMTP_EMAIL | Seu e-mail Gmail |
| SMTP_PASSWORD | Senha de app do Gmail |

## Endpoint do Webhook

Após deploy, cole esta URL na InfinityPay:
```
https://SEU-APP.onrender.com/webhook
```

## Como pegar o GROUP_ID

1. Adicione @userinfobot no grupo
2. Envie qualquer mensagem
3. Ele responde com o ID do grupo
