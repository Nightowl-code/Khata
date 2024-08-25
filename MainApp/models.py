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
    date = models.DateField()
    comment = models.TextField(blank=True)

    def __str__(self):
        sign = "" if self.type == "credit" else "-"
        return f"{self.party} -> {sign} {self.amount}"

    def save(self, *args, **kwargs):
        # Determine if this is an update or a new transaction
        if self.pk:  # If primary key exists, it's an update
            print("Updating transaction")
            old_transaction = Transaction.objects.get(pk=self.pk)
            # Reverse the effect of the old transaction
            if old_transaction.type == "credit":
                old_transaction.party.amount -= old_transaction.amount
            else:
                old_transaction.party.amount += old_transaction.amount

            old_transaction.party.amount_type = "credit" if old_transaction.party.amount >= 0 else "debit"
            old_transaction.party.save()
            print("Old transaction effect reversed", old_transaction.party.amount, old_transaction.party.amount_type)
            self.party.refresh_from_db()
        # Apply the effect of the new/updated transaction
        if self.type == "credit":
            self.party.amount += self.amount
        else:
            self.party.amount -= self.amount

        self.party.amount_type = "credit" if self.party.amount >= 0 else "debit"
        self.party.save()
        print("New transaction effect applied", self.party.amount, self.party.amount_type)

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Reverse the effect of the transaction before deleting
        if self.type == "credit":
            self.party.amount -= self.amount
        else:
            self.party.amount += self.amount

        self.party.amount_type = "credit" if self.party.amount >= 0 else "debit"
        self.party.save()

        super().delete(*args, **kwargs)