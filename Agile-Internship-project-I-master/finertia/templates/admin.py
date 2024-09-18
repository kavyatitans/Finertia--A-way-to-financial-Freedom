from django.contrib import admin
from .models import AllTransactions, UserData,Card

# Register your models here.

admin.site.register(AllTransactions)
admin.site.register(UserData)
admin.site.register(Card)
