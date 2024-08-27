from django import forms
from . import models
from django.conf import settings
from django.utils.timezone import now

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['type', 'amount', 'party', 'comment', 'date']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        # Extract 'prefill' before calling super().__init__()
        prefill = kwargs.pop('prefill', None)
        super(TransactionForm, self).__init__(*args, **kwargs)

        # Handle factor for amount adjustments
        factor = getattr(settings, 'FACTOR', 0)

        # Apply prefill values and disable fields if necessary
        if prefill:
            for key, value in prefill.items():
                if key in self.fields:
                    self.fields[key].initial = value
                    self.fields[key].widget.attrs['disabled'] = True  # Remember, disabled fields are not submitted

        # Ensure date defaults to today's date if not provided
        if not self.fields['date'].initial:
            self.fields['date'].initial = now().date()

        if self.instance and self.instance.pk:
            # Adjust the amount according to the factor
            adjusted_amount = self.instance.amount * (10 ** factor)
            self.initial['amount'] = adjusted_amount
            self.fields['amount'].initial = adjusted_amount

            # Update the data if amount is not already present (to ensure form shows the adjusted value)
            self.data = self.data.copy()
            if 'amount' not in self.data:
                self.data['amount'] = adjusted_amount

    def clean(self):
        cleaned_data = super().clean()

        # Ensure that disabled fields are not lost; they need to be re-included in cleaned_data
        for field_name in self.fields:
            if self.fields[field_name].widget.attrs.get('disabled'):
                cleaned_data[field_name] = self.initial.get(field_name)

        return cleaned_data

    def save(self, commit=True):
        instance = super(TransactionForm, self).save(commit=False)

        # Re-adjust amount before saving if a factor is used
        factor = getattr(settings, 'FACTOR', 0)
        if factor:
            instance.amount = instance.amount / (10 ** factor)

        if commit:
            instance.save()

        return instance


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")
    active = forms.BooleanField(required=False, label="Is Active")  # Add the active field

    class Meta:
        model = models.CustomUser
        fields = ['username', 'first_name', 'last_name','active', 'password']  # Include the active field

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


        
    