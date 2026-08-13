import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from .base import *
APP_DOMAIN = os.getenv("APP_DOMAIN", "http://localhost:8000")
CARAPASSA_APP_URL = os.getenv("CARAPASSA_APP_URL", "http://localhost:8001")
CARAPASSA_FACE_STATUS_URL = os.getenv(
    "CARAPASSA_FACE_STATUS_URL",
    f"{CARAPASSA_APP_URL.rstrip('/')}/v1/subjects/face-status",
)
CARAPASSA_DELETE_SUBJECT_URL = os.getenv(
    "CARAPASSA_DELETE_SUBJECT_URL",
    f"{CARAPASSA_APP_URL.rstrip('/')}/v1/subjects/{{subject_id}}",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-14n3^6$xsv#a468(&(0&hf%6xjtg#6bpx4q^_2ha7)@5z7-kty"

KIOSK_SECRET_KEY = os.getenv("KIOSK_SECRET_KEY")
# SECURITY WARNING: define the correct hosts in production!
# ALLOWED_HOSTS = ["*"]

# EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "cantinaSF"),
        "USER": os.getenv("DB_USER", "postgres"),
        "PASSWORD": os.getenv("DB_PASSWORD", "root"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

ACCOUNT_FORMS = {
    'login': 'cantinaSF.templates.account.forms.CustomLoginForm',
    'signup': 'cantinaSF.templates.account.forms.CustomSignupForm',
}

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = "in-v3.mailjet.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("MAILJET_API_KEY")
EMAIL_HOST_PASSWORD = os.getenv("MAILJET_API_SECRET", "API_PRIVATE_KEY")
EMAIL_SENDER = os.getenv("MAILJET_EMAIL_SENDER", "MAILJET_EMAIL_SENDER")
DEFAULT_FROM_EMAIL = 'naoresponda@cantinasemfila.com.br'

# EMAIL_BACKEND = 'django_mailjet.backends.MailjetBackend'
# MAILJET_API_KEY = os.getenv("MAILJET_API_KEY")
# MAILJET_API_SECRET = os.getenv("MAILJET_API_SECRET", "API_PRIVATE_KEY")
# DEFAULT_FROM_EMAIL = 'naoresponda@cantinasemfila.com.br'
# EMAIL_HOST_USER = 'naoresponda@cantinasemfila.com.br'
# EMAIL_HOST_USER_NAME = f'Cantina Sem Fila <{EMAIL_HOST_USER}>'

SITE_ID = 1

try:
    from .local import *
except ImportError:
    pass
