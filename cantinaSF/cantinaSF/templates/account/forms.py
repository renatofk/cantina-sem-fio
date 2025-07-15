from django import forms
from allauth.account.forms import LoginForm, SignupForm



class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adiciona placeholder ao campo "login"
        self.fields['login'].widget = forms.TextInput(attrs={
            'placeholder': 'Digite o nome de usuário (ex: joao89)',
            'class': 'form-control'
        })


class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': 'Digite o nome de usuário (ex: joao89)',
            'class': 'form-control'
        })