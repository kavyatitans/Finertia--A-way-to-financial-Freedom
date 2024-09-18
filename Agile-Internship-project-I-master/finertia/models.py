from django.db import models
from django.contrib.auth.models import User


class AllTransactions(models.Model):
    date = models.DateTimeField()
    mode = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100)
    note = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    income_expense = models.CharField(max_length=20)
    currency = models.CharField(max_length=3)

    def __str__(self):
        return f"{self.date} - {self.category} - {self.amount} {self.currency}"


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    transactions = models.ManyToManyField(AllTransactions)

    def __str__(self):
        return self.user.username


class Card(AllTransactions):
    card_number = models.IntegerField(max_length=16)
    cvv_number = models.IntegerField(max_length=3)

    def __str__(self):
        return f"{self.card_number} - {self.cvv_number}"


