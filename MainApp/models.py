from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    amount = models.FloatField(default=0)
    amount_type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')], default='credit')

    def __str__(self):
        return self.username

class Transaction(models.Model):
    type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    amount = models.FloatField()
    party = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    def __str__(self):
        sign = "" if self.type == "credit" else "-"
        return f"{self.party} -> {sign} {self.amount}"
    
    # save the transaction and update the users amount and amoutn_type by computing everything
    def save(self, *args, **kwargs):
        if self.type == "credit":
            self.party.amount += self.amount
        else:
            self.party.amount -= self.amount
        self.party.amount_type = "credit" if self.party.amount >= 0 else "debit"
        self.party.save()
        super().save(*args, **kwargs)