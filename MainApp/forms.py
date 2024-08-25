from django import forms
from . import models

from django import forms
from . import models

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['type', 'amount', 'party', 'comment', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),  # Date picker in the form
        }

    # check if prefill values are provided
    def __init__(self, *args, **kwargs):
        if 'prefill' in kwargs:
            prefill = kwargs.pop('prefill')
            super(TransactionForm, self).__init__(*args, **kwargs)
            for key, value in prefill.items():
                self.fields[key].initial = value
                self.fields[key].widget.attrs['disabled'] = True
        else:
            super(TransactionForm, self).__init__(*args, **kwargs)

        

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


        
    