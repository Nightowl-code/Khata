from django import forms
from . import models
from django.conf import settings

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['type', 'amount', 'party', 'comment', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(TransactionForm, self).__init__(*args, **kwargs)

        factor = getattr(settings, 'FACTOR', 0)

        if 'prefill' in kwargs:
            prefill = kwargs.pop('prefill')
            for key, value in prefill.items():
                self.fields[key].initial = value
                self.fields[key].widget.attrs['disabled'] = True
        
        if self.instance and self.instance.pk:
            adjusted_amount = self.instance.amount * (10 ** factor)
            # Override the initial value for the amount field
            self.initial['amount'] = adjusted_amount
            self.fields['amount'].initial = adjusted_amount

            # Ensure that the field reflects this change by rendering it unbound
            self.data = self.data.copy()
            if 'amount' not in self.data:
                self.data['amount'] = adjusted_amount

    def save(self, commit=True):
        instance = super(TransactionForm, self).save(commit=False)

        factor = getattr(settings, 'FACTOR', 0)
        if factor:
            instance.amount = instance.amount / (10 ** factor)

        if commit:
            instance.save()

        return instance


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = models.CustomUser
        fields = ['username', 'first_name', 'last_name', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        user.set_password(password)  # Hash the password
        if commit:
            user.save()
        return user


        
    