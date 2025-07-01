from django import forms
from .models import Transaction

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


    # def save(self, commit=True):
    #     instance = super().save(commit=False)
    #     instance.type = 'credito'  # força o valor
    #     if commit:
    #         instance.save()
    #     return instance