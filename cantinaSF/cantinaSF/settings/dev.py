from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-14n3^6$xsv#a468(&(0&hf%6xjtg#6bpx4q^_2ha7)@5z7-kty"

# SECURITY WARNING: define the correct hosts in production!
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

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

# EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = "in-v3.mailjet.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv("MAILJET_APIKEY", "MAILJET_APIKEY")
EMAIL_HOST_PASSWORD = os.getenv("MAILJET_APISECRET", "API_PRIVATE_KEY")
EMAIL_SENDER = os.getenv("MAILJET_EMAIL_SENDER", "MAILJET_EMAIL_SENDER")
DEFAULT_FROM_EMAIL = 'naoresponda@cantinasemfila.com.br'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
LOGIN_REDIRECT_URL = "/admin/"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Cantina Sem Fila] "

SITE_ID = 1

try:
    from .local import *
except ImportError:
    pass
