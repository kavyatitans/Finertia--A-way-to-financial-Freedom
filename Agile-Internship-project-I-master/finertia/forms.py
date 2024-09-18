# transactions/forms.py
from django import forms
# from .models import Account, BillPayment
from .models import AllTransactions, UserData, Card

from django.core.exceptions import ValidationError


# class TransferForm(forms.Form):
#     from_account = forms.ModelChoiceField(queryset=Account.objects.all())
#     to_account = forms.CharField(max_length=20)
#     amount = forms.DecimalField(max_digits=10, decimal_places=2)
#
#
# class BillPaymentForm(forms.ModelForm):
#     class Meta:
#         model = BillPayment
#         fields = ['account', 'biller', 'amount', 'due_date']


class FinancialForm(forms.Form):
    annual_income = forms.FloatField(label='Annual Income')
    birthday_count = forms.IntegerField(label='Birthday Count')
    employed_days = forms.IntegerField(label='Employed Days')
    mobile_phone = forms.BooleanField(label='Mobile Phone', required=False)
    work_phone = forms.BooleanField(label='Work Phone', required=False)
    phone = forms.BooleanField(label='Phone', required=False)
    email_id = forms.BooleanField(label='Email ID', required=False)
    family_members = forms.IntegerField(label='Family Members')
    total_amount = forms.FloatField(label='Total Amount')
    mean_amount = forms.FloatField(label='Mean Amount')
    std_amount = forms.FloatField(label='Std Amount')
    productive_ratio = forms.FloatField(label='Productive Ratio')
    gender_f = forms.BooleanField(label='Female', required=False)
    car_owner_y = forms.BooleanField(label='Car Owner', required=False)
    propert_owner_y = forms.BooleanField(label='Property Owner', required=False)
    type_income = forms.ChoiceField(label='Type of Income', choices=[
        ('Commercial associate', 'Commercial associate'),
        ('Pensioner', 'Pensioner'),
        ('State servant', 'State servant'),
        ('Student', 'Student')
    ])
    education = forms.ChoiceField(label='Education', choices=[
        ('Higher education', 'Higher education'),
        ('Incomplete higher', 'Incomplete higher'),
        ('Secondary / secondary special', 'Secondary / secondary special')
    ])
    marital_status = forms.ChoiceField(label='Marital Status', choices=[
        ('Married', 'Married'),
        ('Single / not married', 'Single / not married'),
        ('Widow / Widower', 'Widow / Widower')
    ])
    housing_type = forms.ChoiceField(label='Housing Type', choices=[
        ('House / apartment', 'House / apartment'),
        ('Municipal apartment', 'Municipal apartment'),
        ('Office apartment', 'Office apartment')
    ])
    type_occupation = forms.ChoiceField(label='Type of Occupation', choices=[
        ('Management', 'Management'),
        ('Laborers', 'Laborers'),
        ('Private service staff', 'Private service staff'),
        ('Sales staff', 'Sales staff')
    ])
    cibil_score = forms.IntegerField(label='CIBIL Score')
    bank_assets_value = forms.FloatField(label='Bank Assets Value')


class TransferForm(forms.Form):
    to_account = forms.CharField(max_length=100)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    note = forms.CharField(widget=forms.Textarea, required=False)


class BillPaymentForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['date', 'category', 'card_number', 'cvv_number', 'note', 'amount', 'currency']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

        def clean_card_number(self):
            card_number = self.cleaned_data['card_number']
            if not card_number.isdigit():
                raise ValidationError('Card number must be numeric.')
            return card_number

        def clean_cvv_number(self):
            cvv_number = self.cleaned_data['cvv_number']
            if not cvv_number.isdigit():
                raise ValidationError('CVV number must be numeric.')
            return cvv_number
