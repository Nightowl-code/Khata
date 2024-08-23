from django import forms
from . import models

class TransactionForm(forms.ModelForm):
    class Meta:
        model = models.Transaction
        fields = ['type', 'amount', 'party', 'comment']

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
    class Meta:
        model = models.CustomUser
        fields = ['username', 'first_name', 'last_name']


        
    