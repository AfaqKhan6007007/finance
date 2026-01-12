from django.urls import path
from .views import Login, Signup, Logout, Dashboard, Journal, TrialBalance, Ledger, Companies, Payables, Invoices, Receivables, InvoiceScan, Reports, CompanyCreate, CompanyEdit, CompanyDelete, Accounts,AccountCreate,AccountEdit, AccountDelete, InvoiceCreate, InvoiceEdit, InvoiceDelete, JournalCreate, JournalEdit, JournalDelete, Suppliers, SupplierCreate, SupplierEdit, SupplierDelete

urlpatterns = [
     # ============ Authentication ============
    path('login/', Login.as_view(), name='finance-login'),
    path('signup/', Signup.as_view(), name='finance-signup'),
    path('logout/', Logout.as_view(), name='finance-logout'),
    
    
     # ============ Account Management ============
    path('accounts/', Accounts.as_view(), name='finance-accounts'),
    path('accounts/add/', AccountCreate.as_view(), name='finance-account-create'),
    path('accounts/<int:pk>/edit/', AccountEdit.as_view(), name='finance-account-edit'),
    path('accounts/<int:pk>/delete/', AccountDelete.as_view(), name='finance-account-delete'),

    # ============ Supplier Management ============
    path('suppliers/', Suppliers.as_view(), name='finance-suppliers'),
    path('suppliers/new/', SupplierCreate.as_view(), name='finance-supplier-create'),
    path('suppliers/<int:pk>/edit/', SupplierEdit.as_view(), name='finance-supplier-edit'),
    path('suppliers/<int:pk>/delete/', SupplierDelete.as_view(), name='finance-supplier-delete'),
     
     
     # ============ Journal Entry Management ============
    path('journal/', Journal.as_view(), name='finance-journal'),
    path('journal/add/', JournalCreate.as_view(), name='finance-journal-create'),
    path('journal/<int:pk>/edit/', JournalEdit.as_view(), name='finance-journal-edit'),
    path('journal/<int:pk>/delete/', JournalDelete.as_view(), name='finance-journal-delete'),

    # ============ Main Pages ============
    path('dashboard/', Dashboard.as_view(), name='finance-dashboard'),
    path('trial/', TrialBalance.as_view(), name='finance-trial'),
    path('ledger/', Ledger.as_view(), name='finance-ledger'),
    path('reports/', Reports.as_view(), name='finance-reports'),
    path('scan/', InvoiceScan.as_view(), name='finance-scan'),
    
    # ============ Company/Account Management ============
    path('companies/', Companies.as_view(), name='finance-companies'),
    path('companies/add/', CompanyCreate.as_view(), name='finance-company-create'),
    path('companies/<int:pk>/edit/', CompanyEdit.as_view(), name='finance-company-edit'),
    path('companies/<int:pk>/delete/', CompanyDelete.as_view(), name='finance-company-delete'),
    
    # ============ Invoice Management ============
    path('invoices/', Invoices.as_view(), name='finance-invoices'),
    path('invoices/add/', InvoiceCreate.as_view(), name='finance-invoice-create'),
    path('invoices/<int:pk>/edit/', InvoiceEdit.as_view(), name='finance-invoice-edit'),
    path('invoices/<int:pk>/delete/', InvoiceDelete.as_view(), name='finance-invoice-delete'),

    # ============ Accounting Modules ============
    path('payables/', Payables.as_view(), name='finance-payables'),
    path('receivables/', Receivables.as_view(), name='finance-receivables'),
]