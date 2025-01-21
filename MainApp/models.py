from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    amount = models.FloatField(default=0)
    amount_type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')], default='credit')
    block_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username


class Transaction(models.Model):
    type = models.CharField(max_length=10, choices=[('credit', 'Credit'), ('debit', 'Debit')])
    amount = models.FloatField()
    party = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    date = models.DateField()
    comment = models.TextField(blank=True)
    running_total = models.FloatField(default=0)
    sequence_number = models.FloatField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_transactions')

    class Meta:
        unique_together = ('party', 'sequence_number')

    def __str__(self):
        sign = "" if self.type == "credit" else "-"
        return f"{self.party} -> {sign} {self.amount}"

    def save(self, *args, **kwargs):
        # Determine the sequence number if it hasn’t been set
        if self.sequence_number is None:
            self.set_sequence_number()

        # Retrieve the previous version of this transaction if it exists
        old_amount = 0
        if self.pk:
            old_transaction = Transaction.objects.get(pk=self.pk)
            old_amount = old_transaction.amount if old_transaction.type == self.type else -old_transaction.amount

        # Calculate the running total based on the previous transaction (if any)
        last_transaction = Transaction.objects.filter(
            party=self.party,
            date__lte=self.date,
            sequence_number__lte=self.sequence_number
        ).exclude(pk=self.pk).order_by('-date', '-sequence_number').first()

        print("last_transaction",last_transaction)

        if last_transaction:
            # Adjust running total based on the last transaction's running total
            self.running_total = last_transaction.running_total + (self.amount if self.type == "credit" else -self.amount)
        else:
            # This is the first transaction, set initial running total
            self.running_total = self.amount if self.type == "credit" else -self.amount

        # Calculate the amount difference to update the party’s total amount correctly
        amount_difference = self.amount - old_amount
        if self.type == "debit":
            amount_difference = -amount_difference  # Reverse sign for debits

        # Adjust the party's total amount
        self.party.amount += amount_difference
        self.party.amount_type = "credit" if self.party.amount >= 0 else "debit"
        self.party.save()

        # Save the transaction with the new running total
        super().save(*args, **kwargs)

        # Update running totals for all subsequent transactions to reflect the adjusted amount
        self.update_subsequent_running_totals()

    def delete(self, *args, **kwargs):
        # Adjust the party's amount before deleting the transaction
        if self.type == "credit":
            self.party.amount -= self.amount
        else:
            self.party.amount += self.amount

        self.party.amount_type = "credit" if self.party.amount >= 0 else "debit"
        self.party.save()

        super().delete(*args, **kwargs)

        # Update running totals for subsequent transactions after deletion
        self.update_subsequent_running_totals()

    def set_sequence_number(self):
        # Find the closest transactions above and below the current transaction date
        transaction_above = Transaction.objects.filter(
            party=self.party, date__gt=self.date
        ).order_by('date', 'sequence_number').first()

        transaction_below = Transaction.objects.filter(
            party=self.party, date__lte=self.date
        ).order_by('-date', '-sequence_number').first()

        if transaction_above and transaction_below:
            self.sequence_number = (transaction_above.sequence_number + transaction_below.sequence_number) / 2
        elif transaction_above:
            self.sequence_number = transaction_above.sequence_number - 1
        elif transaction_below:
            self.sequence_number = transaction_below.sequence_number + 1
        else:
            self.sequence_number = 1

    def update_subsequent_running_totals(self):
        # Fetch all subsequent transactions in the correct order
        subsequent_transactions = Transaction.objects.filter(
            party=self.party,
            sequence_number__gt=self.sequence_number
        ).order_by('date', 'sequence_number')

        # if previous transaction
        transaction_below = Transaction.objects.filter(
            party=self.party, date__lte=self.date
        ).order_by('-date', '-sequence_number').first()

        # check if transaction_below is null
        if transaction_below:
            running_total = transaction_below.running_total
        else:
            running_total =0

        print(subsequent_transactions)

    
        for transaction in subsequent_transactions:
            # Adjust running total for each subsequent transaction
            if transaction.type == "credit":
                running_total += transaction.amount
            else:
                running_total -= transaction.amount

            # Update only the running total for each transaction
            Transaction.objects.filter(pk=transaction.pk).update(running_total=running_total)

        # update the parties total amount
        CustomUser.objects.filter(pk=self.party.pk).update(amount=running_total)
        if running_total >= 0:
            CustomUser.objects.filter(pk=self.party.pk).update(amount_type="credit")
        else:
            CustomUser.objects.filter(pk=self.party.pk).update(amount_type="debit")



class SiteSettings(models.Model):
    is_site_available = models.BooleanField(default=True)
    superuser_login_url = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Check if an instance already exists
        if SiteSettings.objects.exists():
            # If so, update the existing instance
            self.pk = SiteSettings.objects.first().pk
        super().save(*args, **kwargs)
    
    def __str__(self):
        return "Site Settings"