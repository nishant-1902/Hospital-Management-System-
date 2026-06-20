from django.conf import settings
from django.core.mail import send_mail

from ahms.celery import app


@app.task
def send_password_reset_email(email, reset_url):
    subject = "AHMS password reset"
    message = (
        "A password reset was requested for your AHMS account.\n\n"
        f"Use this secure link to set a new password:\n{reset_url}\n\n"
        "If you did not request this, you can ignore this email."
    )
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)
