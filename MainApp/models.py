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

    class Meta:
        # Ensure sequence_number is unique for each party
        unique_together = ('party', 'sequence_number')

    def __str__(self):
        sign = "" if self.type == "credit" else "-"
        return f"{self.party} -> {sign} {self.amount}"

    def save(self, *args, **kwargs):
        # Determine the sequence number for the transaction
        if self.sequence_number is None:
            self.set_sequence_number()


        # Get the last transaction for this party to calculate the running total
        last_transaction = Transaction.objects.filter(
            party=self.party, 
            date__lte=self.date
        ).exclude(pk=self.pk).order_by('-date', '-id').first()

        if self.pk:  # If primary key exists, it's an update
            old_transaction = Transaction.objects.get(pk=self.pk)
            if old_transaction.type == "credit":
                old_transaction.party.amount -= old_transaction.amount
            else:
                old_transaction.party.amount += old_transaction.amount

            old_transaction.party.amount_type = "credit" if old_transaction.party.amount >= 0 else "debit"
            old_transaction.party.save()
            # If the date has changed, reset the sequence number
            if old_transaction.date != self.date:
                self.set_sequence_number()
            self.party.refresh_from_db()

        # Calculate the new running total
        if last_transaction:
            if self.type == "credit":
                self.running_total = last_transaction.running_total + self.amount
            else:
                self.running_total = last_transaction.running_total - self.amount
        else:
            self.running_total = self.amount if self.type == "credit" else -self.amount
        
        # Update party's total amount
        if self.type == "credit":
            self.party.amount += self.amount
        else:
            self.party.amount -= self.amount

        self.party.amount_type = "credit" if self.party.amount >= 0 else "debit"
        self.party.save()

        super().save(*args, **kwargs)

        # Update running totals for subsequent transactions
        self.update_subsequent_running_totals()

    def delete(self, *args, **kwargs):
        # Reverse the effect of the transaction before deleting
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
        # get transaction just above it
        transaction_above = Transaction.objects.filter(party=self.party,date__gt=self.date).order_by('date', 'sequence_number').first()
        # get transaction just below it
        transaction_below = Transaction.objects.filter(party=self.party,date__lte=self.date).order_by('-date', '-sequence_number').first()
        if transaction_above and transaction_below:
            self.sequence_number = (transaction_above.sequence_number + transaction_below.sequence_number) / 2
        elif transaction_above:
            self.sequence_number = transaction_above.sequence_number - 1
        elif transaction_below:
            self.sequence_number = transaction_below.sequence_number + 1
        else:
            self.sequence_number = 1


    def update_subsequent_running_totals(self):
        subsequent_transactions = Transaction.objects.filter(
            party=self.party, 
            sequence_number__gt=self.sequence_number
        ).order_by('date', 'sequence_number')

        running_total = self.running_total
        for transaction in subsequent_transactions:
            if transaction.pk != self.pk:
                if transaction.type == "credit":
                    running_total += transaction.amount
                else:
                    running_total -= transaction.amount

                Transaction.objects.filter(pk=transaction.pk).update(running_total=running_total)

