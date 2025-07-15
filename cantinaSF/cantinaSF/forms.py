from datetime import datetime
from django import forms
from .models import Transaction, Student
from django.utils.translation import gettext_lazy as _

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        # Não remover o request aqui, será tratado na view
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.type = 'credito'
        if commit:
            obj.save()
        return obj


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.for_user = kwargs.pop('for_user', None)  # <- pega e remove o argumento
        super().__init__(*args, **kwargs)

    birthday = forms.DateField(
        label=_("Data de Nascimento"),
        widget=forms.TextInput(attrs={
            'placeholder': 'dd/mm/aaaa',
            'class': 'form-control',
            'autocomplete': 'off'
        }),
        input_formats=['%d/%m/%Y'],
        required=False,
    )

    class Meta:
        model = Student
        fields = ['name', 'last_name', 'birthday', 'plan', 'courses', 'user']

    def clean_birthday(self):
        data = self.cleaned_data.get("birthday")
        if isinstance(data, str):
            try:
                data = datetime.strptime(data, "%d/%m/%Y").date()
            except ValueError:
                raise forms.ValidationError(_("Data inválida. Use o formato dd/mm/aaaa."))
        return data