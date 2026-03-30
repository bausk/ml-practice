import resend

from scoreboard import config


def send_pin_email(to_email: str, pin: str):
    """Send a PIN verification email via Resend."""
    resend.api_key = config.RESEND_API_KEY

    resend.Emails.send({
        "from": config.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Код підтвердження для турнірної таблиці — ЛР №3",
        "text": (
            f"Ваш код підтвердження: {pin}\n\n"
            f"Код дійсний протягом {config.PIN_EXPIRY_MINUTES} хвилин.\n\n"
            "Якщо ви не запитували цей код, проігноруйте цей лист."
        ),
    })
