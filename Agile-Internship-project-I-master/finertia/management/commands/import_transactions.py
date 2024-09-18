import csv
import os
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from finertia.models import AllTransactions

class Command(BaseCommand):
    help = 'Import transactions from CSV file into AllTransactions model'

    def handle(self, *args, **options):
        csv_file_path = os.path.join(settings.BASE_DIR, 'Daily_Household_Transactions.csv')

        if not os.path.exists(csv_file_path):
            raise CommandError(f"CSV file does not exist at path: {csv_file_path}")

        with open(csv_file_path, 'r') as file:
            reader = csv.DictReader(file)
            imported_data = []  # Changed the variable name here
            for row in reader:
                # Try parsing with time first, if it fails, parse only the date
                try:
                    date = datetime.strptime(row['Date'], '%d/%m/%Y %H:%M:%S')
                except ValueError:
                    date = datetime.strptime(row['Date'], '%d/%m/%Y')

                entry = AllTransactions(  # Changed variable name to entry
                    date=date,
                    mode=row['Mode'],
                    category=row['Category'],
                    subcategory=row['Subcategory'],
                    note=row['Note'],
                    amount=float(row['Amount']),
                    income_expense=row['Income/Expense'],
                    currency=row['Currency']
                )
                imported_data.append(entry)  # Updated to use the new variable name

            # Bulk create all transactions
            with transaction.atomic():
                AllTransactions.objects.bulk_create(imported_data)  # Updated to use the new variable name

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(imported_data)} transactions from CSV'))