from django.urls import path
from .views import Home, Login, Signup, Logout, Dashboard, Journal, TrialBalance, Ledger, Companies, Payables, Invoices

urlpatterns = [
    path('home', Home.as_view(), name='finance-home'),
    path('login', Login.as_view(), name='finance-login'),
    path('signup', Signup.as_view(), name='finance-signup'),
    path('logout', Logout.as_view(), name='finance-logout'),
    path('dashboard', Dashboard.as_view(), name='finance-dashboard' ),
    path('journal', Journal.as_view(), name='finance-journal' ),
    path('trial', TrialBalance.as_view(), name='finance-trial' ),
    path('ledger', Ledger.as_view(), name='finance-ledger' ),
    path('companies', Companies.as_view(), name='finance-companies' ),
    path('payables', Payables.as_view(), name='finance-payables' ),
    path('invoices', Invoices.as_view(), name='finance-invoices' ),
]