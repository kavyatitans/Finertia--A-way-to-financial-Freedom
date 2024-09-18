from django.urls import path
from finertia import views
from .views import SignupView, LoginView, logout, home, dashboard, analytics, insights, payments, financial_form_view

app_name = 'finertia'

urlpatterns = [
    path('accounts/signup/', SignupView.as_view(), name='signup'),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', logout, name='logout'),
    path('', views.home, name='home'),
    path('dashboard', dashboard, name='dashboard'),
    path('analytics', financial_form_view, name='analytics'),
    path('insights', insights, name='insights'),
    path('payments', payments, name='payments'),
    path('forms', financial_form_view, name='financial_form_view'),
    path('transfer_success/', views.transfer_success, name='transfer_success'),
    path('bill_payment_success/', views.bill_payment_success, name='bill_payment_success'),

]
