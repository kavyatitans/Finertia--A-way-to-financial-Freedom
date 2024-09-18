from django.contrib.auth import authenticate, logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

from django.contrib.auth.decorators import login_required
from .forms import FinancialForm, TransferForm, BillPaymentForm
from .MLmodel import classify_financial_status_and_suggest_plan
import pandas as pd
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from .models import UserData, AllTransactions,Card
import random
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone


class SignupView(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/signup.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Create UserData instance
            user_data = UserData.objects.create(user=user)

            # Get 15 random transactions
            all_transactions = list(AllTransactions.objects.all())
            random_transactions = random.sample(all_transactions, 15)

            # Add transactions to user_data
            user_data.transactions.add(*random_transactions)
            print('here')
            return redirect('finertia:dashboard')

        return render(request, 'registration/signup.html', {'form': form})


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user)
                return redirect('finertia:dashboard')
        return render(request, 'registration/login.html', {'form': form})


def home(request):
    return render(request, 'home.html')


# @login_required
# def dashboard(request):
#     user_data = UserData.objects.get(user=request.user)
#     user_transactions = user_data.transactions.all()
#     context = {
#         'transactions': user_transactions,
#         'username': request.user.username  # Add this line
#     }
#     return render(request, 'dashboard.html', context)


def dashboard(request):
    user_data = UserData.objects.get(user=request.user)
    user_transactions = user_data.transactions.all()

    # Calculate spending by category
    # category_spending = user_transactions.filter(income_expense='Expense').values('category').annotate(
    #     total=Coalesce(Sum('amount', output_field=DecimalField()), 0)
    # ).order_by('-total')

    # Calculate spending by category
    category_spending = user_transactions.filter(income_expense='Expense').values('category').annotate(
        total=Coalesce(Sum('amount', output_field=DecimalField()), 0, output_field=DecimalField())
    ).order_by('-total')

    # Prepare data for the chart
    categories = [item['category'] for item in category_spending]
    amounts = [float(item['total']) for item in category_spending]

    context = {
        'transactions': user_transactions,
        'username': request.user.username,
        'categories_json': json.dumps(categories, cls=DjangoJSONEncoder),
        'amounts_json': json.dumps(amounts, cls=DjangoJSONEncoder),
    }
    return render(request, 'dashboard.html', context)


def analytics(request):
    return render(request, 'analytics.html')


def insights(request):
    return render(request, 'ini-test.html')


# def payments(request):
#     return render(request, 'payments.html')


def logout(request):
    if request.method == 'GET':
        auth_logout(request)
        return render(request, 'registration/login.html')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password')
            )
            if user is not None:
                login(request, user)
                return redirect('finertia:dashboard')
        return render(request, 'registration/login.html', {'form': form})


def financial_form_view(request):
    if request.method == 'POST':
        form = FinancialForm(request.POST)
        if form.is_valid():
            form_data = form.cleaned_data
            stability, loan_eligibility, suggested_loan_amount, plan_text = classify_financial_status_and_suggest_plan(
                form_data)
            return render(request, 'result.html', {
                'stability': stability,
                'loan_eligibility': loan_eligibility,
                'suggested_loan_amount': suggested_loan_amount,
                'plan_text': plan_text
            })
    else:
        form = FinancialForm()
    return render(request, 'analytics.html', {'form': form})


def payments(request):
    transfer_form = TransferForm()
    bill_payment_form = BillPaymentForm()

    if request.method == 'POST':
        if 'transfer' in request.POST:
            transfer_form = TransferForm(request.POST)
            if transfer_form.is_valid():
                to_account = transfer_form.cleaned_data['to_account']
                amount = transfer_form.cleaned_data['amount']
                note = transfer_form.cleaned_data['note']

                transaction = AllTransactions.objects.create(
                    date=timezone.now(),
                    mode='Transfer',
                    category='Transfer',
                    subcategory='To Account',
                    note=note,
                    amount=amount,
                    income_expense='expense',
                    currency='CAD'
                )
                user_data = UserData.objects.get(user=request.user)
                user_data.transactions.add(transaction)
                return redirect('transfer_success')
        # elif 'bill_payment' in request.POST:
        #     bill_payment_form = BillPaymentForm(request.POST)
        #     if bill_payment_form.is_valid():
        #         bill_payment = bill_payment_form.save(commit=False)
        #         bill_payment.mode = 'Bill Payment'
        #         bill_payment.category = 'Bill'
        #         bill_payment.subcategory = 'Utility'
        #         bill_payment.income_expense = 'expense'
        #         bill_payment.save()
        #
        #         user_data = UserData.objects.get(user=request.user)
        #         user_data.transactions.add(bill_payment)
        #         return redirect('bill_payment_success')
        elif 'bill_payment' in request.POST:
            bill_payment_form = BillPaymentForm(request.POST)
            if bill_payment_form.is_valid():
                bill_payment = bill_payment_form.save(commit=False)
                bill_payment.mode = 'Bill Payment'
                bill_payment.category = 'Bill'
                bill_payment.income_expense = 'expense'
                bill_payment.save()

                user_data = UserData.objects.get(user=request.user)
                user_data.transactions.add(bill_payment)
                return redirect('bill_payment_success')

    return render(request, 'payments.html', {
        'transfer_form': transfer_form,
        'bill_payment_form': bill_payment_form,
    })


def transfer_success(request):
    return render(request, 'transfer_success.html')


def bill_payment_success(request):
    return render(request, 'bill_payment_success.html')
