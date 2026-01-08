from django.urls import path
from .views import Home, Login, Signup, Logout, Dashboard, Journal, TrialBalance, Ledger, Companies, Payables, Invoices, Receivables, InvoiceScan, Reports, CompanyCreate, CompanyEdit, CompanyDelete

urlpatterns = [
     # ============ Authentication ============
    path('login/', Login.as_view(), name='finance-login'),
    path('signup/', Signup.as_view(), name='finance-signup'),
    path('logout/', Logout.as_view(), name='finance-logout'),
    
    # ============ Main Pages ============
    path('home/', Home.as_view(), name='finance-home'),
    path('dashboard/', Dashboard.as_view(), name='finance-dashboard'),
    path('journal/', Journal.as_view(), name='finance-journal'),
    path('trial/', TrialBalance.as_view(), name='finance-trial'),
    path('ledger/', Ledger.as_view(), name='finance-ledger'),
    path('reports/', Reports.as_view(), name='finance-reports'),
    path('scan/', InvoiceScan.as_view(), name='finance-scan'),
    
    # ============ Company/Account Management ============
    path('companies/', Companies.as_view(), name='finance-companies'),
    path('companies/add/', CompanyCreate.as_view(), name='finance-company-create'),
    path('companies/<int:pk>/edit/', CompanyEdit.as_view(), name='finance-company-edit'),
    path('companies/<int:pk>/delete/', CompanyDelete.as_view(), name='finance-company-delete'),
    
    # ============ Accounting Modules ============
    path('payables/', Payables.as_view(), name='finance-payables'),
    path('invoices/', Invoices.as_view(), name='finance-invoices'),
    path('receivables/', Receivables.as_view(), name='finance-receivables'),
]