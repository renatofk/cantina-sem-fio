# em um arquivo forms.py em seu app
from django import forms
from wagtail.images.forms import ImageForm

class CameraEnabledImageForm(ImageForm):
    """Form para a imagem Wagtail com captura por câmera"""
    pass  # Vamos usar apenas o template customizado