from django.core.management.base import BaseCommand
from MainApp.models import Transaction, CustomUser
from django.db import transaction as db_transaction

class Command(BaseCommand):
    help = "Correct running totals and user balances for all transactions."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the correction of transactions...")

        with db_transaction.atomic():
            # Iterate over all users
            users = CustomUser.objects.all()
            for user in users:
                self.stdout.write(f"Processing user: {user.username} (ID: {user.id})")
                
                # Fetch all transactions for the user, ordered by date and sequence_number
                user_transactions = Transaction.objects.filter(party=user).order_by('date', 'sequence_number')

                running_total = 0
                for txn in user_transactions:
                    # Adjust running total for each transaction
                    if txn.type == "credit":
                        running_total += txn.amount
                    else:
                        running_total -= txn.amount

                    # Update the transaction's running total
                    txn.running_total = running_total
                    txn.save(update_fields=['running_total'])

                # Update user's total amount and amount type
                user.amount = running_total
                user.amount_type = "credit" if running_total >= 0 else "debit"
                user.save(update_fields=['amount', 'amount_type'])

        self.stdout.write("Transaction correction completed successfully!")
